#!/usr/bin/env python3
"""Actual captured claim-transaction native+WSOL cash, separate from gross fees."""
import argparse,csv,decimal,hashlib,json,pathlib
from value_receipts import retrieve_prices,stamp
D=decimal.Decimal

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--claims',required=True);ap.add_argument('--output',required=True);ap.add_argument('--offline',action='store_true');a=ap.parse_args();out=pathlib.Path(a.output)
 claims=list(csv.DictReader(open(a.claims)));included=[r for r in claims if r['includedStandaloneExcludesTradeOverlap']=='True'];assert len({r['signature'] for r in included})==len(included)
 candles=retrieve_prices([stamp(r['utc']) for r in included],out/'raw',a.offline);values=[]
 for r in included:
  c=candles[stamp(r['utc'])//60*60];sol=D(r['walletNativeOwnedWsolDeltaLamports'])/D(10**9)
  values.append({**r,'signedSolEquivalent':str(sol),'priceMinuteUTC':c['minuteUTC'],'solUsdMinuteClose':str(c['close']),'usdSignedCashflow':str(sol*c['close']),'usdLowSensitivity':str(sol*(c['low'] if sol>=0 else c['high'])),'usdHighSensitivity':str(sol*(c['high'] if sol>=0 else c['low'])),'priceRawSource':c['rawSource']})
 with (out/'standalone-claim-account-cash-valued-usd.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
 fees=json.loads((out/'summary.json').read_text());trading=json.loads((out/'trading-summary-usd.json').read_text());closed=trading['cohorts']['closed_native_sol_quote'];spot=D(fees['currentSolUsdSpot'])
 sol=sum((D(r['signedSolEquivalent']) for r in values),D(0));usd=sum((D(r['usdSignedCashflow']) for r in values),D(0));low=sum((D(r['usdLowSensitivity']) for r in values),D(0));high=sum((D(r['usdHighSensitivity']) for r in values),D(0))
 rows=[{'metric':'Gross verified SOL/WSOL creator-fee receipts','historicalUsd':fees['historicalUsdMarketValue'],'solQuantity':fees['solEquivalent'],'sameQuantityAtFrozenSpotUsd':fees['sameSolAtCurrentSpotUsd']},{'metric':f"Closed {closed['launches']} positions original-wallet cash after allocated failed fees",'historicalUsd':closed['cashUsd'],'solQuantity':closed['cashSol'],'sameQuantityAtFrozenSpotUsd':str(D(closed['cashSol'])*spot)},{'metric':'Standalone claim-transaction original-wallet native+WSOL cash','historicalUsd':str(usd),'solQuantity':str(sol),'sameQuantityAtFrozenSpotUsd':str(sol*spot)},{'metric':'Combined closed positions + standalone claim account cash surplus','historicalUsd':str(D(closed['cashUsd'])+usd),'solQuantity':str(D(closed['cashSol'])+sol),'sameQuantityAtFrozenSpotUsd':str((D(closed['cashSol'])+sol)*spot)}]
 with (out/'comparison-metrics-usd.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={'sourceClaims':a.claims,'sourceClaimsSha256':hashlib.sha256(pathlib.Path(a.claims).read_bytes()).hexdigest(),'sourceTradingSummarySha256':hashlib.sha256((out/'trading-summary-usd.json').read_bytes()).hexdigest(),'includedStandaloneTransactions':len(included),'excludedTradeOverlapTransactions':len(claims)-len(included),'standaloneClaimCashSol':str(sol),'standaloneClaimCashHistoricalUsd':str(usd),'standaloneClaimCashUsdLowSensitivity':str(low),'standaloneClaimCashUsdHighSensitivity':str(high),'metrics':rows,'frozenCurrentSolUsd':str(spot),'frozenCurrentSpotTradeUTC':fees['currentSpotTradeUTC'],'definition':'Original-wallet account cash surplus, not complete operator net profit. Gross fee receipts remain a separate metric. Every signed cash component and failed fee is priced at its own minute. Claim cash includes actual fees/tips/rent/outflows in wallet balances; unidentified outflows are not assumed to be economic expenses.','sourceDocs':'https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles'}
 (out/'combined-account-cash-summary-usd.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
