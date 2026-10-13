"""Offline census economics from retained centralized creator-wallet references.
All execution effects are prohibited. Exact integer units, no signing or network.
"""
import json,pathlib,collections,datetime,decimal,csv,hashlib,os
import sys
CODE_ROOT=pathlib.Path(os.environ.get('RAMONOS_CODE_ROOT',pathlib.Path(__file__).resolve().parents[2])).resolve()
sys.path.insert(0,str(CODE_ROOT/'tools'))
import decoder as D
import fee_core as C
D.PROGRAM=D.IDL['address'];D.AMM_PROGRAM=D.AMM_IDL['address'];D.FEE_PROGRAM=D.FEE_IDL['address']
D.TIPS=set(json.loads((C.ROOT/'outputs/ramonos-launches-20261013/trading/inputs/jito-tip-accounts.json').read_text())['result'])
ROOT=pathlib.Path(os.environ.get('RAMONOS_RESEARCH_ROOT',pathlib.Path.cwd())).resolve(); D.ROOT=ROOT; OUT=ROOT/'outputs/ramonos-launches-20261013/trading'; RAW=ROOT/'outputs/ramonos-launches-20261013/census/raw'; WORK=ROOT/'work/ramonos-launches-20261013/trading'
W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'; WSOL='So11111111111111111111111111111111111111112'
SYSTEM='11111111111111111111111111111111'; TOKENS={'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA','TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'}
LL_IDL=json.loads((ROOT/'outputs/ramonos-launches-20261013/trading/inputs/launchlab-idl.json').read_text()); LL=LL_IDL['address']; LL_TYPES={t['name']:t['type'] for t in LL_IDL['types']}; LL_EVENTS={bytes(e['discriminator']):e['name'] for e in LL_IDL['events']}
IX_NAMES={p:{bytes(i['discriminator']):i['name'] for i in idl['instructions']} for p,idl in [(D.PROGRAM,D.IDL),(D.AMM_PROGRAM,D.AMM_IDL),(LL,LL_IDL)]}
if D.FEE_PROGRAM: IX_NAMES[D.FEE_PROGRAM]={bytes(i['discriminator']):i['name'] for i in D.FEE_IDL['instructions']}
class LLReader(D.Reader):
 def value(self,t):
  if isinstance(t,dict) and 'array' in t:return [self.value(t['array'][0]) for _ in range(t['array'][1])]
  if isinstance(t,dict) and 'defined' in t:
   x=self.types[t['defined']['name']]
   if x['kind']=='enum':
    v=x['variants'][self.take(1)[0]]
    if not v.get('fields'):return v['name']
    fields=v['fields']
    return {'variant':v['name'],'fields':{f['name']:self.value(f['type']) for f in fields} if isinstance(fields[0],dict) and 'name' in fields[0] else [self.value(f) for f in fields]}
  return super().value(t)
def extract_native_instructions(instructions):
    transfers = []
    creations = []
    closes = []
    for ix in instructions:
        parsed = ix.get("parsed", {})
        if not isinstance(parsed, dict):
            continue
        info = parsed.get("info", {})
        location = {key: ix[key] for key in ["topLevelInstructionIndex", "innerInstructionIndex", "parentProgram"]}
        if ix["programId"] == "11111111111111111111111111111111" and parsed.get("type") in {"transfer", "transferWithSeed"}:
            transfers.append({"source": info["source"], "destination": info["destination"], "lamports": str(info["lamports"]),
                              "sol": D.units(info["lamports"], 9), "officialJitoTipAccount": info["destination"] in D.TIPS, **location})
        if ix["programId"] == "11111111111111111111111111111111" and parsed.get("type") in {"createAccount", "createAccountWithSeed"}:
            creations.append({"source": info["source"], "newAccount": info["newAccount"], "lamports": str(info["lamports"]),
                              "ownerProgram": info["owner"], **location})
        if parsed.get("type") == "closeAccount" and ix["programId"] in {"TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb", "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}:
            closes.append({**info, **location})
    return transfers, creations, closes

D.extract_native_instructions=extract_native_instructions
def key(k):return k['pubkey'] if isinstance(k,dict) else k
def ts(t):return D.utc(t)
def sol(n):return D.units(n,9)
def iamount(i):return int(i.get('amount',i.get('tokenAmount',{}).get('amount',0)))
def qmint(v):return WSOL if v in {None,SYSTEM} else v

EXT=ROOT/'outputs/ramonos-launches-20261013/trading'
WORK=EXT
manifest=json.loads((ROOT/'outputs/ramonos-launches-20261013/census/history-manifest.json').read_text())
cutoff=manifest['cutoff'];start=int(datetime.datetime.fromisoformat(manifest['pages'][0]['firstUtc'].replace('Z','+00:00')).timestamp())
launches={r['mint']:r for r in json.loads((ROOT/'outputs/ramonos-launches-20261013/census/launches.json').read_text())}
for l in launches.values():
 l['quoteMint']=qmint(l.get('initialQuoteMint'));l['quoteDecimals']=9 if l['quoteMint']==WSOL else None;l['curve']=l.get('launchlabPool',l.get('createEvent',{}).get('event',{}).get('bonding_curve'));l['inSupplied14']=False
for pg in manifest['pages']:
 p=ROOT/pg['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==pg['sha256']
TX={};sources={};duplicates=0
for p in manifest['pages']:
 for tx in json.loads((ROOT/p['path']).read_text())['result']['data']:
  if not start<=tx['blockTime']<cutoff:continue
  sig=tx['transaction']['signatures'][0]
  if sig in TX:duplicates+=1;continue
  TX[sig]=tx;sources[sig]=p['path']
assert sum(t['meta']['err'] is None for t in TX.values())==manifest['transactionCount']
ordered=sorted(TX.values(),key=lambda t:(t['slot'],t.get('transactionIndex',0),t['transaction']['signatures'][0]))
account_info={};mint_decimals={};target_account_mint={};transfer_fee_configs={}
for tx in ordered:
 keys=[key(a) for a in tx['transaction']['message']['accountKeys']]
 for stage in ['preTokenBalances','postTokenBalances']:
  for v in tx['meta'].get(stage,[]):
   a=keys[v['accountIndex']];account_info[a]={'mint':v['mint'],'owner':v.get('owner'),'decimals':v['uiTokenAmount']['decimals']};mint_decimals[v['mint']]=v['uiTokenAmount']['decimals']
   if v['mint'] in launches:target_account_mint[a]=v['mint']
 if tx['meta']['err'] is None:
  for ix in D.flatten_instructions(tx):
   p=ix.get('parsed',{});inf=p.get('info',{}) if isinstance(p,dict) else {}
   if ix['programId'] in TOKENS and isinstance(p,dict) and p.get('type')=='initializeTransferFeeConfig':transfer_fee_configs[inf['mint']]={'bps':int(inf['transferFeeBasisPoints']),'maximumFee':int(inf['maximumFee']),'signature':tx['transaction']['signatures'][0]}
for l in launches.values():
 if l['quoteDecimals'] is None:l['quoteDecimals']=mint_decimals.get(l['quoteMint'])
# Decode only successful transaction events. Failed logs are never trade proof.
records=[];errors=[];pool_mint={r['curve']:r['mint'] for r in launches.values() if r['platform']=='Raydium LaunchLab'}
for tx in ordered:
 sig=tx['transaction']['signatures'][0];meta=tx['meta'];keys=[key(a) for a in tx['transaction']['message']['accountKeys']]; ix=D.flatten_instructions(tx); fail=meta['err'] is not None
 events=[]
 if not fail:
  events=C.events(tx,sources[sig],errors)
  for x in ix:
   if x['programId']!=LL or not x.get('data') or x['innerInstructionIndex'] is None:continue
   raw=D.unb58(x['data'])
   if raw[:8]!=D.EVENT_CPI_TAG or raw[8:16] not in LL_EVENTS:continue
   name=LL_EVENTS[raw[8:16]]
   if name!='TradeEvent':continue
   r=LLReader(raw[8:],LL_TYPES);v={}
   try:
    for f in LL_TYPES[name]['fields']:v[f['name']]=r.value(f['type'])
    events.append({'name':name,'program':LL,'event':v,'source':'event_cpi','topLevelInstructionIndex':x['topLevelInstructionIndex'],'innerInstructionIndex':x['innerInstructionIndex']})
   except Exception as exc:errors.append({'signature':sig,'eventName':name,'error':str(exc)})
 for e in events:
  if e['name']=='CompletePumpAmmMigrationEvent' and e['event'].get('mint') in launches:pool_mint[e['event']['pool']]=e['event']['mint']
 names=[]
 for x in ix:
  if x['programId'] in IX_NAMES and x.get('data'):
   name=IX_NAMES[x['programId']].get(D.unb58(x['data'])[:8]);
   if name:names.append(name)
 native=meta['postBalances'][keys.index(W)]-meta['preBalances'][keys.index(W)] if W in keys else 0
 balances={};owner_delta=collections.Counter()
 for stage,prefix in [('preTokenBalances','pre'),('postTokenBalances','post')]:
  for v in meta.get(stage,[]):
   a=keys[v['accountIndex']]; info=account_info.get(a,{})
   b=balances.setdefault(a,{'mint':v['mint'],'owner':v.get('owner',info.get('owner')),'decimals':v['uiTokenAmount']['decimals'],'pre':0,'post':0});b[prefix]=int(v['uiTokenAmount']['amount'])
 for a,b in balances.items():
  if b['owner']==W:owner_delta[b['mint']]+=b['post']-b['pre']
 records.append({'sig':sig,'tx':tx,'keys':keys,'ix':ix,'events':events,'names':names,'failed':fail,'native':native,'ownedDeltas':dict(owner_delta),'balances':balances,'source':sources[sig]})
# Resolve AMM base mint via recorded base token accounts even if migration is out of the wallet window.
for rec in records:
 for e in rec['events']:
  if e['program']==D.AMM_PROGRAM and e['name'] in {'BuyEvent','SellEvent'}:
   v=e['event'];a=v.get('user_base_token_account');m=rec['balances'].get(a,account_info.get(a,{})).get('mint')
   if m in launches:pool_mint[v['pool']]=m
acc_to_mint={**target_account_mint,**{r['curve']:r['mint'] for r in launches.values()}}
# Per-launch complete rows even when unresolved.
rows={}
for m,l in launches.items():
 rows[m]={'mint':m,'name':l['name'],'symbol':l['symbol'],'platform':l['platform'],'createdUtc':l['utc'],'createdDateUtc':l['utc'][:10],'creationSignature':l['signature'],'quoteMint':l['quoteMint'],'quoteDecimals':l['quoteDecimals'],'inSupplied14':l['inSupplied14'],'buyCount':0,'sellCount':0,'tokensBoughtRaw':0,'tokensSoldRaw':0,'tokensTransferredInRaw':0,'tokensTransferredOutRaw':0,'tokensBurnedRaw':0,'unexplainedTargetDeltaRaw':0,'unknownInventoryTransactions':[],'quoteBuyPrincipalRaw':0,'quoteSellPrincipalRaw':0,'quoteTradeFeesRaw':0,'nativeWsolCashDeltaLamports':0,'failedNetworkFeesLamports':0,'ownerPaidNetworkFeesLamports':0,'creationNativeWsolDeltaLamports':0,'nativeWsolBuyDebitsLamports':0,'nativeWsolSellReceiptsLamports':0,'nativeWsolStandaloneDeltaLamports':0,'nativeRentFundingLamports':0,'nativeAccountClosureRefundLamports':0,'nativeJitoTipLamports':0,'nativeExternalOuterTransfersLamports':0,'targetAssociatedQuoteDeltaRaw':0,'multiLaunchTransactions':[],'excludedFeeOperationSignatures':[],'economicTransactions':[],'inventoryAccounts':{},'firstBuyUtc':None,'lastSaleUtc':None,'buyRouteNativeFundingLamports':0,'buyRouteNativeFundingSignatures':[]}
wallet_by_day=collections.defaultdict(lambda:collections.Counter());crosswalk=[];fee_operations=[];unallocated=[]
for rec in records:
 tx=rec['tx'];sig=rec['sig'];day=ts(tx['blockTime'])[:10];payer=rec['keys'][0];fee=int(tx['meta']['fee']);nw=rec['native']+rec['ownedDeltas'].get(WSOL,0);wd=wallet_by_day[day];wd['references']+=1;wd['failed' if rec['failed'] else 'successful']+=1;wd['nativeDelta']+=rec['native'];wd['wsolDelta']+=rec['ownedDeltas'].get(WSOL,0)
 if payer==W:wd['networkFees']+=fee;wd['failedNetworkFees' if rec['failed'] else 'successfulNetworkFees']+=fee
 direct=set(rec['keys'])&set(launches); referenced=direct|{acc_to_mint[a] for a in rec['keys'] if a in acc_to_mint}
 own_target_balances={b['mint'] for b in rec['balances'].values() if b['owner']==W and b['mint'] in launches}
 target_trades=collections.defaultdict(list)
 if not rec['failed']:
  for e in rec['events']:
   v=e['event']; m=v.get('mint') if e['program']==D.PROGRAM else pool_mint.get(v.get('pool',v.get('pool_state')))
   if m not in launches:continue
   if e['program']==D.PROGRAM and e['name']=='TradeEvent' and v.get('user')==W:
    target_trades[m].append({'venue':'Pump','buy':v['is_buy'],'token':int(v['token_amount']),'quote':int(v.get('quote_amount',v['sol_amount'])),'fees':int(v.get('fee',0))+int(v.get('creator_fee',0)),'event':e})
   elif e['program']==D.AMM_PROGRAM and e['name'] in {'BuyEvent','SellEvent'} and v.get('user')==W:
    buy=e['name']=='BuyEvent'
    # Event field semantics differ for exact-quote buy. Reconcile the actual
    # user quote transfers under this event's corresponding AMM instruction.
    parents=[]
    for q in rec['ix']:
     if q['programId']==D.AMM_PROGRAM and q.get('data'):
      raw=D.unb58(q['data'])
      if raw[:8]==D.EVENT_CPI_TAG and hashlib.sha256(raw[8:]).hexdigest()==e['payloadSha256']:parents.append(q['topLevelInstructionIndex'])
    assert len(set(parents))==1,(sig,'event parent unavailable')
    parent=parents[0];qacct=v['user_quote_token_account'];total=0;legs=[]
    for q in rec['ix']:
     p=q.get('parsed',{});inf=p.get('info',{}) if isinstance(p,dict) else {}
     if q['topLevelInstructionIndex']!=parent or q.get('parentProgram')!=D.AMM_PROGRAM or q['programId'] not in TOKENS or p.get('type') not in {'transfer','transferChecked'}:continue
     if (buy and inf.get('source')==qacct) or (not buy and inf.get('destination')==qacct):total+=iamount(inf);legs.append({'source':inf['source'],'destination':inf['destination'],'amountRaw':str(iamount(inf)),'topLevelInstructionIndex':parent,'innerInstructionIndex':q['innerInstructionIndex']})
    assert legs,(sig,'actual AMM quote transfers unavailable')
    principal=int(v['user_quote_amount_in' if buy else 'quote_amount_out']);fees=total-principal if buy else principal-total
    assert fees>=0,(sig,fees)
    target_trades[m].append({'venue':'PumpSwap','buy':buy,'token':int(v['base_amount_out' if buy else 'base_amount_in']),'quote':principal,'fees':fees,'actualQuoteTransferRaw':total,'actualQuoteTransferWitness':legs,'event':e})
   elif e['program']==LL and e['name']=='TradeEvent':
    # LaunchLab events omit user; the corresponding parent instruction supplies exact payer and mint.
    x=next((x for x in rec['ix'] if x['topLevelInstructionIndex']==e['topLevelInstructionIndex'] and x['programId']==LL and x.get('accounts') and x['accounts'][0]==W and len(x['accounts'])>9 and x['accounts'][9]==m and x.get('data') and IX_NAMES[LL].get(D.unb58(x['data'])[:8],'').startswith(('buy','sell'))),None)
    if x:
     buy=v['trade_direction']=='Buy';target_trades[m].append({'venue':'LaunchLab','buy':buy,'token':int(v['amount_out' if buy else 'amount_in']),'quote':abs(int(v['real_quote_after'])-int(v['real_quote_before'])),'actualQuoteTransferRaw':int(v['amount_in' if buy else 'amount_out']),'fees':int(v['protocol_fee'])+int(v['platform_fee'])+int(v['creator_fee'])+int(v['share_fee']),'quotePrincipalDefinition':'Exact pool real-quote reserve movement; amount_in/out is actual quote transfer including/deducting venue fees','event':e})
 # A zero-amount distribute call in a creation/config transaction is setup, not income.
 fee_op=False
 idls={D.PROGRAM:D.IDL,D.AMM_PROGRAM:D.AMM_IDL,LL:LL_IDL}
 if D.FEE_PROGRAM:idls[D.FEE_PROGRAM]=D.FEE_IDL
 for x in rec['ix']:
  if x['programId'] not in idls or not x.get('data') or not x.get('accounts'):continue
  idef=next((i for i in idls[x['programId']]['instructions'] if bytes(i['discriminator'])==D.unb58(x['data'])[:8]),None)
  if idef is None:continue
  n=idef['name'];roles={a['name']:x['accounts'][i] for i,a in enumerate(idef['accounts']) if i<len(x['accounts'])}
  beneficiary=None
  if n.startswith('collect_creator_fee'):beneficiary=roles.get('creator')
  elif n=='collect_coin_creator_fee':beneficiary=roles.get('coin_creator')
  elif n.startswith(('claim_cashback','claim_token_incentives')):beneficiary=roles.get('user')
  elif n.startswith('claim_social_fee_pda'):beneficiary=roles.get('recipient')
  elif n.startswith(('claim_creator','claim_platform','claim_protocol')):
   a=roles.get('recipient_token_account');beneficiary=rec['balances'].get(a,account_info.get(a,{})).get('owner')
  if beneficiary==W:fee_op=True
 fee_op=fee_op or any(e['name']=='SocialFeePdaClaimed' and e['event'].get('recipient')==W or e['name']=='DistributeCreatorFeesEvent' and int(e['event'].get('distributed',0))>0 and any(s['address']==W for s in e['event'].get('shareholders',[])) for e in rec['events'])
 # Token2022 LaunchLab events report pool-side gross/net amounts. Reconcile the
 # wallet inventory to the parsed original-wallet transfer and initialized tax.
 for m,trades in target_trades.items():
  for t in trades:
   if t['venue']!='LaunchLab' or m not in transfer_fee_configs:continue
   cfg=transfer_fee_configs[m];fee_for=lambda n:min(cfg['maximumFee'],(n*cfg['bps']+9999)//10000)
   legs=[]
   for x in rec['ix']:
    p=x.get('parsed',{});inf=p.get('info',{}) if isinstance(p,dict) else {}
    if x['programId'] not in TOKENS or not isinstance(p,dict) or p.get('type') not in {'transfer','transferChecked'}:continue
    src=inf.get('source');dst=inf.get('destination');si=rec['balances'].get(src,account_info.get(src,{}));di=rec['balances'].get(dst,account_info.get(dst,{}));lm=inf.get('mint',si.get('mint',di.get('mint')))
    if lm==m and ((t['buy'] and di.get('owner')==W) or (not t['buy'] and si.get('owner')==W)):legs.append(iamount(inf))
   if len(legs)!=1:continue
   gross=legs[0];tax_fee=fee_for(gross);event_token=t['token'];wallet_token=gross-tax_fee if t['buy'] else gross
   if event_token!=(gross if t['buy'] else gross-tax_fee):continue
   if len(trades)==1 and rec['ownedDeltas'].get(m,0)!=wallet_token*(1 if t['buy'] else -1):continue
   t['eventPoolTokenRaw']=event_token;t['token']=wallet_token;t['targetTransferFeeRaw']=tax_fee;t['tokenTaxProofSignature']=cfg['signature']
 transfers=collections.defaultdict(lambda:collections.Counter());burns=collections.Counter();direct_native_in=0;direct_native_out=0
 if not rec['failed']:
  for x in rec['ix']:
   p=x.get('parsed',{}); info=p.get('info',{}) if isinstance(p,dict) else {};kind=p.get('type') if isinstance(p,dict) else None
   if x['programId']==SYSTEM and kind in {'transfer','transferWithSeed'}:
    if info.get('destination')==W:direct_native_in+=int(info['lamports'])
    if info.get('source')==W:direct_native_out+=int(info['lamports'])
   if x['programId'] in TOKENS and kind in {'transfer','transferChecked'}:
    src=info.get('source');dst=info.get('destination');si=rec['balances'].get(src,account_info.get(src,{}));di=rec['balances'].get(dst,account_info.get(dst,{}));m=info.get('mint',si.get('mint',di.get('mint')))
    if m not in launches:continue
    # Pool legs of a decoded trade are not external inventory transfers.
    if m in target_trades:continue
    a=iamount(info)
    if si.get('owner')==W and di.get('owner')!=W:transfers[m]['out']+=a
    if di.get('owner')==W and si.get('owner')!=W:transfers[m]['in']+=a
   if x['programId'] in TOKENS and kind in {'burn','burnChecked'}:
    a=info.get('account');ai=rec['balances'].get(a,account_info.get(a,{}));m=info.get('mint',ai.get('mint'))
    if m in launches and ai.get('owner')==W:burns[m]+=iamount(info)
 wd['parsedNativeIn']+=direct_native_in;wd['parsedNativeOut']+=direct_native_out
 active=set(target_trades)|{m for m in own_target_balances if rec['ownedDeltas'].get(m,0)!=0}|set(transfers)|set(burns)
 if any(sig==l['signature'] for l in launches.values()):active|={m for m,l in launches.items() if l['signature']==sig}
 # Empty original ATAs can be closed in a pooled cleanup. Attribute only each
 # exact account's recovered reserve; leave the shared service/network charge
 # in the wallet-level residual once rather than charging every mint for it.
 closure_components=[]
 if not rec['failed'] and not active and not fee_op:
  for x in rec['ix']:
   p=x.get('parsed',{});inf=p.get('info',{}) if isinstance(p,dict) else {};a=inf.get('account');b=rec['balances'].get(a,account_info.get(a,{}))
   if x['programId'] not in TOKENS or not isinstance(p,dict) or p.get('type')!='closeAccount' or inf.get('destination')!=W or b.get('owner')!=W or b.get('mint') not in launches or a not in rec['keys']:continue
   refund=int(tx['meta']['preBalances'][rec['keys'].index(a)]);m=b['mint'];closure_components.append((m,a,refund))
 if closure_components:
  for m,a,refund in closure_components:
   r=rows[m];r['nativeWsolCashDeltaLamports']+=refund;r['nativeWsolStandaloneDeltaLamports']+=refund;r['nativeAccountClosureRefundLamports']+=refund
   if a in r['inventoryAccounts']:r['inventoryAccounts'][a].update(lastObservedPostRaw='0',lastObservedSignature=sig,lastObservedUtc=ts(tx['blockTime']))
   r.setdefault('sharedBatchCleanupChargeExcludedSignatures',[]).append(sig)
   r['economicTransactions'].append({'signature':sig,'utc':ts(tx['blockTime']),'kind':'exact_target_ata_reserve_refund_component','nativeWsolDeltaLamports':str(refund),'nativeDeltaLamports':str(refund),'ownedWsolDeltaRaw':'0','targetDeltaRaw':'0','quoteAssetDeltaRaw':'0','networkFeeLamports':'0','names':rec['names'],'trades':[],'targetAccount':a,'wholeWalletTransactionDeltaLamports':str(nw),'sharedBatchChargeAllocation':'Only exact target account reserve allocated. Whole transaction network/service charge remains wallet-level once.','rawSource':rec['source']})
  residual=nw-sum(c[2] for c in closure_components)
  if residual:unallocated.append({'signature':sig,'utc':ts(tx['blockTime']),'nativeWsolDeltaLamports':str(residual),'wholeWalletTransactionDeltaLamports':str(nw),'exactTargetAtaRefundAllocatedLamports':str(sum(c[2] for c in closure_components)),'allocatedWeekMints':sorted({c[0] for c in closure_components}),'names':rec['names'],'kind':'batch_cleanup_residual_other_account_refunds_minus_shared_charges','rawSource':rec['source']})
  continue
 # Standalone configuration and ATA/account maintenance only when exact one launch is referenced and payer/signature owner is present.
 if not active and len(referenced)==1 and payer==W and not fee_op:active|=referenced
 if rec['failed']:
  # Failed messages are only paid-network-cost evidence, never inventory/effects.
  if payer==W and len(referenced)==1:
   m=next(iter(referenced));r=rows[m];r['failedNetworkFeesLamports']+=fee;r['nativeWsolCashDeltaLamports']+=nw
   r['economicTransactions'].append({'signature':sig,'utc':ts(tx['blockTime']),'kind':'failed_network_fee_only','nativeWsolDeltaLamports':str(nw),'networkFeeLamports':str(fee),'rawSource':rec['source']})
  continue
 mixed_target_fee=fee_op and (bool(target_trades) or any(rec['ownedDeltas'].get(m,0)!=0 for m in own_target_balances))
 if mixed_target_fee:
  unallocated.append({'signature':sig,'utc':ts(tx['blockTime']),'nativeWsolDeltaLamports':str(nw),'names':rec['names'],'kind':'mixed_fee_target_cash_unresolved','rawSource':rec['source']})
  for m in active:rows[m]['multiLaunchTransactions'].append(sig)
  fee_op=False
 if fee_op:
  fee_operations.append({'signature':sig,'utc':ts(tx['blockTime']),'names':rec['names'],'nativeWsolDeltaLamports':str(nw),'referencedWeekMints':sorted(referenced),'rawSource':rec['source']});wd['feeOperationCashDelta']+=nw
  for m in referenced:rows[m]['excludedFeeOperationSignatures'].append(sig)
  continue
 if len(active)>1:
  for m in active:rows[m]['multiLaunchTransactions'].append(sig)
  if nw:unallocated.append({'signature':sig,'utc':ts(tx['blockTime']),'nativeWsolDeltaLamports':str(nw),'names':rec['names'],'kind':'multi_launch_cash_ambiguous','rawSource':rec['source']})
 if not active:
  if nw:unallocated.append({'signature':sig,'utc':ts(tx['blockTime']),'nativeWsolDeltaLamports':str(nw),'names':rec['names'],'rawSource':rec['source']})
  continue
 # Cash can only be allocated to a launch when the transaction has one active launched asset.
 sole=next(iter(active)) if len(active)==1 and not mixed_target_fee else None
 for m in active:
  r=rows[m];tr=target_trades.get(m,[]);expected=0
  for t in tr:
   r['buyCount' if t['buy'] else 'sellCount']+=1;r['tokensBoughtRaw' if t['buy'] else 'tokensSoldRaw']+=t['token'];r['quoteBuyPrincipalRaw' if t['buy'] else 'quoteSellPrincipalRaw']+=t['quote'];r['quoteTradeFeesRaw']+=t['fees'];expected+=t['token']*(1 if t['buy'] else -1)
   if t.get('targetTransferFeeRaw'):r['targetTransferFeesWithheldRaw']=r.get('targetTransferFeesWithheldRaw',0)+t['targetTransferFeeRaw'];r['token2022TransferFeeConfig']=transfer_fee_configs[m]
   if t['buy'] and r['firstBuyUtc'] is None:r['firstBuyUtc']=ts(tx['blockTime'])
   if not t['buy']:r['lastSaleUtc']=ts(tx['blockTime'])
  r['tokensTransferredInRaw']+=transfers[m]['in'];r['tokensTransferredOutRaw']+=transfers[m]['out'];r['tokensBurnedRaw']+=burns[m];expected+=transfers[m]['in']-transfers[m]['out']-burns[m]
  observed=rec['ownedDeltas'].get(m,0);residual=observed-expected
  if residual:
   r['unexplainedTargetDeltaRaw']+=residual;r['unknownInventoryTransactions'].append({'signature':sig,'observedDeltaRaw':str(observed),'expectedDeltaRaw':str(expected),'residualRaw':str(residual),'names':rec['names']})
  for a,b in rec['balances'].items():
   if b['mint']==m and b['owner']==W:
    z=r['inventoryAccounts'].setdefault(a,{'firstObservedPreRaw':str(b['pre']),'lastObservedPostRaw':str(b['post']),'lastObservedSignature':sig,'lastObservedUtc':ts(tx['blockTime'])});z.update(lastObservedPostRaw=str(b['post']),lastObservedSignature=sig,lastObservedUtc=ts(tx['blockTime']))
  if m!=sole:continue
  r['nativeWsolCashDeltaLamports']+=nw;r['ownerPaidNetworkFeesLamports']+=fee if payer==W else 0;r['targetAssociatedQuoteDeltaRaw']+=rec['ownedDeltas'].get(r['quoteMint'],0) if r['quoteMint']!=WSOL else 0
  creation=sig==r['creationSignature'];buy=any(t['buy'] for t in tr);sell=any(not t['buy'] for t in tr)
  kind='creation_and_buy' if creation and buy else 'creation' if creation else 'buy' if buy else 'sell' if sell else 'inventory_transfer' if transfers[m] else 'standalone_configuration_or_account_cost'
  if creation:r['creationNativeWsolDeltaLamports']+=nw
  if buy:r['nativeWsolBuyDebitsLamports']+=max(0,-nw)
  elif sell:r['nativeWsolSellReceiptsLamports']+=max(0,nw)
  elif not creation:r['nativeWsolStandaloneDeltaLamports']+=nw
  native_trans,creations,closes=D.extract_native_instructions(rec['ix'])
  r['nativeRentFundingLamports']+=sum(int(a['lamports']) for a in creations if a['source']==W)
  # closure refund = native lamports in closed account before tx; for WSOL subtract token principal.
  for c in closes:
   if c.get('destination')!=W or c.get('account') not in rec['keys']:continue
   idx=rec['keys'].index(c['account']);refund=tx['meta']['preBalances'][idx];b=rec['balances'].get(c['account'],{})
   if b.get('mint')==WSOL:refund-=b.get('pre',0)
   r['nativeAccountClosureRefundLamports']+=max(refund,0)
  r['nativeJitoTipLamports']+=sum(int(a['lamports']) for a in native_trans if a['source']==W and a['officialJitoTipAccount'])
  r['nativeExternalOuterTransfersLamports']+=sum(int(a['lamports']) for a in native_trans if a['source']==W and a['innerInstructionIndex'] is None)
  # Route funding is native wallet -> wallet's own recorded/initialized WSOL account in a buy tx.
  own_wsol={a for a,b in rec['balances'].items() if b['mint']==WSOL and b['owner']==W}
  for x in rec['ix']:
   p=x.get('parsed',{});inf=p.get('info',{}) if isinstance(p,dict) else {}
   if isinstance(p,dict) and p.get('type') in {'initializeAccount','initializeAccount2','initializeAccount3'} and inf.get('owner')==W and inf.get('mint')==WSOL:own_wsol.add(inf['account'])
  route=sum(int(a['lamports']) for a in native_trans if a['source']==W and a['destination'] in own_wsol)
  if buy and route:r['buyRouteNativeFundingLamports']+=route;r['buyRouteNativeFundingSignatures'].append(sig)
  r['economicTransactions'].append({'signature':sig,'utc':ts(tx['blockTime']),'kind':kind,'nativeWsolDeltaLamports':str(nw),'nativeDeltaLamports':str(rec['native']),'ownedWsolDeltaRaw':str(rec['ownedDeltas'].get(WSOL,0)),'targetDeltaRaw':str(observed),'quoteAssetDeltaRaw':str(rec['ownedDeltas'].get(r['quoteMint'],0)),'networkFeeLamports':str(fee if payer==W else 0),'names':rec['names'],'trades':[{'venue':t['venue'],'isBuy':t['buy'],'tokenRaw':str(t['token']),'quoteRaw':str(t['quote']),'venueFeesRaw':str(t['fees']),'actualQuoteTransferRaw':str(t.get('actualQuoteTransferRaw',t['quote']+t['fees'] if t['buy'] else t['quote']-t['fees'])),'actualQuoteTransferWitness':t.get('actualQuoteTransferWitness'),'eventWitness':t['event']} for t in tr],'rawSource':rec['source']})
# Finalize quantities and bounded classifications; creator claim income remains separate.
for r in rows.values():
 remaining=sum(int(z['lastObservedPostRaw']) for z in r['inventoryAccounts'].values());opening=sum(int(z['firstObservedPreRaw']) for z in r['inventoryAccounts'].values());ledger=opening+r['tokensBoughtRaw']+r['tokensTransferredInRaw']-r['tokensSoldRaw']-r['tokensTransferredOutRaw']-r['tokensBurnedRaw']+r['unexplainedTargetDeltaRaw'];r['openingObservedTargetRaw']=opening;r['lastObservedInventoryRaw']=remaining;r['inventoryLedgerExpectedRaw']=ledger;r['inventoryLedgerMatchesLastObserved']=ledger==remaining
 r['cashResultSol']=sol(r['nativeWsolCashDeltaLamports']);r['buyNativeCashDebitSol']=sol(r['nativeWsolBuyDebitsLamports']);r['sellNativeCashReceiptsSol']=sol(r['nativeWsolSellReceiptsLamports']);r['failedNetworkFeesSol']=sol(r['failedNetworkFeesLamports']);r['buyRouteNativeFundingSol']=sol(r['buyRouteNativeFundingLamports'])
 r['quoteBuyPrincipalUnits']=D.units(r['quoteBuyPrincipalRaw'],r['quoteDecimals']) if r['quoteDecimals'] is not None else None;r['quoteSellPrincipalUnits']=D.units(r['quoteSellPrincipalRaw'],r['quoteDecimals']) if r['quoteDecimals'] is not None else None
 if r['multiLaunchTransactions'] or r['unknownInventoryTransactions'] or not r['inventoryLedgerMatchesLastObserved']:status='unresolved_inventory_or_cash_allocation'
 elif r['tokensTransferredOutRaw']:status='inventory_transferred_out_operator_result_unresolved'
 elif remaining:status='remaining_inventory_in_last_observation'
 elif not r['buyCount']:status='no_original_wallet_acquisition_observed'
 elif r['quoteMint']!=WSOL and r['targetAssociatedQuoteDeltaRaw']!=0:status='target_closed_other_quote_inventory_change'
 elif r['tokensBoughtRaw']==r['tokensSoldRaw'] and r['tokensBoughtRaw']>0 and r['tokensTransferredInRaw']==0:status='bounded_closed_original_wallet_position'
 else:status='target_zero_inventory_but_basis_unresolved'
 r['positionStatus']=status;r['observedCashDirection']='positive' if r['nativeWsolCashDeltaLamports']>0 else 'negative' if r['nativeWsolCashDeltaLamports']<0 else 'zero';r['boundedCashOutcome']=('win' if r['nativeWsolCashDeltaLamports']>0 else 'loss' if r['nativeWsolCashDeltaLamports']<0 else 'flat') if status=='bounded_closed_original_wallet_position' else 'unresolved'
 r['secondsFromFirstBuyToLastSale']=int((datetime.datetime.fromisoformat(r['lastSaleUtc'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(r['firstBuyUtc'].replace('Z','+00:00'))).total_seconds()) if r['firstBuyUtc'] and r['lastSaleUtc'] else None
 for k,v in list(r.items()):
  if isinstance(v,int) and (k.endswith('Raw') or k.endswith('Lamports')):r[k]=str(v)

for r in rows.values():
 components=collections.Counter()
 for t in r['economicTransactions']:components[t['kind']]+=int(t['nativeWsolDeltaLamports'])
 r['cashComponentsLamports']={k:str(v) for k,v in components.items()}
 r['cashComponentSumMatches']=sum(components.values())==int(r['nativeWsolCashDeltaLamports'])
result={'generatedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'wallet':W,'windowStartUtc':D.utc(start),'windowEndExclusiveUtc':D.utc(cutoff),'coverage':{'centralizedPages':len(manifest['pages']),'walletReferencedTransactions':len(records),'successfulWalletReferences':sum(not r['failed'] for r in records),'retainedFailedReferences':sum(r['failed'] for r in records),'terminalSuccessfulHistory':manifest['terminal'],'failedHistoryComplete':False,'definition':'All available terminal successful direct-wallet history, with retained failed references only. Token-account-only transfers/current account snapshots are outside this capture.'},'launches':list(rows.values()),'excludedFeeOperations':fee_operations,'unallocatedSuccessfulCashTransactions':unallocated,'decoderErrors':errors,'records':[{'signature':r['sig'],'slot':r['tx']['slot'],'transactionIndex':r['tx'].get('transactionIndex'),'utc':D.utc(r['tx']['blockTime']),'failed':r['failed'],'nativeLamports':str(r['native']),'ownedWsolDeltaRaw':str(r['ownedDeltas'].get(WSOL,0)),'networkFeeLamports':str(r['tx']['meta']['fee'] if r['keys'][0]==W else 0),'names':r['names'],'rawSource':r['source']} for r in records]}
(WORK/'capital-ledger.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'launches':len(rows),'records':len(records),'successful':result['coverage']['successfulWalletReferences'],'errors':len(errors),'positions':dict(collections.Counter(r['positionStatus'] for r in rows.values()))},indent=2))
