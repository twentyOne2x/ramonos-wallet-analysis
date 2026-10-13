import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import sys,pathlib,json,collections,hashlib
sys.path.insert(0,str(CODE_ROOT/'tools'));import fee_core as C
OUT=ROOT/'outputs/ramonos-launches-20261013/own-fees';W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
for name in ['pump','pump_amm','pump_fees']:
 j=json.loads((CODE_ROOT/f'schemas/{name}.json').read_text());C.IDLS[j['address']]=j;C.TYPES[j['address']]={t['name']:t['type'] for t in j['types']}
C.NAMES={'CollectCreatorFeeEvent','CollectCoinCreatorFeeEvent','DistributeCreatorFeesEvent'};C.TAGS={bytes(e['discriminator']):(p,e['name']) for p,j in C.IDLS.items() for e in j['events'] if e['name'] in C.NAMES}
manifest=json.loads((ROOT/'outputs/ramonos-launches-20261013/census/history-manifest.json').read_text());events=[];txs={};errors=[]
for page in manifest['pages']:
 p=ROOT/page['path']; assert C.sha(p)==page['sha256'];rows=json.loads(p.read_text())['result']['data']
 for tx in rows:
  es=C.events(tx,page['path'],errors)
  if not es:continue
  own=[e for e in es if (e['event'].get('creator')==W or e['event'].get('coin_creator')==W or any(sh['address']==W for sh in e['event'].get('shareholders',[])))]
  if own:
   events+=own;txs[tx['transaction']['signatures'][0]]=tx
 print(page['path'],len(events),flush=True)
(OUT/'events.json').write_text(json.dumps(events,indent=2));(OUT/'transactions.json').write_text(json.dumps(txs));(OUT/'decode-errors.json').write_text(json.dumps(errors,indent=2))
print('SUMMARY',dict(collections.Counter(e['name'] for e in events)),flush=True)
for name in C.NAMES:
 es=[e for e in events if e['name']==name];print(name,sum(int(e['event'].get('creator_fee',e['event'].get('coin_creator_fee',e['event'].get('distributed',0)))) for e in es))
