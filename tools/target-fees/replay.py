import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
"""Read-only direct GitHub destination replay; financial execution cap 0 SOL."""
import pathlib,json,importlib.util,datetime,hashlib,collections,re,sys,urllib.request
sys.dont_write_bytecode=True
OUT=ROOT/'outputs/ramonos-launches-20261013/target-fees'; RAW=OUT/'raw'
RAW.mkdir(parents=True,exist_ok=True)
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
C=module('ramonos_fee_core',CODE_ROOT/'tools/fee_core.py')
RPC=module('ramonos_readonly_rpc',CODE_ROOT/'tools/rpc_readonly.py')
SDK=CODE_ROOT/'schemas'
for name in ['pump','pump_amm','pump_fees']:
    j=json.loads((SDK/f'{name}.json').read_text());C.IDLS[j['address']]=j;C.TYPES[j['address']]={t['name']:t['type']for t in j['types']}
C.TAGS={bytes(e['discriminator']):(p,e['name'])for p,j in C.IDLS.items()for e in j['events']if e['name']in C.NAMES}
C.IXS={p:{bytes(i['discriminator']):i for i in j['instructions']}for p,j in C.IDLS.items()}
A='qNG5wnFQWzDHm1zGTMnqddwGp861LK7srHv3prtn1Dv'; UID='12810712'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(name,data):(OUT/name).write_text(json.dumps(data,indent=2))
conf=OUT/'config.json'
if conf.exists():cfg=json.loads(conf.read_text())
else:
    cutoff=int(datetime.datetime.now(datetime.timezone.utc).timestamp());cfg={'address':A,'githubNumericId':UID,'cutoff':cutoff,'cutoffUtc':C.utc(cutoff),'commitment':'finalized','financialExecutionCapSol':0};save('config.json',cfg)
cursor=None;seen=set();pages=[];txs={};index=0
while True:
    opts={'transactionDetails':'full','encoding':'jsonParsed','sortOrder':'asc','limit':1000,'maxSupportedTransactionVersion':1,'commitment':'finalized','filters':{'status':'succeeded','tokenAccounts':'none','blockTime':{'gte':0,'lt':cfg['cutoff']}}}
    if cursor:opts['paginationToken']=cursor
    params=[A,opts];p=RAW/f'page-{index:04d}.response.json';rq=p.with_name(f'page-{index:04d}.request.json')
    if p.exists():
        assert json.loads(rq.read_text())['params']==params,'Mismatched cached request';res=json.loads(p.read_text())
    else:
        start=now();res=RPC.rpc('getTransactionsForAddress',params);p.write_text(json.dumps(res,separators=(',',':')));rq.write_text(json.dumps({'method':'getTransactionsForAddress','params':params,'startedUtc':start,'completedUtc':now(),'endpoint':'configured mainnet read-only RPC; credentials omitted','responseSha256':C.sha(p),'financialExecutionCapSol':0},indent=2))
    result=res['result'];batch=result['data'];nxt=result.get('paginationToken');source=str(p.relative_to(ROOT))
    for tx in batch:
        assert tx['meta']['err'] is None and tx['blockTime']<cfg['cutoff'];sig=tx['transaction']['signatures'][0];assert sig not in txs,'Duplicate reference';txs[sig]=(tx,source)
    pages.append({'path':source,'sha256':C.sha(p),'count':len(batch),'cursorIn':cursor,'cursorOut':nxt,'minBlockTime':min((x['blockTime']for x in batch),default=None),'maxBlockTime':max((x['blockTime']for x in batch),default=None)})
    save('coverage.json',{**cfg,'terminal':not bool(nxt),'pages':pages,'transactionCount':len(txs)})
    if not nxt:break
    if not batch or nxt in seen:raise RuntimeError('Nonadvancing pagination')
    seen.add(nxt);cursor=nxt;index+=1
errors=[];events=[];distributions=[];claims=[];checks=[]
def delta(tx,a):
    keys=[C.key(x)for x in tx['transaction']['message']['accountKeys']]
    return int(tx['meta']['postBalances'][keys.index(a)])-int(tx['meta']['preBalances'][keys.index(a)])if a in keys else None
for sig,(tx,source)in txs.items():
    es=C.events(tx,source,errors);events+=es
    for e in es:
        v=e['event']
        if e['name']=='SocialFeePdaClaimed'and v.get('social_fee_pda')==A:claims.append(e)
        if e['name']!='DistributeCreatorFeesEvent'or not any(s['address']==A for s in v['shareholders']):continue
        q=v.get('quote_mint');native=q in (None,C.SOL,C.WSOL);candidates=[]
        for ix in C.D.flatten_instructions(tx):
            if ix['programId']not in C.IXS or not ix.get('data'):continue
            schema=C.IXS[ix['programId']].get(C.D.unb58(ix['data'])[:8])
            if schema and schema['name'].startswith('distribute_creator_fees'):
                mapped={f['name']:C.key(a)for f,a in zip(schema['accounts'],ix.get('accounts',[]))}
                if mapped.get('mint')==v['mint']and mapped.get('sharing_config')==v['sharing_config']:candidates.append((ix,mapped))
        event_instruction_indexes=set()
        for event_ix in C.D.flatten_instructions(tx):
            if event_ix['programId']!=e['program']or not event_ix.get('data'):continue
            event_raw=C.D.unb58(event_ix['data'])
            if event_raw[:8]==C.D.EVENT_CPI_TAG and hashlib.sha256(event_raw[8:]).hexdigest()==e['payloadSha256']:event_instruction_indexes.add(event_ix['topLevelInstructionIndex'])
        if len(candidates)>1 and len(event_instruction_indexes)==1:candidates=[candidate for candidate in candidates if candidate[0]['topLevelInstructionIndex']in event_instruction_indexes]
        transfers=collections.Counter();verified=False;vault=None
        if len(candidates)==1:
            ix,mapped=candidates[0];vault=mapped.get('creator_vault');shareholders={x['address']for x in v['shareholders']}
            for ix2 in C.D.flatten_instructions(tx):
                parsed=ix2.get('parsed')or{};info=parsed.get('info',{})
                if ix2['programId']==C.SOL and parsed.get('type')=='transfer'and info.get('source')==vault and info.get('destination')in shareholders and ix2['topLevelInstructionIndex']==ix['topLevelInstructionIndex']:transfers[info['destination']]+=int(info['lamports'])
            verified=native and sum(transfers.values())==int(v['distributed'])
        checks.append({'signature':sig,'mint':v['mint'],'check':'native distribution event equals matched vault transfers','passed':verified,'native':native,'candidates':len(candidates)})
        distributions.append({**e,'nativeQuote':native,'recipient':A,'nativePaymentLamports':str(transfers[A])if verified else None,'nativeTransfersVerified':verified,'creatorVault':vault})
native_claims=[e for e in claims if e['event'].get('quote_mint')in(None,C.SOL,C.WSOL)]
by_mint=collections.Counter()
for e in distributions:
    if e['nativeTransfersVerified']:by_mint[e['event']['mint']]+=int(e['nativePaymentLamports'])
unexplained=[];initial_funding=None;lastpost=None
for tx,source in sorted(txs.values(),key=lambda t:(t[0]['slot'],t[0].get('transactionIndex',-1))):
    keys=[C.key(x)for x in tx['transaction']['message']['accountKeys']];i=keys.index(A);pre=int(tx['meta']['preBalances'][i]);post=int(tx['meta']['postBalances'][i]);lastpost=post;sig=tx['transaction']['signatures'][0]
    deposit=sum(int(e['nativePaymentLamports'])for e in distributions if e['signature']==sig and e['nativeTransfersVerified']);withdrawal=sum(int(e['event']['amount_claimed'])for e in native_claims if e['signature']==sig);extra=post-pre-deposit+withdrawal
    creation=any(e['signature']==sig and e['name']=='SocialFeePdaCreated'and e['event'].get('social_fee_pda')==A for e in events)
    if extra:
        if pre==0 and creation and initial_funding is None:initial_funding=extra
        else:unexplained.append({'signature':sig,'extraLamports':str(extra),'rawSource':source})
reconciled=not native_claims and not unexplained and initial_funding is not None and lastpost==initial_funding+sum(by_mint.values())and all(e['nativeTransfersVerified']for e in distributions if e['nativeQuote'])
launches=json.loads((ROOT/'outputs/ramonos-launches-20261013/census/launches.json').read_text());mints={r['mint']for r in launches};selected={m:str(n)for m,n in by_mint.items()if m in mints};other={m:str(n)for m,n in by_mint.items()if m not in mints}
summary={**cfg,'transactionCount':len(txs),'terminal':True,'claimEventCountAllAssets':len(claims),'nativeClaimEventCount':len(native_claims),'nativeClaimedLamports':str(sum(int(e['event']['amount_claimed'])for e in native_claims)),'distributionCount':len(distributions),'nativeMintAttributionReconciled':reconciled,'initialFundingLamports':str(initial_funding)if initial_funding is not None else None,'terminalNativeBalanceLamports':str(lastpost),'unexplainedNativeMovements':unexplained,'pendingNativeByMint':{m:str(n)for m,n in by_mint.items()}if reconciled else None,'ramonosUnclaimedNativeByMint':selected if reconciled else None,'otherLauncherUnclaimedNativeByMint':other if reconciled else None,'ramonosUnclaimedNativeLamports':str(sum(int(n)for n in selected.values()))if reconciled else None,'errors':errors,'failedChecks':[c for c in checks if not c['passed']and c['native']],'limitations':['Single direct GitHub destination; UsePaid downstream developer settlement is unknown.','Only exact mint-tagged native transfers are fee income; initial account funding excluded.','Replayed to exact cutoff; upstream custody snapshot is separate and not atomic.']}
save('replay.json',{'summary':summary,'events':events,'distributions':distributions,'claims':claims,'checks':checks});save('summary.json',summary)
if not (OUT/'github-identity.json').exists():
    raise RuntimeError('Missing retained GitHub identity; reacquire separately as a new read-only observation.')
print(json.dumps(summary),flush=True)
