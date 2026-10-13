"""Read-only Pump receipt/account decoder with exact integer quantities."""
import base64,datetime,hashlib,importlib.util,json,pathlib,re,os
from paths import ROOT, CODE_ROOT
OUT=ROOT/'outputs/ramonos-launches-20261013/core'; RAW=OUT/'raw'
CUT='2026-10-13T16:19:01Z'; END=int(datetime.datetime.fromisoformat(CUT.replace('Z','+00:00')).timestamp())
WSOL='So11111111111111111111111111111111111111112'; SOL='11111111111111111111111111111111'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
D=module('retained_decoder',CODE_ROOT/'tools/decoder.py')
IDLS={j['address']:j for j in [D.IDL,D.FEE_IDL,D.AMM_IDL]}; TYPES={p:{t['name']:t['type'] for t in j['types']} for p,j in IDLS.items()}
NAMES={'CreateEvent','TradeEvent','BuyEvent','SellEvent','CollectCreatorFeeEvent','CollectCoinCreatorFeeEvent','DistributeCreatorFeesEvent','DistributeFeeToHoldersEvent','SocialFeePdaClaimed','SocialFeePdaCreated','UpdateFeeSharesEvent','CreateFeeSharingConfigEvent','ResetFeeSharingConfigEvent','SetCreatorEvent','MigrateBondingCurveCreatorEvent','MigratePoolCoinCreatorEvent','SweepBondingCurveFeeEvent','SweepPoolFeeEvent','SetMetaplexCreatorEvent','SetBondingCurveCoinCreatorEvent','SetMetaplexCoinCreatorEvent','DonationFeePdaCreated','DonationFeePdaCranked'}
TAGS={bytes(e['discriminator']):(p,e['name']) for p,j in IDLS.items() for e in j['events'] if e['name'] in NAMES}
class Reader(D.Reader):
 def value(self,t):
  if isinstance(t,dict) and 'array' in t:return [self.value(t['array'][0]) for _ in range(t['array'][1])]
  return super().value(t)
def utc(t):return datetime.datetime.fromtimestamp(t,datetime.timezone.utc).isoformat().replace('+00:00','Z')
def key(a):return a['pubkey'] if isinstance(a,dict) else a
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def body(p):return json.loads((ROOT/p).read_text())
def rows(p):
 b=body(p);b=b.get('response',b);r=b.get('result',{});return r.get('data',[]) if isinstance(r,dict) else []
def events(tx,source,errors=None):
 if tx['meta']['err'] is not None:return []
 errors=errors if errors is not None else [];payloads=[];seen=set();stack=[]
 for i,l in enumerate(tx['meta'].get('logMessages',[])):
  m=re.fullmatch(r'Program (\w+) invoke \[\d+\]',l)
  if m:stack.append(m[1]);continue
  if re.match(r'Program \w+ (success|failed:)',l):
   if stack:stack.pop()
   continue
  if l.startswith('Program data: ') and stack and stack[-1] in IDLS:
   raw=base64.b64decode(l[14:]);tag=TAGS.get(raw[:8])
   if tag and tag[0]==stack[-1]:payloads.append((raw,{'logIndex':i,'evidence':'program_log'}));seen.add(raw)
 for ix in D.flatten_instructions(tx):
  if ix['programId'] not in IDLS or not ix.get('data'):continue
  r=D.unb58(ix['data'])
  if r[:8]==D.EVENT_CPI_TAG and r[8:16] in TAGS and r[8:] not in seen:
   payloads.append((r[8:],{'evidence':'event_cpi','topLevelInstructionIndex':ix['topLevelInstructionIndex'],'innerInstructionIndex':ix['innerInstructionIndex']}));seen.add(r[8:])
 es=[]
 for raw,loc in payloads:
  p,n=TAGS[raw[:8]];r=Reader(raw,TYPES[p]);v={};missing=[];fields=TYPES[p][n]['fields']
  try:
   for i,f in enumerate(fields):
    try:v[f['name']]=r.value(f['type'])
    except EOFError:missing=[q['name'] for q in fields[i:]];break
   es.append({'signature':tx['transaction']['signatures'][0],'slot':tx['slot'],'transactionIndex':tx.get('transactionIndex'),'blockTime':tx['blockTime'],'utc':utc(tx['blockTime']),'name':n,'program':p,'event':v,'rawSource':str(source),'missingTrailingFields':missing,'unparsedBytes':len(raw)-r.position,'payloadSha256':hashlib.sha256(raw).hexdigest(),'transactionUrl':'https://solscan.io/tx/'+tx['transaction']['signatures'][0],**loc})
  except Exception as e:errors.append({'signature':tx['transaction']['signatures'][0],'name':n,'rawSource':str(source),'error':type(e).__name__,'detail':str(e)})
 return es
IXS={p:{bytes(i['discriminator']):i for i in j['instructions']} for p,j in IDLS.items()}
def instructions(tx,source):
 rs=[]
 for ix in D.flatten_instructions(tx):
  if ix['programId'] not in IDLS or not ix.get('data'):continue
  raw=D.unb58(ix['data']);schema=IXS[ix['programId']].get(raw[:8]);
  if not schema or not any(x in schema['name'] for x in ['sharing','shares','creator','social','donation']):continue
  r=Reader(raw,TYPES[ix['programId']]);args={f['name']:r.value(f['type']) for f in schema['args']}
  rs.append({'signature':tx['transaction']['signatures'][0],'slot':tx['slot'],'transactionIndex':tx.get('transactionIndex'),'blockTime':tx['blockTime'],'utc':utc(tx['blockTime']),'name':schema['name'],'program':ix['programId'],'accounts':{f['name']:key(a) for f,a in zip(schema['accounts'],ix.get('accounts',[]))},'args':args,'successful':tx['meta']['err'] is None,'signers':[key(a) for a in tx['transaction']['message']['accountKeys'] if isinstance(a,dict) and a.get('signer')],'rawSource':str(source),'topLevelInstructionIndex':ix['topLevelInstructionIndex'],'innerInstructionIndex':ix['innerInstructionIndex'],'transactionUrl':'https://solscan.io/tx/'+tx['transaction']['signatures'][0]})
 return rs
def decode_account(a,v,source,slot=None):
 if not v:return {'address':a,'exists':False,'rawSource':str(source),'slot':slot}
 p=v['owner'];raw=base64.b64decode(v['data'][0]);name=next((x['name'] for x in IDLS.get(p,{}).get('accounts',[]) if bytes(x['discriminator'])==raw[:8]),None);out={'address':a,'exists':True,'owner':p,'lamports':str(v['lamports']),'dataLength':len(raw),'rawSource':str(source),'slot':slot,'type':name,'dataSha256':hashlib.sha256(raw).hexdigest()}
 if name:
  r=Reader(raw,TYPES[p]);vals={};missing=[]
  for f in TYPES[p][name]['fields']:
   if f['name']=='_reserved':break
   try:vals[f['name']]=r.value(f['type'])
   except EOFError:missing.append(f['name']);break
  out.update(decoded=vals,missingTrailingFields=missing)
 return out
def query(label,method,params):
 p=RAW/(label+'.json');p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():return json.loads(p.read_text())
 rpc=module('readonly_provider',CODE_ROOT/'tools/rpc_readonly.py')
 started=datetime.datetime.now(datetime.timezone.utc).isoformat();res=rpc.rpc(method,params);p.write_text(json.dumps(res,separators=(',',':')))
 p.with_suffix('.request.json').write_text(json.dumps({'method':method,'params':params,'startedUtc':started,'completedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':sha(p),'endpoint':'configured Helius mainnet read-only RPC; credential omitted'},indent=2));return res
def history(label,address,lower=0,upper=END):
 pages=[];cursor=None;seen=set();i=0
 while True:
  opts={'transactionDetails':'full','encoding':'jsonParsed','sortOrder':'asc','limit':1000,'maxSupportedTransactionVersion':1,'commitment':'finalized','filters':{'status':'succeeded','tokenAccounts':'none','blockTime':{'gte':lower,'lt':upper}}}
  if cursor:opts['paginationToken']=cursor
  labelp=f'{label}/page-{i:04d}';res=query(labelp,'getTransactionsForAddress',[address,opts])['result'];rr=res['data'];nxt=res.get('paginationToken');times=[t['blockTime'] for t in rr]
  pages.append({'path':str((RAW/(labelp+'.json')).relative_to(ROOT)),'count':len(rr),'cursorIn':cursor,'cursorOut':nxt,'sha256':sha(RAW/(labelp+'.json')),'minBlockTime':min(times) if times else None,'maxBlockTime':max(times) if times else None})
  report={'address':address,'windowStart':lower,'windowEndExclusive':upper,'fixedCutoffUtc':CUT,'tokenAccounts':'none','statusFilter':'succeeded','pages':pages,'terminal':not bool(nxt),'transactionCount':sum(p['count'] for p in pages),'coverage':'terminal provider pagination for exact fixed time window' if not nxt else 'partial'};(RAW/label/'coverage.json').write_text(json.dumps(report,indent=2))
  if not nxt:return report
  if not rr or nxt in seen:raise RuntimeError('Non-advancing history pagination')
  seen.add(nxt);cursor=nxt;i+=1
