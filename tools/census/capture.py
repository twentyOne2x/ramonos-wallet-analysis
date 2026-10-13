import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import importlib.util,pathlib,json,datetime,hashlib,time
OUT=ROOT/'outputs/ramonos-launches-20261013/census';RAW=OUT/'raw'
W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
R=mod('rpc_read', CODE_ROOT/'tools/rpc_readonly.py')
D=mod('dec',CODE_ROOT/'tools/fee_core.py')
def utc(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat().replace('+00:00','Z')
def query(label,method,params):
 p=RAW/(label+'.json')
 if p.exists():return json.loads(p.read_text())
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();b=R.rpc(method,params);p.write_text(json.dumps(b,separators=(',',':')))
 p.with_suffix('.request.json').write_text(json.dumps({'method':method,'params':params,'startedUtc':start,'completedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'endpoint':'configured read-only mainnet provider; credential omitted','economicCapLamports':'0'},indent=2));return b
config=OUT/'config.json'
if config.exists():cut=json.loads(config.read_text())['cutoff']
else:
 cut=int(time.time());config.write_text(json.dumps({'wallet':W,'cutoff':cut,'cutoffUtc':utc(cut),'commitment':'finalized','capLamports':'0'},indent=2))
pages=[];cursor=None;seen=set();i=0
while True:
 opts={'transactionDetails':'full','encoding':'jsonParsed','sortOrder':'asc','limit':1000,'maxSupportedTransactionVersion':1,'commitment':'finalized','filters':{'status':'succeeded','tokenAccounts':'none','blockTime':{'gte':0,'lt':cut}}}
 if cursor:opts['paginationToken']=cursor
 b=query(f'page-{i:04d}','getTransactionsForAddress',[W,opts]);r=b['result'];rows=r['data'];nxt=r.get('paginationToken');ts=[x['blockTime'] for x in rows if x.get('blockTime') is not None]
 pages.append({'path':f'outputs/ramonos-launches-20261013/census/raw/page-{i:04d}.json','count':len(rows),'cursorIn':cursor,'cursorOut':nxt,'firstUtc':utc(min(ts)) if ts else None,'lastUtc':utc(max(ts)) if ts else None,'sha256':hashlib.sha256((RAW/f'page-{i:04d}.json').read_bytes()).hexdigest()})
 (OUT/'history-manifest.json').write_text(json.dumps({'wallet':W,'cutoff':cut,'cutoffUtc':utc(cut),'status':'succeeded','tokenAccounts':'none','commitment':'finalized','pages':pages,'terminal':not bool(nxt),'transactionCount':sum(x['count'] for x in pages),'coverage':'terminal provider-indexed direct-wallet references' if not nxt else 'partial'},indent=2))
 creates=[];inits=[];errs=[]
 for tx in rows:
  keys=tx['transaction']['message']['accountKeys'];signers=[D.key(k) for k in keys if isinstance(k,dict) and k.get('signer')];sig=tx['transaction']['signatures'][0]
  for e in D.events(tx,pages[-1]['path'],errs):
   if e['name']=='CreateEvent':creates.append({**e,'walletSigned':W in signers,'signers':signers})
  for ix in D.D.flatten_instructions(tx):
   parsed=ix.get('parsed',{})
   if isinstance(parsed,dict) and parsed.get('type') in ('initializeMint','initializeMint2'):
    inits.append({'signature':sig,'slot':tx['slot'],'blockTime':tx.get('blockTime'),'utc':utc(tx['blockTime']),'walletSigned':W in signers,'signers':signers,'info':parsed.get('info'),'tokenProgram':ix['programId'],'parentProgram':ix.get('parentProgram'),'rawSource':pages[-1]['path'],'topLevelInstructionIndex':ix['topLevelInstructionIndex'],'innerInstructionIndex':ix['innerInstructionIndex']})
 (OUT/f'decoded-page-{i:04d}.json').write_text(json.dumps({'creates':creates,'mintInitializations':inits,'errors':errs},indent=2))
 print(json.dumps({'page':i,'count':len(rows),'firstUtc':pages[-1]['firstUtc'],'lastUtc':pages[-1]['lastUtc'],'creates':len(creates),'initializations':len(inits),'terminal':not bool(nxt),'earliestCreates':creates[:2]}),flush=True)
 if not nxt:break
 if not rows or nxt in seen:raise RuntimeError('pagination did not advance')
 seen.add(nxt);cursor=nxt;i+=1
