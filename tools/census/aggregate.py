import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,collections,datetime,csv
P=(ROOT/'outputs/ramonos-launches-20261013/census');W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b';c=[];ini=[];errors=[]
for f in sorted(P.glob('decoded-page-*.json')):
 b=json.loads(f.read_text());c+=b['creates'];ini+=b['mintInitializations'];errors+=b['errors']
ix={(x['signature'],x['info']['mint']):x for x in ini};launches=[];excluded=[]
for e in c:
 mint=e['event']['mint'];init=ix.get((e['signature'],mint))
 if not e['walletSigned'] or e['event']['user']!=W or init is None:
  excluded.append({'reason':'wallet not signed deployer or no matched mint initialization','creation':e});continue
 v=e['event'];launches.append({'mint':mint,'name':v['name'],'symbol':v['symbol'],'uri':v['uri'],'platform':'Pump','program':e['program'],'signature':e['signature'],'slot':e['slot'],'blockTime':e['blockTime'],'utc':e['utc'],'deployer':v['user'],'initialCreator':v.get('creator'),'signers':e['signers'],'initialCreatorFeeBps':v.get('creator_fee_bps'),'initialHolderReward':v.get('is_holder_reward'),'initialCashbackEnabled':v.get('is_cashback_enabled'),'initialQuoteMint':v.get('quote_mint'),'historicalMissingFields':e['missingTrailingFields'],'rawSource':e['rawSource'],'transactionUrl':e['transactionUrl'],'createEvent':e,'mintInitialization':init})
matched={(e['signature'],e['event']['mint']) for e in c}
for x in ini:
 if (x['signature'],x['info']['mint']) in matched:continue
 if not x['walletSigned']:excluded.append({'reason':'wallet did not sign mint initialization','initialization':x});continue
 launches.append({'mint':x['info']['mint'],'name':None,'symbol':None,'uri':None,'platform':'Raydium LaunchLab' if x['parentProgram']=='LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj' else 'unknown mint initialization','program':x['parentProgram'],'signature':x['signature'],'slot':x['slot'],'blockTime':x['blockTime'],'utc':x['utc'],'deployer':W,'initialCreator':None,'signers':x['signers'],'rawSource':x['rawSource'],'transactionUrl':'https://solscan.io/tx/'+x['signature'],'mintInitialization':x})
launches.sort(key=lambda x:(x['slot'],x['signature'],x['mint']))
(P/'launches.json').write_text(json.dumps(launches,indent=2));(P/'excluded.json').write_text(json.dumps(excluded,indent=2));(P/'decode-errors.json').write_text(json.dumps(errors,indent=2))
daily=collections.Counter(x['utc'][:10] for x in launches);weekly=collections.Counter(datetime.datetime.fromtimestamp(x['blockTime'],datetime.timezone.utc).date().strftime('%G-W%V') for x in launches)
s={'launchCount':len(launches),'distinctMints':len({x['mint'] for x in launches}),'platformCounts':dict(collections.Counter(x['platform'] for x in launches)),'first':launches[0],'last':launches[-1],'excludedCreationCount':len(excluded),'decodeErrors':errors,'daily':dict(sorted(daily.items())),'weekly':dict(sorted(weekly.items())),'initialCreatorCounts':dict(collections.Counter(str(x.get('initialCreator')) for x in launches)),'initialHolderRewardCounts':dict(collections.Counter(str(x.get('initialHolderReward')) for x in launches))}
(P/'summary.json').write_text(json.dumps(s,indent=2))
fields=['utc','name','symbol','mint','platform','deployer','initialCreator','initialCreatorFeeBps','initialHolderReward','initialCashbackEnabled','initialQuoteMint','signature','transactionUrl','rawSource']
with (P/'launches.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(launches)
print(json.dumps({k:v for k,v in s.items() if k not in ['first','last','daily','weekly']},indent=2));print('first',launches[0]['utc'],launches[0]['mint']);print('last',launches[-1]['utc'],launches[-1]['mint'])
