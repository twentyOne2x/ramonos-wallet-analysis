import json,sys,pathlib,hashlib,decimal
ROOT=pathlib.Path(__file__).resolve().parents[2]
INPUT=pathlib.Path(__file__).resolve().parent/'input';OUT=pathlib.Path(__file__).resolve().parent/'evaluation-output';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'))
import fee_core as F
W=json.load(open(INPUT/'wallet-transactions.json'))['wallet'];rows=[];txrows=[];errors=[];seen=set()
for filename in ['wallet-transactions.json','github-social-transactions.json']:
 path=INPUT/filename;payload=json.load(open(path));txs=payload.get('transactions',payload.get('result',{}).get('data',[]))
 for tx in txs:
  sig=tx['transaction']['signatures'][0]
  if sig in seen:continue
  seen.add(sig);assert tx['meta']['err'] is None
  keys=[F.key(k) for k in tx['transaction']['message']['accountKeys']];ixs=F.D.flatten_instructions(tx);es=F.events(tx,filename,errors)
  txrows.append({'signature':sig,'slot':tx['slot'],'utc':F.utc(tx['blockTime']),'input':filename,'netNativeWalletLamports':tx['meta']['postBalances'][keys.index(W)]-tx['meta']['preBalances'][keys.index(W)],'txFeeLamports':tx['meta']['fee']})
  for e in es:
   if e['name'] not in ['CollectCreatorFeeEvent','CollectCoinCreatorFeeEvent']:continue
   v=e['event'];amm=e['name']=='CollectCoinCreatorFeeEvent';amount=int(v['coin_creator_fee' if amm else 'creator_fee']);matches=[]
   for ix in ixs:
    p=ix.get('parsed',{});inf=p.get('info',{});ta=inf.get('tokenAmount',{})
    if ix['parentProgram']!=e['program']:continue
    if not amm and p.get('type')=='transfer' and inf.get('destination')==W and int(inf.get('lamports',-1))==amount:matches.append((ix,inf,'11111111111111111111111111111111',9,W))
    if p.get('type')=='transferChecked' and int(ta.get('amount',-1))==amount:
     dest=inf['destination'];owner=None
     for tb in tx['meta'].get('postTokenBalances',[])+tx['meta'].get('preTokenBalances',[]):
      if keys[tb['accountIndex']]==dest:owner=tb.get('owner')
     for qi in ixs:
      q=qi.get('parsed',{});qiinfo=q.get('info',{})
      if q.get('type')=='initializeAccount3' and qiinfo.get('account')==dest:owner=qiinfo.get('owner')
     if owner==W and (not amm or (dest==v['coin_creator_token_account'] and inf['source']==v['coin_creator_vault_ata'])):matches.append((ix,inf,inf['mint'],int(ta['decimals']),owner))
   assert len(matches)==1,(sig,e['name'],matches)
   ix,inf,mint,dec,owner=matches[0]
   if 'quote_mint' in v:assert v['quote_mint']==mint
   if mint==F.WSOL:
    assert dec==9
    assert any(q.get('parsed',{}).get('type')=='closeAccount' and q['parsed']['info'].get('account')==inf['destination'] and q['parsed']['info'].get('destination')==W for q in ixs)
    sourceidx=keys.index(inf['source']);pre=next(t for t in tx['meta']['preTokenBalances'] if t['accountIndex']==sourceidx);post=next(t for t in tx['meta']['postTokenBalances'] if t['accountIndex']==sourceidx)
    assert int(pre['uiTokenAmount']['amount'])-int(post['uiTokenAmount']['amount'])==amount
   if mint==F.SOL:assert tx['meta']['preBalances'][keys.index(inf['source'])]-tx['meta']['postBalances'][keys.index(inf['source'])]==amount
   rows.append({'signature':sig,'slot':tx['slot'],'utc':F.utc(tx['blockTime']),'input':filename,'rawSourceSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'event':e['name'],'eventPayloadSha256':e['payloadSha256'],'missingTrailingFields':e['missingTrailingFields'],'program':e['program'],'outerInstruction':ix['topLevelInstructionIndex'],'innerInstruction':ix['innerInstructionIndex'],'source':inf['source'],'destination':inf['destination'],'destinationOwner':owner,'mint':mint,'rawAmount':amount,'decimals':dec,'amount':F.D.units(amount,dec),'unwrappedIntoWallet':mint==F.WSOL})
assert not errors
sums={}
for row in rows:sums[row['mint']]=sums.get(row['mint'],0)+row['rawAmount']
summary={'disclosedWallet':W,'transactions':len(txrows),'nativeSOLRaw':sums[F.SOL],'WSOLRaw':sums[F.WSOL],'grossSOLEquivalentRaw':sums[F.SOL]+sums[F.WSOL],'grossSOLEquivalent':F.D.units(sums[F.SOL]+sums[F.WSOL],9),'assets':sums,'netNativeWalletCashRaw':sum(t['netNativeWalletLamports'] for t in txrows),'txFeesRaw':sum(t['txFeeLamports'] for t in txrows),'scope':'Selected supplied successful transactions, not lifetime history','decodingErrors':errors}
for subset in ['wallet-transactions.json','github-social-transactions.json']:
 sr=[r for r in rows if r['input']==subset and r['mint'] in [F.SOL,F.WSOL]]
 summary[subset+'GrossSOLEquivalent']=F.D.units(sum(r['rawAmount'] for r in sr),9)
json.dump({'summary':summary,'receipts':rows,'transactions':txrows},open(OUT/'receipt-ledger.json','w'),indent=2)
print(json.dumps(summary,indent=2))
