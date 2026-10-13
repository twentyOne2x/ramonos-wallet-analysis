import os,pathlib,json,hashlib,collections,functools,csv,datetime
ROOT=pathlib.Path(os.environ.get('RAMONOS_RESEARCH_ROOT', pathlib.Path.cwd())).resolve()
BASE=ROOT/'outputs/ramonos-launches-20261013';OUT=BASE/'costs-coverage';OUT.mkdir(exist_ok=True)
W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
def key(k):return k.get('pubkey') if isinstance(k,dict) else k
def flat(tx):
 yield from tx['transaction']['message'].get('instructions',[])
 for g in tx['meta'].get('innerInstructions') or []:yield from g.get('instructions',[])
@functools.lru_cache(None)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
launches=json.loads((BASE/'census/launches.json').read_text());mints={x['mint'] for x in launches};launchs={x['signature'] for x in launches}
sources=[];success={};account_mints=collections.defaultdict(set)
for p in sorted((BASE/'census/raw').glob('page-*.json')):
 if p.name.endswith('.request.json'):continue
 sources.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p)})
 for tx in json.loads(p.read_text())['result']['data']:
  keys=[key(k) for k in tx['transaction']['message']['accountKeys']];sig=tx['transaction']['signatures'][0];success[sig]=(tx,p)
  for b in (tx['meta'].get('preTokenBalances') or [])+(tx['meta'].get('postTokenBalances') or []):
   if b.get('mint') in mints:account_mints[keys[b['accountIndex']]].add(b['mint'])
def witnesses(tx):
 out=[]
 for n,ix in enumerate(flat(tx)):
  accounts=set(ix.get('accounts') or [])
  parsed=ix.get('parsed',{});info=parsed.get('info',{}) if isinstance(parsed,dict) else {}
  accounts.update(v for v in info.values() if isinstance(v,str))
  hits=accounts&mints;via=set()
  for a in accounts:via.update(account_mints.get(a,set()))
  if hits or via:out.append({'flattenedInstructionIndex':n,'programId':ix.get('programId'),'directMints':sorted(hits),'knownTokenAccountMints':sorted(via)})
 return out
failed=[];seen=set();duplicates=[]
for p in sorted((OUT/'raw').glob('failed-page-*.json')):
 if p.name.endswith('.request.json'):continue
 sources.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p)})
 for tx in json.loads(p.read_text())['result']['data']:
  sig=tx['transaction']['signatures'][0]
  if sig in seen:duplicates.append(sig);continue
  seen.add(sig);keys=[key(k) for k in tx['transaction']['message']['accountKeys']];payer=keys[0];wi=keys.index(W);meta=tx['meta'];wit=witnesses(tx)
  scope='cohort-instruction-witness' if wit else ('cohort-key-reference-only' if set(keys)&mints else 'no-cohort-witness-unallocated')
  othermints=sorted({b['mint'] for b in (meta.get('preTokenBalances') or [])+(meta.get('postTokenBalances') or []) if b.get('mint') not in mints and b.get('mint')!='So11111111111111111111111111111111111111112'})
  failed.append({'signature':sig,'slot':tx['slot'],'blockTime':tx.get('blockTime'),'feePayer':payer,'walletPaysFee':payer==W,'networkFeeLamports':meta['fee'],'walletDeltaLamports':meta['postBalances'][wi]-meta['preBalances'][wi],'error':meta['err'],'scope':scope,'instructionWitnesses':wit,'otherTokenBalanceMints':othermints,'rawSource':str(p.relative_to(ROOT)),'rawSourceSha256':digest(p)})
(OUT/'failed-fee-ledger.json').write_text(json.dumps(failed,indent=2))
claimtx=json.loads((BASE/'own-fees/transactions.json').read_text());sources.append({'path':str((BASE/'own-fees/transactions.json').relative_to(ROOT)),'sha256':digest(BASE/'own-fees/transactions.json')})
def aggregate(rows):
 groups={}
 for scope in sorted({r['scope'] for r in rows}):
  rs=[r for r in rows if r['scope']==scope];ours=[r for r in rs if r['walletPaysFee']]
  groups[scope]={'transactionCount':len(rs),'walletFeePayerCount':len(ours),'walletPaidFeeLamports':sum(r['networkFeeLamports'] for r in ours),'walletDeltaLamports':sum(r['walletDeltaLamports'] for r in rs)}
 return groups
def successrow(tx,p,scope):
 keys=[key(k) for k in tx['transaction']['message']['accountKeys']];wi=keys.index(W);meta=tx['meta'];creates=[];closes=[];transfers=[]
 for n,ix in enumerate(flat(tx)):
  z=ix.get('parsed',{});info=z.get('info',{}) if isinstance(z,dict) else {};typ=z.get('type') if isinstance(z,dict) else None
  if typ in ('createAccount','createAccountWithSeed') and info.get('source')==W:creates.append({'flattenedInstructionIndex':n,**info})
  if typ=='closeAccount' and info.get('destination')==W:closes.append({'flattenedInstructionIndex':n,**info})
  if typ=='transfer' and ix.get('programId')=='11111111111111111111111111111111' and info.get('source')==W:transfers.append({'flattenedInstructionIndex':n,**info})
 return {'signature':tx['transaction']['signatures'][0],'slot':tx['slot'],'scope':scope,'feePayer':keys[0],'walletPaysFee':keys[0]==W,'networkFeeLamports':meta['fee'],'walletDeltaLamports':meta['postBalances'][wi]-meta['preBalances'][wi],'walletFundedCreates':creates,'walletDestinationCloses':closes,'walletNativeTransfers':transfers,'rawSource':str(p.relative_to(ROOT)),'rawSourceSha256':digest(p)}
rows=[]
for sig,(tx,p) in success.items():
 if sig in launchs:rows.append(successrow(tx,p,'signed-launch'))
 if sig in claimtx:rows.append(successrow(tx,p,'creator-fee-claim'))
(OUT/'successful-cost-witnesses.json').write_text(json.dumps(rows,indent=2))
summary={'wallet':W,'cutoffUtc':json.loads((BASE/'census/config.json').read_text())['cutoffUtc'],'failedManifest':json.loads((OUT/'failed-history-manifest.json').read_text()),'failedUniqueCount':len(failed),'duplicateSignatures':duplicates,'failedFeeGroups':aggregate(failed),'successCostGroups':aggregate(rows),'launchClaimOverlap':sorted(launchs&set(claimtx)),'walletFundedCreateLamportsOnLaunchTx':sum(c.get('lamports',0) for r in rows if r['scope']=='signed-launch' for c in r['walletFundedCreates']),'limitations':['Failed fee attribution uses explicit instruction mint/account witness; no witness is unallocated, not proven irrelevant.','An attempted cohort instruction may occur after the failing instruction; fee allocation is transaction purpose evidence, not executed trade.','Rent/create-account deposits are capital/custody outflow until release or proven unrecoverable; do not call all deposit principal expense.','Successful wallet deltas already include transaction fees, tips, setup deposits, refunds and other transfers. Subtracting these again double-counts.','tokenAccounts none is terminal direct-wallet references, not arbitrary lifetime associated-account coverage.']}
summary['failedUnexpectedWalletCashResiduals']=[r['signature'] for r in failed if r['walletDeltaLamports']!=(-r['networkFeeLamports'] if r['walletPaysFee'] else 0)]
for label,rs in [('unallocatedWithOtherTokenBalanceWitness',[r for r in failed if r['scope']=='no-cohort-witness-unallocated' and r['otherTokenBalanceMints']]),('unallocatedWithoutOtherTokenBalanceWitness',[r for r in failed if r['scope']=='no-cohort-witness-unallocated' and not r['otherTokenBalanceMints']])]:
 summary[label]={'transactions':len(rs),'walletPaidFeesLamports':sum(r['networkFeeLamports'] for r in rs if r['walletPaysFee']),'walletFeePayerCount':sum(r['walletPaysFee'] for r in rs)}
tp=BASE/'trading/capital-ledger.json'
if tp.exists():
 t=json.loads(tp.read_text());trade={z['signature'] for l in t['launches'] for z in l.get('economicTransactions',[])};overlap=trade&set(claimtx)
 summary['tradeClaimOverlap']=sorted(overlap);summary['tradeNetworkFeesLamports']=sum(success[s][0]['meta']['fee'] for s in trade if s in success and key(success[s][0]['transaction']['message']['accountKeys'][0])==W)
 summary['tradeSignatureCount']=len(trade);sources.append({'path':str(tp.relative_to(ROOT)),'sha256':digest(tp)})
 receipts=json.loads((BASE/'own-fees/verified-receipts.json').read_text());positive={r['signature'] for r in receipts if r.get('verified') and r.get('asset') in ('SOL','WSOL') and int(r.get('amountRaw',r.get('amountLamports',0)))>0}
 def feecount(sigs):return {'transactionCount':len(sigs),'walletFeePayerCount':sum(key(claimtx[s]['transaction']['message']['accountKeys'][0])==W for s in sigs),'walletPaidFeeLamports':sum(claimtx[s]['meta']['fee'] for s in sigs if key(claimtx[s]['transaction']['message']['accountKeys'][0])==W)}
 summary['additionalPositiveSolClaimFees']=feecount(positive-trade)
 summary['positiveSolClaimFees']=feecount(positive)
 summary['additionalAllClaimFees']=feecount(set(claimtx)-trade)
 summary['tradeClaimOverlapPayoutLamports']=sum(int(r.get('amountLamports',0)) for r in receipts if r['signature'] in overlap and r.get('verified') and r.get('asset') in ('SOL','WSOL'))
 permint=collections.defaultdict(lambda:{'transactionCount':0,'walletPaidFeeLamports':0,'signatures':[]});mixed=[]
 for r in failed:
  if not r['walletPaysFee'] or r['scope']!='cohort-instruction-witness':continue
  hits={m for z in r['instructionWitnesses'] for m in z['directMints']+z['knownTokenAccountMints']}
  if len(hits)!=1:mixed.append({'signature':r['signature'],'mints':sorted(hits),'walletPaidFeeLamports':r['networkFeeLamports']});continue
  d=permint[next(iter(hits))];d['transactionCount']+=1;d['walletPaidFeeLamports']+=r['networkFeeLamports'];d['signatures'].append(r['signature'])
 summary['perMintFailedFeeAmbiguousTransactions']=mixed
 (OUT/'per-mint-failed-fees.json').write_text(json.dumps(dict(permint),indent=2))
 summary['soleMintFailedFeesLamports']=sum(x['walletPaidFeeLamports'] for x in permint.values())
 summary['multiMintFailedFeesLamports']=sum(x['walletPaidFeeLamports'] for x in mixed)
 groups=collections.defaultdict(lambda:{'mints':0,'failedFeesLamports':0,'failedTransactions':0})
 for l in t['launches']:
  d=groups[l['positionStatus']];d['mints']+=1;z=permint.get(l['mint'],{});d['failedFeesLamports']+=z.get('walletPaidFeeLamports',0);d['failedTransactions']+=z.get('transactionCount',0)
 summary['failedFeesByTradingPositionStatus']=dict(groups)
 solquote=[l for l in t['launches'] if l['quoteMint']=='So11111111111111111111111111111111111111112']
 summary['solQuoteCohortMints']=len(solquote)
 summary['solQuoteCohortFailedFeesLamports']=sum(permint.get(l['mint'],{}).get('walletPaidFeeLamports',0) for l in solquote)
 status_by_mint={l['mint']:l['positionStatus'] for l in t['launches']}
 with (OUT/'failed-cohort-fees.csv').open('w',newline='') as handle:
  writer=csv.DictWriter(handle,fieldnames=['signature','utc','blockTime','mint','positionStatus','feeLamports','feeSol','rawSource','rawSourceSha256']);writer.writeheader()
  for r in failed:
   if not r['walletPaysFee'] or r['scope']!='cohort-instruction-witness':continue
   hits={m for z in r['instructionWitnesses'] for m in z['directMints']+z['knownTokenAccountMints']};mint=next(iter(hits)) if len(hits)==1 else ''
   writer.writerow({'signature':r['signature'],'utc':datetime.datetime.fromtimestamp(r['blockTime'],datetime.timezone.utc).isoformat().replace('+00:00','Z'),'blockTime':r['blockTime'],'mint':mint,'positionStatus':status_by_mint.get(mint,'multi_mint_unallocated'),'feeLamports':r['networkFeeLamports'],'feeSol':f"{r['networkFeeLamports']/1e9:.9f}",'rawSource':r['rawSource'],'rawSourceSha256':r['rawSourceSha256']})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'source-manifest.json').write_text(json.dumps(sources,indent=2))
print(json.dumps({k:v for k,v in summary.items() if k!='failedManifest'},indent=2))
