import os,pathlib,json,collections,hashlib,csv,datetime
ROOT=pathlib.Path(os.environ.get('RAMONOS_RESEARCH_ROOT', pathlib.Path.cwd())).resolve();BASE=ROOT/'outputs/ramonos-launches-20261013';OUT=BASE/'costs-coverage'
W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b';WSOL='So11111111111111111111111111111111111111112';SYSTEM='11111111111111111111111111111111'
def key(k):return k.get('pubkey') if isinstance(k,dict) else k
def flat(tx):
 for n,ix in enumerate(tx['transaction']['message'].get('instructions',[])):yield n,None,ix
 for g in tx['meta'].get('innerInstructions') or []:
  for n,ix in enumerate(g.get('instructions',[])):yield g['index'],n,ix
txs=json.loads((BASE/'own-fees/transactions.json').read_text());tips=set(json.loads((BASE/'trading/inputs/jito-tip-accounts.json').read_text())['result']);rows=[];transfers=[]
for sig,t in txs.items():
 keys=[key(k) for k in t['transaction']['message']['accountKeys']];meta=t['meta'];wi=keys.index(W);accounts={};ws=[0,0]
 for side,k in enumerate(['preTokenBalances','postTokenBalances']):
  for b in meta.get(k) or []:
   addr=keys[b['accountIndex']];accounts[addr]={'owner':b.get('owner'),'mint':b['mint'],'evidence':k}
   if b.get('owner')==W and b['mint']==WSOL:ws[side]+=int(b['uiTokenAmount']['amount'])
 for oi,ii,ix in flat(t):
  p=ix.get('parsed',{});a=p.get('info',{}) if isinstance(p,dict) else {}
  if p.get('type') in ('initializeAccount','initializeAccount2','initializeAccount3') and a.get('account'):accounts[a['account']]={'owner':a.get('owner'),'mint':a.get('mint'),'evidence':'parsed '+p['type']}
  if ix.get('program')=='spl-associated-token-account' and a.get('account') and a.get('wallet'):accounts[a['account']]={'owner':a['wallet'],'mint':a.get('mint'),'evidence':'parsed associated create'}
 native=meta['postBalances'][wi]-meta['preBalances'][wi];new=[];creates=[]
 for oi,ii,ix in flat(t):
  p=ix.get('parsed',{});a=p.get('info',{}) if isinstance(p,dict) else {}
  if p.get('type') in ('createAccount','createAccountWithSeed') and a.get('source')==W:creates.append({'outerInstructionIndex':oi,'innerInstructionIndex':ii,**a})
  if ix.get('programId')!=SYSTEM or p.get('type')!='transfer' or a.get('source')!=W:continue
  d=a['destination'];proof=accounts.get(d);category='official-jito-tip' if d in tips else ('wallet-owned-wsol-internal-wrap' if proof and proof.get('owner')==W and proof.get('mint')==WSOL else ('wallet-owned-other-token-account-funding' if proof and proof.get('owner')==W else 'external-destination-purpose-and-beneficial-owner-unproved'))
  row={'signature':sig,'blockTime':t.get('blockTime'),'outerInstructionIndex':oi,'innerInstructionIndex':ii,'destination':d,'lamports':a['lamports'],'category':category,'tokenOwnershipWitness':proof,'outer':ii is None};new.append(row);transfers.append(row)
 rows.append({'signature':sig,'blockTime':t.get('blockTime'),'walletNativeDeltaLamports':native,'walletOwnedWsolDeltaRaw':ws[1]-ws[0],'walletNativeOwnedWsolDeltaLamports':native+ws[1]-ws[0],'walletPaidFeeLamports':meta['fee'] if keys[0]==W else 0,'walletFundedCreates':creates,'outgoingSystemTransfers':new})
groups={}
for category in sorted({r['category'] for r in transfers}):
 rs=[r for r in transfers if r['category']==category];groups[category]={'transferCount':len(rs),'allTransfersLamports':sum(r['lamports'] for r in rs),'outerTransferCount':sum(r['outer'] for r in rs),'outerTransfersLamports':sum(r['lamports'] for r in rs if r['outer']),'distinctDestinations':len({r['destination'] for r in rs})}
summary={'transactions':len(rows),'outgoingTransferClassification':groups,'walletNativeDeltaLamports':sum(r['walletNativeDeltaLamports'] for r in rows),'walletOwnedWsolDeltaRaw':sum(r['walletOwnedWsolDeltaRaw'] for r in rows),'walletNativeOwnedWsolDeltaLamports':sum(r['walletNativeOwnedWsolDeltaLamports'] for r in rows),'walletFundedCreateLamports':sum(a.get('lamports',0) for r in rows for a in r['walletFundedCreates']),'walletPaidFeeLamports':sum(r['walletPaidFeeLamports'] for r in rows),'grossSolEquivalentPayoutLamports':1660286830500,'grossPayoutMinusWalletNativeOwnedWsolDeltaLamports':1660286830500-sum(r['walletNativeOwnedWsolDeltaLamports'] for r in rows),'limitations':['External destination is not proof of third-party beneficial ownership or service expense.','Rent deposits and released rent require custody lots, not blanket expense treatment.','Cash across these transactions includes zero-distribution launch/configuration operations and other legs.','Pre/post token ownership plus parsed initialization identifies internal WSOL wraps even if account is initialized and closed within one transaction.']}
receipts=json.loads((BASE/'own-fees/verified-receipts.json').read_text());positive={r['signature'] for r in receipts if r.get('verified') and r.get('asset') in ('SOL','WSOL') and int(r.get('amountRaw',r.get('amountLamports',0)))>0};trading=json.loads((BASE/'trading/capital-ledger.json').read_text());trade={r['signature'] for l in trading['launches'] for r in l['economicTransactions']}
for label,selected in [('positiveSolPayoutTransactions',positive),('allClaimTransactionsExcludingAllocatedTrade',set(txs)-trade)]:
 rr=[r for r in rows if r['signature'] in selected];summary[label]={'transactions':len(rr),'walletNativeOwnedWsolDeltaLamports':sum(r['walletNativeOwnedWsolDeltaLamports'] for r in rr),'walletPaidFeeLamports':sum(r['walletPaidFeeLamports'] for r in rr),'officialJitoTipLamports':sum(z['lamports'] for r in rr for z in r['outgoingSystemTransfers'] if z['category']=='official-jito-tip'),'signatureSet':sorted(selected)}
native=json.loads((BASE/'own-fees/cash-ledgers.json').read_text());movement=collections.Counter()
for s,r in native.items():
 for v in r['nativeTransfers']:
  if v.get('destination')==W:movement['in_'+v['type']]+=int(v['amount'])
  if v.get('source')==W:movement['out_'+v['type']]+=int(v['amount'])
summary['reconstructedNativeMovementsLamports']=dict(movement)
summary['reconstructedNativeLedgerMatchesAll']=all(x['walletCashLedgerMatches'] for x in native.values())
summary['sourceHashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BASE/'own-fees/transactions.json',BASE/'own-fees/cash-ledgers.json',BASE/'own-fees/verified-receipts.json',BASE/'trading/inputs/jito-tip-accounts.json',BASE/'trading/capital-ledger.json']}
with (OUT/'claim-native-wsol-cash.csv').open('w',newline='') as h:
 writer=csv.DictWriter(h,fieldnames=['signature','utc','blockTime','walletNativeDeltaLamports','walletOwnedWsolDeltaRaw','walletNativeOwnedWsolDeltaLamports','walletPaidFeeLamports','officialJitoTipLamports','positiveSolPayout','includedStandaloneExcludesTradeOverlap']);writer.writeheader()
 for r in rows:writer.writerow({**{k:r[k] for k in ['signature','blockTime','walletNativeDeltaLamports','walletOwnedWsolDeltaRaw','walletNativeOwnedWsolDeltaLamports','walletPaidFeeLamports']},'utc':datetime.datetime.fromtimestamp(r['blockTime'],datetime.timezone.utc).isoformat().replace('+00:00','Z'),'officialJitoTipLamports':sum(z['lamports'] for z in r['outgoingSystemTransfers'] if z['category']=='official-jito-tip'),'positiveSolPayout':r['signature'] in positive,'includedStandaloneExcludesTradeOverlap':r['signature'] not in trade})
(OUT/'claim-cash-ledger.json').write_text(json.dumps(rows,indent=2));(OUT/'claim-transfer-classification.json').write_text(json.dumps(transfers,indent=2));(OUT/'claim-cash-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
