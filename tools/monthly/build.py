"""Monthly frozen Ramonos audit: UTC cash timing and per-launch SOL buy-ins."""
import argparse,csv,collections,datetime,decimal,hashlib,json,pathlib
D=decimal.Decimal;SCALE=D(10**9);WSOL='So11111111111111111111111111111111111111112';CLOSED='bounded_closed_original_wallet_position'
def readcsv(p):
 with p.open() as f:return list(csv.DictReader(f))
def median(vals):
 a=sorted(vals);n=len(a)
 return None if not n else D(a[n//2]) if n%2 else (D(a[n//2-1])+D(a[n//2]))/2
def quantile(vals,q):
 a=sorted(vals)
 if not a:return None
 x=D(len(a)-1)*D(q);i=int(x);return D(a[i])+(D(a[min(i+1,len(a)-1)])-D(a[i]))*(x-i)
def sol(x):return None if x is None else str(D(x)/SCALE)
def stats(vals):
 return {'count':len(vals),'medianSol':sol(median(vals)),'meanSol':sol(D(sum(vals))/len(vals)) if vals else None,'p25Sol':sol(quantile(vals,'.25')),'p75Sol':sol(quantile(vals,'.75')),'minimumSol':sol(min(vals)) if vals else None,'maximumSol':sol(max(vals)) if vals else None,'totalSol':sol(sum(vals))}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=pathlib.Path,default=pathlib.Path.cwd());ap.add_argument('--output',type=pathlib.Path);a=ap.parse_args();root=a.source.resolve();base=root/'outputs/ramonos-launches-20261013';out=a.output or base/'monthly';out.mkdir(parents=True,exist_ok=True)
 paths={k:base/v for k,v in {'capital':'trading/capital-ledger.json','positions':'trading/positions.json','trades':'trading/trades.csv','cash':'trading/transactions.csv','failed':'costs-coverage/failed-cohort-fees.csv','claims':'costs-coverage/claim-native-wsol-cash.csv','receipts':'own-fees/receipts.csv','cutoff':'census/config.json','valuation':'usd-valuation/trading-cashflows-valued-usd.csv','feevaluation':'usd-valuation/monthly-valued-usd.csv'}.items()}
 positions=json.loads(paths['positions'].read_text());launches={r['mint']:r for r in positions};trades=readcsv(paths['trades']);cash=readcsv(paths['cash']);failed=readcsv(paths['failed']);claims=readcsv(paths['claims']);receipts=readcsv(paths['receipts']);config=json.loads(paths['cutoff'].read_text())
 chain={r['signature']:(r['slot'],r['transactionIndex']) for r in json.loads(paths['capital'].read_text())['records']};assert all(i is not None for _,i in chain.values())
 begin=min(r['createdUtc'][:7] for r in positions);end=config['cutoffUtc'][:7];months=[];year,mo=map(int,begin.split('-'))
 while f'{year:04}-{mo:02}'<=end:
  months.append(f'{year:04}-{mo:02}');mo+=1
  if mo==13:year+=1;mo=1
 ints=['launches','solQuoteLaunches','nonSolQuoteLaunches','positiveCreationBuyLaunches','zeroCreationBuyLaunches','closedSolLaunches','initialBuyTotalLamports','tradingNetCashLamports','closedTradingNetCashLamports','grossCreatorFeeLamports','standaloneClaimNetCashLamports','closedCohortLifetimeNetCashLamports']
 data={m:{'monthUTC':m,**{k:0 for k in ints}} for m in months};initial=collections.Counter();first={};closecohort=collections.Counter()
 for t in trades:
  if t['quoteMint']!=WSOL or t['isBuy']!='True':continue
  mint=t['mint'];qty=int(t['actualQuoteTransferRaw']);key=(*chain[t['signature']],t['utc'],t['signature'])
  if t['sameCreationTransaction']=='True':initial[mint]+=qty
  if mint not in first or key<first[mint][0]:first[mint]=(key,qty)
  elif key==first[mint][0]:first[mint]=(key,first[mint][1]+qty)
 for r in cash:
  l=launches[r['mint']];n=int(r['signedSolDeltaLamports']);month=r['utc'][:7]
  if l['quoteMint']==WSOL:
   data[month]['tradingNetCashLamports']+=n
   if l['positionStatus']==CLOSED:data[month]['closedTradingNetCashLamports']+=n;closecohort[r['mint']]+=n
 for r in failed:
  l=launches[r['mint']];n=int(r['feeLamports']);month=r['utc'][:7]
  if l['quoteMint']==WSOL:
   data[month]['tradingNetCashLamports']-=n
   if l['positionStatus']==CLOSED:data[month]['closedTradingNetCashLamports']-=n;closecohort[r['mint']]-=n
 for r in receipts:
  if r['verified']=='True' and r['asset'] in {'SOL','WSOL'}:data[r['utc'][:7]]['grossCreatorFeeLamports']+=int(r['amountLamports'])
 for r in claims:
  if r['includedStandaloneExcludesTradeOverlap']=='True':data[r['utc'][:7]]['standaloneClaimNetCashLamports']+=int(r['walletNativeOwnedWsolDeltaLamports'])
 perlaunch=[]
 for l in positions:
  m=l['createdUtc'][:7];r=data[m];r['launches']+=1;native=l['quoteMint']==WSOL;r['solQuoteLaunches' if native else 'nonSolQuoteLaunches']+=1
  if native:r['positiveCreationBuyLaunches' if initial[l['mint']]>0 else 'zeroCreationBuyLaunches']+=1;r['initialBuyTotalLamports']+=initial[l['mint']]
  if l['positionStatus']==CLOSED:r['closedSolLaunches']+=1;r['closedCohortLifetimeNetCashLamports']+=closecohort[l['mint']]
  perlaunch.append({'mint':l['mint'],'name':l['name'],'createdUtc':l['createdUtc'],'monthUTC':m,'quoteMint':l['quoteMint'],'positionStatus':l['positionStatus'],'creationBuyRaw':str(initial[l['mint']]) if native else None,'creationBuySol':sol(initial[l['mint']]) if native else None,'firstObservedBuyUtc':first[l['mint']][0][2] if l['mint'] in first else None,'firstObservedBuySol':sol(first[l['mint']][1]) if l['mint'] in first else None})
 for m,r in data.items():
  rr=[x for x in perlaunch if x['monthUTC']==m and x['quoteMint']==WSOL];allvals=[int(x['creationBuyRaw']) for x in rr];positive=[v for v in allvals if v>0]
  for col in ints:
   if col.endswith('Lamports'):r[col[:-8]+'Sol']=sol(r[col])
  r['medianPositiveCreationBuySol']=sol(median(positive));r['medianAllSolCreationBuySol']=sol(median(allvals));r['meanPositiveCreationBuySol']=sol(D(sum(positive))/len(positive)) if positive else None
  r['combinedBroadNetCashSol']=sol(r['tradingNetCashLamports']+r['standaloneClaimNetCashLamports']);r['combinedClosedNetCashSol']=sol(r['closedTradingNetCashLamports']+r['standaloneClaimNetCashLamports'])
 for row in readcsv(paths['feevaluation']):data[row['monthUTC']]['grossCreatorFeeUsdAtReceipt']=row['usd']
 for row in readcsv(paths['valuation']):
  if row['quoteMint']==WSOL:
   r=data[row['utc'][:7]];r['tradingNetCashUsdAtEvent']=str(D(r.get('tradingNetCashUsdAtEvent','0'))+D(row['usdSignedCashflow']))
   if row['positionStatus']==CLOSED:r['closedTradingNetCashUsdAtEvent']=str(D(r.get('closedTradingNetCashUsdAtEvent','0'))+D(row['usdSignedCashflow']))
 for r in data.values():
  r.setdefault('tradingNetCashUsdAtEvent','0');r.setdefault('closedTradingNetCashUsdAtEvent','0');r.setdefault('grossCreatorFeeUsdAtReceipt','0')
 def writecsv(name,rows):
  with (out/name).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 rows=list(data.values());writecsv('monthly.csv',rows);writecsv('per-launch-buy-in.csv',perlaunch)
 summary={'wallet':config['wallet'],'cutoffUtc':config['cutoffUtc'],'launchPeriodUtc':[min(r['createdUtc'] for r in positions),max(r['createdUtc'] for r in positions)],'actualTradePeriodUtc':[min(r['utc'] for r in trades),max(r['utc'] for r in trades)],'creatorReceiptPeriodUtc':[min(r['utc'] for r in receipts if r['verified']=='True' and r['asset'] in {'SOL','WSOL'}),max(r['utc'] for r in receipts if r['verified']=='True' and r['asset'] in {'SOL','WSOL'})],'launches':len(positions),'solQuoteLaunches':sum(r['solQuoteLaunches'] for r in rows),'positiveCreationBuy':stats(list(initial.values())),'allSolLaunchesCreationBuyIncludingZero':stats([initial[l['mint']] for l in positions if l['quoteMint']==WSOL]),'firstObservedPositiveSolBuy':stats([x[1] for x in first.values()]),'zeroCreationBuyLaunches':sum(r['zeroCreationBuyLaunches'] for r in rows),'firstBoughtLaterLaunches':sum(l['quoteMint']==WSOL and initial[l['mint']]==0 and l['mint'] in first for l in positions),'noObservedSolAcquisitionLaunches':sum(l['quoteMint']==WSOL and l['mint'] not in first for l in positions),'cashTotalsSol':{k:sol(sum(r[k] for r in rows)) for k in ['tradingNetCashLamports','closedTradingNetCashLamports','grossCreatorFeeLamports','standaloneClaimNetCashLamports']},'method':'Launch counts and buy-in statistics use creation UTC month. Money columns use individual UTC cash/receipt event month. Failed fees assigned once to the fee-paying wallet and witnessed launch. Cohort lifetime closed cash is a separate launch-month column. Median positive creation buy includes venue fees, excludes setup/network/rent, and excludes non-SOL quotes.','financialExecutionCapLamports':'0'}
 expected={'tradingNetCashLamports':'2278.697872527','closedTradingNetCashLamports':'1674.323228104','grossCreatorFeeLamports':'1660.286830500','standaloneClaimNetCashLamports':'1629.080316235'}
 assert set(summary['cashTotalsSol'])==set(expected);assert all(D(summary['cashTotalsSol'][k])==D(v) for k,v in expected.items());assert summary['launches']==279;assert summary['positiveCreationBuy']['count']==230;assert summary['positiveCreationBuy']['medianSol']=='4.9925925915'
 (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'monthly.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'source-manifest.json').write_text(json.dumps({'sources':[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths.values()],'validatedGlobalTotals':True},indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
