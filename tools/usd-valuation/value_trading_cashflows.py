#!/usr/bin/env python3
"""Price finalized signed native-SOL/WSOL cash components by their own minute."""
import argparse,csv,decimal,hashlib,json,pathlib
from value_receipts import retrieve_prices,stamp
D=decimal.Decimal
SOL='So11111111111111111111111111111111111111112'

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ledger',required=True);ap.add_argument('--cashflows');ap.add_argument('--output',required=True);ap.add_argument('--offline',action='store_true');ap.add_argument('--failed-fees');ap.add_argument('--claim-network-fees');a=ap.parse_args()
 out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True);ledgerpath=pathlib.Path(a.ledger);ledger=json.loads(ledgerpath.read_text());launches={x['mint']:x for x in ledger['launches']}
 if a.cashflows:rows=list(csv.DictReader(open(a.cashflows)))
 else:
  rows=[{'mint':l['mint'],'signature':t['signature'],'utc':t['utc'],'kind':t['kind'],'nativeWsolDeltaLamports':t['nativeWsolDeltaLamports']} for l in launches.values() for t in l['economicTransactions']]
 seen=set();full={};totalByMint={};times=[]
 for r in rows:
  mint=r.get('mint',r.get('launchMint'));r['mint']=mint
  if mint not in launches:raise ValueError('Unknown source launch '+str(mint))
  key=(mint,r['signature'],r['kind'])
  if key in seen:raise ValueError('Duplicate exact cash component '+str(key))
  seen.add(key)
  if r['kind']!='exact_target_ata_reserve_refund_component':
   if r['signature'] in full:raise ValueError('Repeated whole-transaction cash allocation '+r['signature'])
   full[r['signature']]=key
  r['signedSolEquivalent']=str(D(r['nativeWsolDeltaLamports'])/D(10**9));totalByMint[mint]=totalByMint.get(mint,0)+int(r['nativeWsolDeltaLamports']);times.append(stamp(r['utc']))
 for mint,l in launches.items():
  if totalByMint.get(mint,0)!=int(l['nativeWsolCashDeltaLamports']):raise ValueError('Cash component/source total mismatch '+mint)
 successRows=len(rows)
 failedRows=[]
 if a.failed_fees:
  failedRows=list(csv.DictReader(open(a.failed_fees)))
  if len({r['signature'] for r in failedRows})!=len(failedRows):raise ValueError('Repeated failed fee signature')
  for f in failedRows:
   if f['signature'] in full:raise ValueError('Failed/successful signature overlap')
   r={'mint':f['mint'],'signature':f['signature'],'utc':f['utc'],'kind':'failed_network_fee','nativeWsolDeltaLamports':str(-int(f['feeLamports'])),'signedSolEquivalent':str(-D(f['feeLamports'])/D(10**9))};rows.append(r);times.append(stamp(r['utc']))
 claimRows=list(csv.DictReader(open(a.claim_network_fees))) if a.claim_network_fees else []
 if len({r['signature'] for r in claimRows})!=len(claimRows):raise ValueError('Repeated claim fee signature')
 if any(r['signature'] in full for r in claimRows):raise ValueError('Claim fee already inside successful cash delta')
 times += [stamp(r['utc']) for r in claimRows]
 prices=retrieve_prices(times,out/'raw',a.offline)
 sums={};valued=[]
 for r in rows:
  l=launches[r['mint']];t=stamp(r['utc']);c=prices[t//60*60];amt=D(r['signedSolEquivalent']);usd=amt*c['close'];lo=amt*(c['low'] if amt>=0 else c['high']);hi=amt*(c['high'] if amt>=0 else c['low'])
  v={**r,'name':l['name'],'quoteMint':l['quoteMint'],'positionStatus':l['positionStatus'],'priceMinuteUTC':c['minuteUTC'],'solUsdMinuteClose':str(c['close']),'usdSignedCashflow':str(usd),'usdLowSensitivity':str(lo),'usdHighSensitivity':str(hi),'priceRawSource':c['rawSource']};valued.append(v)
  z=sums.setdefault(l['mint'],{'mint':l['mint'],'name':l['name'],'quoteMint':l['quoteMint'],'positionStatus':l['positionStatus'],'cashSol':D(0),'cashUsd':D(0),'debitsUsd':D(0),'creditsUsd':D(0),'cashUsdLow':D(0),'cashUsdHigh':D(0),'cashComponents':0})
  z['cashSol']+=amt;z['cashUsd']+=usd;z['cashUsdLow']+=lo;z['cashUsdHigh']+=hi;z['cashComponents']+=1;z['debitsUsd']+=min(usd,D(0));z['creditsUsd']+=max(usd,D(0))
 for mint,l in launches.items():
  if mint not in sums:sums[mint]={'mint':mint,'name':l['name'],'quoteMint':l['quoteMint'],'positionStatus':l['positionStatus'],'cashSol':D(0),'cashUsd':D(0),'debitsUsd':D(0),'creditsUsd':D(0),'cashUsdLow':D(0),'cashUsdHigh':D(0),'cashComponents':0}
 def write(name,data):
  with (out/name).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 write('trading-cashflows-valued-usd.csv',valued);write('trading-launches-valued-usd.csv',list(sums.values()))
 cohorts={'closed_native_sol_quote':[s for s in sums.values() if s['quoteMint']==SOL and s['positionStatus']=='bounded_closed_original_wallet_position'],'all_native_sol_quote_cash_only':[s for s in sums.values() if s['quoteMint']==SOL],'all_cohort_sol_cash_only':list(sums.values())}
 result={}
 for key,co in cohorts.items():
  result[key]={'launches':len(co),'components':sum(x['cashComponents'] for x in co),'cashSol':str(sum((x['cashSol'] for x in co),D(0))),'cashUsd':str(sum((x['cashUsd'] for x in co),D(0))),'debitsUsd':str(sum((x['debitsUsd'] for x in co),D(0))),'creditsUsd':str(sum((x['creditsUsd'] for x in co),D(0))),'cashUsdLowSensitivity':str(sum((x['cashUsdLow'] for x in co),D(0))),'cashUsdHighSensitivity':str(sum((x['cashUsdHigh'] for x in co),D(0)))}
 summary={'sourceLedger':a.ledger,'sourceLedgerSha256':hashlib.sha256(ledgerpath.read_bytes()).hexdigest(),'sourceCashflows':a.cashflows,'sourceCashflowsSha256':hashlib.sha256(pathlib.Path(a.cashflows).read_bytes()).hexdigest() if a.cashflows else None,'priceSource':'Coinbase Exchange SOL-USD containing-minute candle close','componentCount':len(rows),'uniquePriceMinutes':len(prices),'cohorts':result,'limitations':['Signed native-SOL/WSOL wallet cash difference at each component timestamp, not actual USD proceeds or token-only trading profit.','All-cohort SOL cash includes launches with other quote assets and unresolved/transferred/remaining positions; not full USD profit.','Network fees already contained in signed transaction delta are not subtracted a second time. Exact allocated account-refund components retained per mint; repeated whole-transaction allocations are rejected.','This source covers successful captured history. Failed transaction costs are included only when explicitly allocated into these cash components by the source ledger; unavailable failed history stays unproved.','Buy-route funding is not added independently unless allocated into the source cash components; it can be an internal SOL/WSOL conversion.','Receipt-minute close may be after the receipt within its minute; low/high sensitivity is not a statistical or cross-exchange uncertainty bound.']}
 feeSummary=json.loads((out/'summary.json').read_text())
 claimValued=[]
 for r in claimRows:
  c=prices[stamp(r['utc'])//60*60];amount=-D(r['feeLamports'])/D(10**9);claimValued.append({**r,'solUsdMinuteClose':str(c['close']),'priceMinuteUTC':c['minuteUTC'],'usdSignedCashflow':str(amount*c['close']),'priceRawSource':c['rawSource']})
 if claimValued:write('additional-claim-network-fees-valued-usd.csv',claimValued)
 claimUsd=sum((D(r['usdSignedCashflow']) for r in claimValued),D(0));claimSol=sum((-D(r['feeLamports'])/D(10**9) for r in claimRows),D(0))
 closed=result['closed_native_sol_quote'];summary['successfulCashComponentCount']=successRows;summary['failedFeeComponentCount']=len(failedRows)
 summary['failedFeesSource']=a.failed_fees;summary['failedFeesSha256']=hashlib.sha256(pathlib.Path(a.failed_fees).read_bytes()).hexdigest() if a.failed_fees else None
 summary['additionalClaimFeeSource']=a.claim_network_fees;summary['additionalClaimFeeSha256']=hashlib.sha256(pathlib.Path(a.claim_network_fees).read_bytes()).hexdigest() if a.claim_network_fees else None
 summary['additionalClaimNetworkFeesSol']=str(-claimSol);summary['additionalClaimNetworkFeesUsd']=str(-claimUsd)
 summary['knownNetCoreHistoricalUsd']=str(D(closed['cashUsd'])+D(feeSummary['historicalUsdMarketValue'])+claimUsd)
 summary['knownNetCoreSol']=str(D(closed['cashSol'])+D(feeSummary['solEquivalent'])+claimSol)
 summary['sameKnownNetCoreSolAtFrozenCurrentSpotUsd']=str(D(summary['knownNetCoreSol'])*D(feeSummary['currentSolUsdSpot']))
 summary['grossFeePlusClosedCashNetworkOnlyProxyCaution']='This optional proxy deducts only extra claim network fees from gross fees and omits the claim transaction wallet outflows accounted for in combined-account-cash-summary-usd.json. Do not report it as account cash surplus or complete net profit.'
 summary['knownNetCoreDefinition']=str(closed['launches'])+' bounded-closed native-SOL quote position signed cashflows including allocated failed transaction fees, plus all verified SOL/WSOL creator-fee receipts, minus additional owner-paid claim network fees once. Historical USD is summed at each individual component timestamp.'
 (out/'trading-summary-usd.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
