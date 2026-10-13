"""Replay frozen launch-trading, claim cash and USD accounting offline."""
import argparse, json, os, pathlib, shutil, subprocess, sys
CODE = pathlib.Path(__file__).resolve().parents[1]
CASE = pathlib.Path('outputs/ramonos-launches-20261013')
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',type=pathlib.Path,default=CODE)
    ap.add_argument('--out',type=pathlib.Path,required=True)
    a=ap.parse_args(); source=a.source.resolve(); out=a.out.resolve()
    if out==source or source in out.parents or out in source.parents:
        ap.error('Output must be outside input repository')
    if out.exists() and any(out.iterdir()): ap.error('Output must be new or empty')
    if not (source/CASE/'costs-coverage/raw/failed-page-0020.json').exists():
        ap.error('Extract the profit evidence release into the source repository first')
    out.mkdir(parents=True,exist_ok=True);shutil.copytree(source/CASE,out/CASE)
    env={**os.environ,'RAMONOS_RESEARCH_ROOT':str(out),'RAMONOS_CODE_ROOT':str(CODE),
         'RAMONOS_ALLOW_NETWORK':'0','PYTHONDONTWRITEBYTECODE':'1'}
    base=str(CASE); usd=base+'/usd-valuation'
    commands=[['trading/build.py'],['trading/report.py'],['trading/verify.py'],
      ['costs-coverage/analyze.py'],['costs-coverage/claim_cash.py'],
      ['usd-valuation/value_receipts.py','--receipts',base+'/own-fees/receipts.csv','--output',usd,'--offline'],
      ['usd-valuation/value_trading_cashflows.py','--ledger',base+'/trading/capital-ledger.json',
       '--failed-fees',base+'/costs-coverage/failed-cohort-fees.csv',
       '--claim-network-fees',usd+'/additional-claim-network-fees.csv','--output',usd,'--offline'],
      ['usd-valuation/value_claim_account_cash.py','--claims',base+'/costs-coverage/claim-native-wsol-cash.csv','--output',usd,'--offline']]
    done=[]
    for command in commands:
        r=subprocess.run([sys.executable,str(CODE/'tools'/command[0]),*command[1:]],cwd=out,env=env,capture_output=True,text=True)
        (out/(command[0].replace('/','-')+'.log')).write_text(r.stdout+'\n'+r.stderr)
        if r.returncode: raise RuntimeError('Replay failed: '+command[0]+'; see scratch log')
        done.append(command[0])
    expected=json.loads((source/CASE/'usd-valuation/combined-account-cash-summary-usd.json').read_text())
    actual=json.loads((out/CASE/'usd-valuation/combined-account-cash-summary-usd.json').read_text())
    for key in ['metrics','standaloneClaimCashSol','standaloneClaimCashHistoricalUsd','frozenCurrentSolUsd','includedStandaloneTransactions','excludedTradeOverlapTransactions']:
        if expected[key]!=actual[key]: raise AssertionError('Frozen comparison mismatch: '+key)
    receipt={'offline':True,'completedScripts':done,'metrics':actual['metrics'],'financialExecutionCapLamports':'0'}
    (out/'profit-replay-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
