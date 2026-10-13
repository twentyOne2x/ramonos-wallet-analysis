import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,importlib.util,datetime,hashlib,collections,sys
sys.dont_write_bytecode=True
OUT=ROOT/'outputs/ramonos-launches-20261013/target-vaults';RAW=OUT/'raw'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
C=module('vault_fee_core',CODE_ROOT/'tools/fee_core.py');RPC=module('vault_readonly',CODE_ROOT/'tools/rpc_readonly.py')
SDK=CODE_ROOT/'schemas'
for n in ['pump','pump_amm','pump_fees']:
 j=json.loads((SDK/f'{n}.json').read_text());C.IDLS[j['address']]=j;C.TYPES[j['address']]={t['name']:t['type']for t in j['types']}
C.TAGS={bytes(e['discriminator']):(p,e['name'])for p,j in C.IDLS.items()for e in j['events']if e['name']in C.NAMES};C.IXS={p:{bytes(i['discriminator']):i for i in j['instructions']}for p,j in C.IDLS.items()}
TARGETS=[dict(name='Flightradar24',mint='4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump',config='7hrJLX3oga1GBmvtcQmyfDujNcmBF5vTComScdSmXfhu',vault='6wZi4ba9SpzmUDPpbQeozX53NwkwD3awq8ErYj3GkJRk',recipient='qNG5wnFQWzDHm1zGTMnqddwGp861LK7srHv3prtn1Dv'),dict(name='Bold',mint='EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM',config='GFpZ79XaLk6kqU448eTykVZGGqec6aLveepdy3EZBbYj',vault='98AhHzY5K9Xb7iixLipcjWWYo1Ksrk3nrBKv2zmkkBrj',recipient='FfLpuH4WPn2MR8Lqn1MpwQc1HtAPPqL3qvMWZjnFHGpv')]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
cfgp=OUT/'config.json'
if cfgp.exists():cfg=json.loads(cfgp.read_text())
else:
 cutoff=int(datetime.datetime.now(datetime.timezone.utc).timestamp());cfg={'cutoff':cutoff,'cutoffUtc':C.utc(cutoff),'commitment':'finalized','financialExecutionCapSol':0};save(cfgp,cfg)
def query(label,method,params):
 p=RAW/(label+'.response.json');q=RAW/(label+'.request.json');p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert json.loads(q.read_text())['params']==params;return json.loads(p.read_text())
 start=now();r=RPC.rpc(method,params);p.write_text(json.dumps(r,separators=(',',':')));save(q,{'method':method,'params':params,'startedUtc':start,'completedUtc':now(),'responseSha256':C.sha(p),'endpoint':'configured mainnet read-only provider; credentials omitted'});return r
routes=json.loads((ROOT/'outputs/ramonos-launches-20261013/routes/routes.json').read_text());seed='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
for r in routes:
 if r['configActive']and r['routeCategory']in('ordinary wallet sharing','native donation sharing')and any(x['address']!=seed for x in r['shareholders']):
  TARGETS.append(dict(name='route-'+r['mint'],displayName=r['name'],mint=r['mint'],config=r['sharingConfig'],vault=r['cfgVault'],recipients=r['shareholders'],routeCategory=r['routeCategory']))
summaries=[]
for target in TARGETS:
 name=target['name'];vault=target['vault'];cursor=None;seen=set();txs={};pages=[];page=0
 while True:
  opts={'transactionDetails':'full','encoding':'jsonParsed','sortOrder':'asc','limit':1000,'maxSupportedTransactionVersion':1,'commitment':'finalized','filters':{'status':'succeeded','tokenAccounts':'none','blockTime':{'gte':0,'lt':cfg['cutoff']}}}
  if cursor:opts['paginationToken']=cursor
  label=f'{name}/page-{page:04d}';r=query(label,'getTransactionsForAddress',[vault,opts])['result'];batch=r['data'];nxt=r.get('paginationToken');source=str((RAW/(label+'.response.json')).relative_to(ROOT))
  for tx in batch:
   sig=tx['transaction']['signatures'][0];assert sig not in txs;txs[sig]=(tx,source)
  pages.append({'path':source,'sha256':C.sha(ROOT/source),'count':len(batch),'cursorIn':cursor,'cursorOut':nxt});save(OUT/name/'coverage.json',{**cfg,**target,'terminal':not bool(nxt),'pages':pages,'transactionCount':len(txs)})
  if not nxt:break
  assert batch and nxt not in seen;seen.add(nxt);cursor=nxt;page+=1
 errors=[];rows=[];fee_in=0;distributed=0;collected=0;extras=[];lastpost=None;firstpre=None;all_events=[]
 for tx,source in sorted(txs.values(),key=lambda t:(t[0]['slot'],t[0].get('transactionIndex',-1))):
  sig=tx['transaction']['signatures'][0];keys=[C.key(k)for k in tx['transaction']['message']['accountKeys']];i=keys.index(vault);pre=tx['meta']['preBalances'][i];post=tx['meta']['postBalances'][i];lastpost=post
  if firstpre is None:firstpre=pre
  flat=C.D.flatten_instructions(tx);es=C.events(tx,source,errors);all_events+=es;ins=[]
  for ix in flat:
   if ix['programId']not in C.IXS or not ix.get('data'):continue
   schema=C.IXS[ix['programId']].get(C.D.unb58(ix['data'])[:8])
   if schema:ins.append((ix,schema,{f['name']:C.key(a)for f,a in zip(schema['accounts'],ix.get('accounts',[]))}))
  ein=0;eout=0;details=[]
  for e in es:
   v=e['event'];n=e['name'];native=v.get('quote_mint')in(None,C.SOL,C.WSOL)
   if not native:continue
   if n=='TradeEvent'and v.get('mint')==target['mint']and v.get('creator')==target['config']:
    candidates=[z for z in ins if z[1]['name'].startswith(('buy','sell'))and z[2].get('mint',z[2].get('base_mint'))==target['mint']and z[2].get('creator_vault')==vault]
   elif n=='DistributeCreatorFeesEvent'and v.get('mint')==target['mint']and v.get('sharing_config')==target['config']:
    candidates=[z for z in ins if z[1]['name'].startswith('distribute_creator_fees')and z[2].get('mint')==target['mint']and z[2].get('sharing_config')==target['config']and z[2].get('creator_vault')==vault]
   elif n=='CollectCreatorFeeEvent'and v.get('creator')==target['config']:
    candidates=[z for z in ins if z[1]['name']=='collect_creator_fee'and z[2].get('creator_vault')==vault]
   else:continue
   indexes=set()
   for ix in flat:
    if ix['programId']!=e['program']or not ix.get('data'):continue
    raw=C.D.unb58(ix['data'])
    if raw[:8]==C.D.EVENT_CPI_TAG and hashlib.sha256(raw[8:]).hexdigest()==e['payloadSha256']:indexes.add(ix['topLevelInstructionIndex'])
   if len(indexes)==1:candidates=[z for z in candidates if z[0]['topLevelInstructionIndex']in indexes]
   transfers=[]
   if len(candidates)==1:
    top=candidates[0][0]['topLevelInstructionIndex']
    for ix in flat:
     parsed=ix.get('parsed')or{};parsed=parsed if isinstance(parsed,dict)else{};info=parsed.get('info',{})
     if ix['programId']==C.SOL and parsed.get('type')=='transfer'and ix['topLevelInstructionIndex']==top and (info.get('source')==vault or info.get('destination')==vault):transfers.append(info)
   amount=int(v.get('creator_fee',0)if n!='DistributeCreatorFeesEvent'else v['distributed']);actual=sum(int(x['lamports'])for x in transfers if x.get('destination')==vault)if n=='TradeEvent'else sum(int(x['lamports'])for x in transfers if x.get('source')==vault)
   verified=len(candidates)==1 and actual==amount
   if n=='TradeEvent'and v.get('is_buy')is True and len(candidates)==1 and sum(int(x['lamports'])for x in transfers if x.get('destination')==vault and int(x['lamports'])==amount)==amount:
    actual=amount;verified=True
   details.append({'name':n,'payloadSha256':e['payloadSha256'],'topLevelInstructionIndexes':sorted(indexes),'candidateCount':len(candidates),'amountLamports':str(amount),'actualSystemTransferLamports':str(actual),'verified':verified,'verification':'system_transfer'if verified else None,'tradeIsBuy':v.get('is_buy'),'instructionName':candidates[0][1]['name']if len(candidates)==1 else None,'transfers':transfers})
   if verified:
    if n=='TradeEvent':ein+=amount;fee_in+=amount
    else:
     eout+=amount
     if n=='DistributeCreatorFeesEvent':distributed+=amount
     else:collected+=amount
  # Pump sell moves program lamports directly. Verify exact transaction cash
  # equality with declared creator fee and independently visible funding transfers.
  unresolved=[d for d in details if not d['verified']]
  funding=sum(int((ix.get('parsed')or{}).get('info',{}).get('lamports',0))for ix in flat if isinstance(ix.get('parsed'),dict)and ix['programId']==C.SOL and ix['parsed'].get('type')=='transfer'and ix['parsed'].get('info',{}).get('destination')==vault)
  known_buy=sum(int(d['actualSystemTransferLamports'])for d in details if d['verified']and d['name']=='TradeEvent')
  nonfee_funding=funding-known_buy
  if unresolved and all(d['name']=='TradeEvent'and d['tradeIsBuy']is False and d['candidateCount']==1 for d in unresolved):
   expected=sum(int(d['amountLamports'])for d in unresolved)
   if post-pre-ein+eout-nonfee_funding==expected:
    for d in unresolved:d['verified']=True;d['verification']='sell_direct_lamport_cash_equality'
    ein+=expected;fee_in+=expected
  extra=post-pre-ein+eout
  if extra:extras.append({'signature':sig,'lamports':str(extra),'pre':str(pre),'post':str(post),'rawSource':source})
  rows.append({'signature':sig,'slot':tx['slot'],'blockTime':tx['blockTime'],'utc':C.utc(tx['blockTime']),'preLamports':str(pre),'postLamports':str(post),'deltaLamports':str(post-pre),'verifiedFeeInLamports':str(ein),'verifiedFeeOutLamports':str(eout),'residualLamports':str(extra),'details':details,'rawSource':source})
 current=query(f'{name}/current-account','getAccountInfo',[vault,{'encoding':'base64','commitment':'finalized'}])['result'];account=current['value']or{'lamports':0,'data':['','base64']};rent=650240 if current['value']else 0
 summary={**cfg,**target,'transactionCount':len(txs),'terminal':True,'verifiedTradeCreatorFeeInflowsLamports':str(fee_in),'verifiedDistributionLamports':str(distributed),'verifiedCollectCreatorFeeLamports':str(collected),'firstPreLamports':str(firstpre),'lastPostLamports':str(lastpost),'currentBalanceLamports':str(account['lamports']),'currentSlot':current['context']['slot'],'currentRentLamports':str(rent),'rentEvidence':'outputs/ramonos-launches-20261013/routes/raw/configs-curves-005.response.json; RentSysvar [5080,1.0,50], (128+space)*5080','currentAboveRentLamports':str(account['lamports']-rent),'lastPostMatchesCurrent':lastpost==account['lamports'],'residualMovements':extras,'unverifiedFeeEvents':[{'signature':r['signature'],**d}for r in rows for d in r['details']if not d['verified']],'decodeErrors':errors}
 summary['netVerifiedFeeLotsLamports']=str(fee_in-distributed-collected)
 summary['feeCashReconciled']=fee_in-distributed-collected>=0 and not errors and not summary['unverifiedFeeEvents'] and all(0<=int(x['lamports'])<=890880 and int(x['pre'])==0 for x in extras)and firstpre==0 and lastpost==sum(int(x['lamports'])for x in extras)+fee_in-distributed-collected
 summary['pendingVerifiedFeeLotsLamports']=str(fee_in-distributed-collected)if summary['feeCashReconciled']else None
 summary['historicalNonfeeFundingLamports']=str(sum(int(x['lamports'])for x in extras))if summary['feeCashReconciled']else None
 payments=collections.Counter()
 for row in rows:
  for detail in row['details']:
   if detail['name']=='DistributeCreatorFeesEvent'and detail['verified']:
    for tr in detail['transfers']:payments[tr['destination']]+=int(tr['lamports'])
 summary['actualDistributionPaymentsByAddressLamports']={a:str(n)for a,n in payments.items()}
 save(OUT/name/'replay.json' ,{'summary':summary,'transactions':rows,'events':all_events});save(OUT/name/'summary.json',summary);summaries.append(summary);print(json.dumps({k:v for k,v in summary.items()if k not in ['residualMovements','unverifiedFeeEvents']}),flush=True)
save(OUT/'summary.json',summaries)
