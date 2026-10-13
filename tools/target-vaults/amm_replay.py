import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,concurrent.futures,collections,base64
exec(((CODE_ROOT/'tools/target-vaults/replay.py').read_text().split('summaries=[]')[0]))
routes=[r for r in routes if r['name']in ['PsyopCartoon','this coin will retire you']]
latest='--latest' in sys.argv
unwraps=json.loads((OUT/'amm-native-unwraps.json').read_text())
if latest:
 for r in routes:
  receipt=max(next(x for x in unwraps if x['mint']==r['mint'])['rows'],key=lambda z:(z['slot'],z['blockTime']))
  r['lower']=receipt['blockTime'];r['baselineSignature']=receipt['signature']
def capture(r):
 label=('amm-latest-'if latest else'amm-')+r['mint'];address=r['cfgAmmAta'];cursor=None;seen=set();page=0;pages=[];txs={}
 while True:
  opts={'transactionDetails':'full','encoding':'jsonParsed','sortOrder':'asc','limit':1000,'maxSupportedTransactionVersion':1,'commitment':'finalized','filters':{'status':'succeeded','tokenAccounts':'none','blockTime':{'gte':r.get('lower',0),'lt':cfg['cutoff']}}}
  if cursor:opts['paginationToken']=cursor
  name=f'{label}/page-{page:04d}';result=query(name,'getTransactionsForAddress',[address,opts])['result'];batch=result['data'];nxt=result.get('paginationToken');source=str((RAW/(name+'.response.json')).relative_to(ROOT))
  for tx in batch:
   sig=tx['transaction']['signatures'][0];assert sig not in txs;txs[sig]=(tx,source)
  pages.append({'path':source,'sha256':C.sha(ROOT/source),'count':len(batch),'cursorIn':cursor,'cursorOut':nxt});save(OUT/label/'coverage.json',{**cfg,'address':address,'terminal':not bool(nxt),'pages':pages,'transactionCount':len(txs)})
  if not nxt:break
  assert batch and nxt not in seen;seen.add(nxt);cursor=nxt;page+=1
  print(json.dumps({'route':r['name'],'pages':page,'transactions':len(txs)}),flush=True)
 return r,label,txs
with concurrent.futures.ThreadPoolExecutor(max_workers=2)as executor:
 captures=list(executor.map(capture,routes))
for r,label,txs in captures:
 errors=[];rows=[];unknown=[];total_in=0;total_out=0;lastpost=None;firstpre=None;baseline_reached=not latest
 for tx,source in sorted(txs.values(),key=lambda t:(t[0]['slot'],t[0].get('transactionIndex',-1))):
  keys=[C.key(x)for x in tx['transaction']['message']['accountKeys']];address=r['cfgAmmAta'];i=keys.index(address);sig=tx['transaction']['signatures'][0]
  def token(bs):
   z=[x for x in bs if x['accountIndex']==i]
   if not z:return 0
   assert len(z)==1 and z[0]['mint']==C.WSOL and z[0].get('owner')==r['cfgAmmAuthority'];return int(z[0]['uiTokenAmount']['amount'])
  pre=token(tx['meta'].get('preTokenBalances',[]));post=token(tx['meta'].get('postTokenBalances',[]));lastpost=post
  if firstpre is None:firstpre=pre
  if latest and not baseline_reached:
   if sig==r['baselineSignature']:
    assert post==0;baseline_reached=True;firstpre=0
   continue
  flat=C.D.flatten_instructions(tx);events=C.events(tx,source,errors);details=[];ein=0;eout=0
  for e in events:
   v=e['event'];n=e['name']
   if n not in ['BuyEvent','SellEvent']or v.get('pool')!=r['canonicalPool']or v.get('coin_creator')!=r['sharingConfig']:continue
   indexes=set()
   for ix in flat:
    if ix['programId']!=e['program']or not ix.get('data'):continue
    raw=C.D.unb58(ix['data'])
    if raw[:8]==C.D.EVENT_CPI_TAG and hashlib.sha256(raw[8:]).hexdigest()==e['payloadSha256']:indexes.add(ix['topLevelInstructionIndex'])
   candidates=[]
   for ix in flat:
    if ix['programId']!=e['program']or not ix.get('data'):continue
    schema=C.IXS[ix['programId']].get(C.D.unb58(ix['data'])[:8])
    if not schema or not schema['name'].startswith(('buy','sell')):continue
    a={f['name']:C.key(z)for f,z in zip(schema['accounts'],ix.get('accounts',[]))}
    if a.get('pool')==r['canonicalPool']and a.get('base_mint')==r['mint']and a.get('quote_mint')==C.WSOL and a.get('coin_creator_vault_ata')==address and (not indexes or ix['topLevelInstructionIndex']in indexes):candidates.append(ix)
   amount=int(v['coin_creator_fee']);transfers=[]
   if len(candidates)==1:
    top=candidates[0]['topLevelInstructionIndex']
    for ix in flat:
     p=ix.get('parsed');info=p.get('info',{})if isinstance(p,dict)else{}
     if isinstance(p,dict)and p.get('type')=='transferChecked'and info.get('mint')==C.WSOL and info.get('destination')==address and ix['topLevelInstructionIndex']==top:transfers.append(info)
   actual=sum(int(t['tokenAmount']['amount'])for t in transfers);verified=len(candidates)==1 and amount==actual
   details.append({'name':n,'eventPayloadSha256':e['payloadSha256'],'topLevelInstructionIndexes':sorted(indexes),'candidates':len(candidates),'feeRaw':str(amount),'actualTransferRaw':str(actual),'verified':verified})
   if verified:ein+=amount;total_in+=amount
  closes=[]
  for ix in flat:
   p=ix.get('parsed');info=p.get('info',{})if isinstance(p,dict)else{}
   if isinstance(p,dict)and p.get('type')=='closeAccount'and info.get('account')==address and info.get('owner')==r['cfgAmmAuthority']and info.get('destination')==r['cfgAmmAuthority']:
    closes.append(info);eout+=pre+ein;total_out+=pre+ein
  residual=post-pre-ein+eout
  if residual or any(not d['verified']for d in details):unknown.append({'signature':sig,'residualRaw':str(residual),'details':details,'source':source})
  rows.append({'signature':sig,'slot':tx['slot'],'blockTime':tx['blockTime'],'preRaw':str(pre),'postRaw':str(post),'verifiedCreatorFeeRaw':str(ein),'closedFeeRaw':str(eout),'residualRaw':str(residual),'details':details,'closes':closes,'source':source})
 current=query(label+'/current-account','getAccountInfo',[r['cfgAmmAta'],{'encoding':'base64','commitment':'finalized'}])['result'];a=current['value'];current_raw=int.from_bytes(base64.b64decode(a['data'][0])[64:72],'little')if a else 0
 if a:
  raw=base64.b64decode(a['data'][0]);assert C.D.b58(raw[:32])==C.WSOL and C.D.b58(raw[32:64])==r['cfgAmmAuthority']
 summary={**cfg,'name':r['name'],'mint':r['mint'],'config':r['sharingConfig'],'pool':r['canonicalPool'],'ata':r['cfgAmmAta'],'authority':r['cfgAmmAuthority'],'transactionCount':len(txs),'terminal':True,'verifiedCreatorFeeInRaw':str(total_in),'verifiedClosedOutRaw':str(total_out),'firstPreRaw':str(firstpre),'lastPostRaw':str(lastpost),'currentRaw':str(current_raw),'lastPostMatchesCurrent':lastpost==current_raw,'unknown':unknown,'decodeErrors':errors,'baselineSignature':r.get('baselineSignature'),'lowerBound':r.get('lower',0),'baselineReached':baseline_reached,'feeProvenanceReconciled':baseline_reached and not unknown and not errors and firstpre==0 and total_in-total_out==lastpost and lastpost==current_raw}
 save(OUT/label/'replay.json',{'summary':summary,'transactions':rows});print(json.dumps({k:v for k,v in summary.items()if k!='unknown'}),flush=True)
