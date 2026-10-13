"""Recompute retained case in a separate workspace; never alter input evidence."""
import argparse, json, os, pathlib, shutil, subprocess, sys

CODE_ROOT = pathlib.Path(__file__).resolve().parents[1]
CASE = pathlib.Path('outputs/ramonos-launches-20261013')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=pathlib.Path, default=CODE_ROOT,
                        help='Repository root containing extracted outputs/')
    parser.add_argument('--out', type=pathlib.Path, required=True,
                        help='New, empty scratch workspace; input remains untouched')
    parser.add_argument('--full', action='store_true', help='Also replay routing and target vaults')
    args = parser.parse_args()
    source, dest = args.source.resolve(), args.out.resolve()
    if dest == source or source in dest.parents or dest in source.parents:
        parser.error('Output must be outside the input repository tree')
    if dest.exists() and any(dest.iterdir()):
        parser.error('Output must be empty to avoid overwriting evidence')
    if not (source/CASE/'census/history-manifest.json').is_file():
        parser.error('Extract the raw evidence release into the source root first')
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source/CASE, dest/CASE)
    env = {**os.environ, 'RAMONOS_RESEARCH_ROOT': str(dest),
           'RAMONOS_ALLOW_NETWORK': '0', 'PYTHONDONTWRITEBYTECODE': '1'}
    commands = [('census/verify.py',), ('own-fees/decode.py',),
                ('own-fees/verify.py',), ('own-fees/report.py',)]
    if args.full:
        commands += [('launchlab/analyze.py',), ('launchlab/claims.py',),
                     ('launchlab/report.py',), ('target-fees/replay.py',),
                     ('target-vaults/replay.py',), ('target-vaults/amm_replay.py', '--latest'),
                     ('routes/snapshot.py', str(CASE/'census/launches.json')),
                     ('routes/finalize.py',)]
    completed = []
    for command in commands:
        result = subprocess.run([sys.executable, str(CODE_ROOT/'tools'/command[0]),
                                 *command[1:]], cwd=dest, env=env,
                                capture_output=True, text=True)
        (dest/(command[0].replace('/','-')+'.log')).write_text(result.stdout+'\n'+result.stderr)
        if result.returncode:
            raise RuntimeError('Replay failed: '+command[0]+'; inspect its scratch log')
        completed.append(command[0])
    actual = json.loads((dest/CASE/'own-fees/summary.json').read_text())
    frozen = json.loads((source/CASE/'own-fees/summary.json').read_text())
    comparisons = ['totalVerifiedPaidLamports', 'eventCount', 'transactionCount',
                   'excludedOtherQuoteReceipts', 'failedReceipts', 'cashLedgerFailedSignatures']
    for key in comparisons:
        if actual[key] != frozen[key]:
            raise AssertionError('Frozen own-fee result mismatch: '+key)
    if actual['totalVerifiedPaidLamports'] != '1660286830500':
        raise AssertionError('Retained Ramonos receipt total mismatch')
    evidence = {'offline': True, 'sourceUntouched': True,
                'completedScripts': completed, 'comparedFrozenFields': comparisons,
                'totalVerifiedPaidLamports': actual['totalVerifiedPaidLamports'],
                'otherQuoteReceiptsExcluded': len(actual['excludedOtherQuoteReceipts'])}
    (dest/'replay-validation.json').write_text(json.dumps(evidence, indent=2)+'\n')
    print(json.dumps(evidence, indent=2))

if __name__ == '__main__':
    main()
