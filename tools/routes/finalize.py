import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import json,pathlib,hashlib,datetime,csv,collections
root=ROOT;out=root/'outputs/ramonos-launches-20261013/routes';rows=json.loads((out/'routes.json').read_text());summary=json.loads((out/'summary.json').read_text());accounts=json.loads((out/'decoded-accounts.json').read_text());by={a['address']:a for a in accounts};checks=json.loads((out/'validation.json').read_text())
for r in rows:
 checks.append({'mint':r['mint'],'check':'derived curve agrees signed historical CreateEvent binding','passed':r['createEvent']['event']['bonding_curve']==r['curve']})
for p in out.glob('raw/*.response.json'):
 req=json.loads(p.with_name(p.name.replace('.response.json','.request.json')).read_text());resp=json.loads(p.read_text());checks.append({'check':'captured response count equals exact request and finalized','source':str(p.relative_to(root)),'passed':len(req['params'][0])<=100 and len(req['params'][0])==len(resp['result']['value']) and req['params'][1]['commitment']=='finalized'})
summary['failedChecks']=[c for c in checks if not c['passed']];summary['activeConfigAdminRevocationCounts']=dict(collections.Counter(str(r['adminRevoked']) for r in rows if r['configActive']));summary['activeHolderFlagUnknownCount']=sum(r['activeHolderReward'] is None for r in rows);summary['idlHead']='639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22';summary['censusCutoffUtc']='2026-10-13T16:19:01Z';summary['nativeDonationRecipients']=[a for a in accounts if a.get('type')=='DonationFeePda'];summary['uniqueCurrentVaultCustodyCount']=len({(v['vault'],v['quote']) for r in rows for v in r['custody']})
for n,v in [('validation.json',checks),('summary.json',summary)]: (out/n).write_text(json.dumps(v,indent=2))
report='''# Ramonos current fee routes

All 279 verified launches are covered: 277 Pump accounts were snapshotted; the two Raydium LaunchLab launches are explicitly delegated to the separate LaunchLab analysis. These are current finalized routes, not historical creation defaults.

| Current Pump route | Launches |
|---|---:|
| Ordinary creator wallet (the disclosed Ramonos wallet) | 258 |
| Native sharing to ordinary wallets | 13 |
| Native donation sharing | 1 |
| Native GitHub social sharing | 2 |
| Native holder rewards | 3 |

The two GitHub routes are Flightradar24 (`4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump`) → numeric ID 12810712, and Bold (`EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM`) → UsePaid numeric ID 322216527. Each has an active 100% split. No other social platform appears. Flightradar24's beneficiary lifetime native claim counter is zero; its current above-rent balance is 0.011355366 SOL. Its config creator vault holds 0.135504354 SOL above rent, independently of the curve's zero pending creator-fee counter. Bold's config vault holds 0.001169962 SOL above rent. Both have absent canonical pools and zero observed quote token custody.

UsePaid's native lifetime claim counter is 52,313.813492020 SOL across all its mints and its stable lifetime raw counter is 19,555,437,862,363. Neither is Ramonos-attributable. Its last claim timestamp, 2026-10-13T16:20:52Z, is after the historical census cutoff; no onward settlement is established.

Diamond Hands (`HJE2DEZXvErwUabTU16xzrS629qXVeVyTGvJYJVfpump`), Pussy Up, Money Printer (`wvbhVMz7iknR8DqYEccWfJqdGRWSwzTwnk7cJePpump`), and Peccy (`CKAwvahwXueRcid9F4FZkbinyzp1F2c1wPnQ2QnRpump`) have authoritative current holder-reward flags true. The first two are complete and use valid bound PumpAMM pools; Peccy remains on its curve. Five active route holder flags are absent in legacy account layouts and remain null. They have the ordinary Ramonos creator identity; null has not been changed into false.

All 16 sharing configurations currently match the authoritative active curve/pool creator; nine have admin revoked and seven do not. TRANSEXUAL COIN's recipient is a verified native DonationFeePda, not an ordinary wallet. Native fee account type, account owner and recorded mint distinguish it.

The account capture ran 2026-10-13 16:22:04–16:22:38 UTC at finalized slots 456505923–456506077. Census cutoff is 16:19:01 UTC. This is a multi-slot snapshot. Official pinned IDLs at `639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22` exactly match installed SDK 4.0.0 route-account schemas. Raw IDLs, requests, responses, hashes, rent parameters, owners, discriminators, PDA derivations, mint and quote bindings are retained. All recorded validation checks pass.

`routes.json` / `routes.csv` contain each launch, active route, share basis points and separate counter allocations. Fractions are applied with integer floor to each available pending fee counter, not to an invented combined total. Missing counters remain null. `social-beneficiaries.json` / `beneficiaries.csv` retain pooled lifetime counters and current custody. Vault above-rent or token balances may contain arbitrary funding and are custody, not proven fee revenue. Ordinary creator vaults span many mints: deduplicate address/quote before any sum. No historical fees, direct claims or global revenue total is inferred from this snapshot. No economic effects were performed.
'''
(out/'REPORT.md').write_text(report)
manifest={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json']};(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('checks',len(checks),'failed',len(summary['failedChecks']))
