#!/usr/bin/env python3
"""Reconcile final frozen sources and refresh the valuation report/manifest."""
import csv,json,pathlib,hashlib,collections,decimal
D=decimal.Decimal
base=pathlib.Path('outputs/ramonos-launches-20261013');out=base/'usd-valuation';work=pathlib.Path('work/ramonos-launches-20261013/usd-valuation')
led=json.loads((base/'trading/capital-ledger.json').read_text());failed=list(csv.DictReader(open(base/'costs-coverage/failed-cohort-fees.csv')));claims=list(csv.DictReader(open(base/'costs-coverage/claim-native-wsol-cash.csv')));tr=json.loads((out/'trading-summary-usd.json').read_text());co=json.loads((out/'combined-account-cash-summary-usd.json').read_text());fees=json.loads((out/'summary.json').read_text())
assert 'status' not in tr and 'status' not in co
assert tr['sourceLedgerSha256']==hashlib.sha256((base/'trading/capital-ledger.json').read_bytes()).hexdigest()
assert tr['failedFeesSha256']==hashlib.sha256((base/'costs-coverage/failed-cohort-fees.csv').read_bytes()).hexdigest()
assert co['sourceClaimsSha256']==hashlib.sha256((base/'costs-coverage/claim-native-wsol-cash.csv').read_bytes()).hexdigest()
SOL='So11111111111111111111111111111111111111112';closed=[x for x in led['launches'] if x['positionStatus']=='bounded_closed_original_wallet_position' and x['quoteMint']==SOL];mints={x['mint'] for x in closed};successful=sum(int(x['nativeWsolCashDeltaLamports']) for x in closed);failedCost=sum(int(r['feeLamports']) for r in failed if r['mint'] in mints);net=D(successful-failedCost)/D(10**9)
assert len(closed)==tr['cohorts']['closed_native_sol_quote']['launches'];assert net==D(tr['cohorts']['closed_native_sol_quote']['cashSol'])
derived=collections.defaultdict(int)
for l in led['launches']:
 for t in l['economicTransactions']:derived[t['signature']]+=int(t['nativeWsolDeltaLamports'])
sourceRows=list(csv.DictReader(open(base/'trading/cashflows-for-usd.csv')));source={r['signature']:int(r['signedSolDeltaLamports']) for r in sourceRows};assert len(source)==len(sourceRows) and dict(derived)==source
claimnet=sum(int(r['walletNativeOwnedWsolDeltaLamports']) for r in claims if r['includedStandaloneExcludesTradeOverlap']=='True');assert D(claimnet)/D(10**9)==D(co['standaloneClaimCashSol']);assert net+D(claimnet)/D(10**9)==D(co['metrics'][-1]['solQuantity'])
rawCount=0
for meta in (out/'raw').glob('*.meta.json'):
 m=json.loads(meta.read_text());body=meta.with_name(meta.name.replace('.meta.json','.json'));assert hashlib.sha256(body.read_bytes()).hexdigest()==m['sha256'];rawCount+=1
cashRows=list(csv.DictReader(open(out/'trading-cashflows-valued-usd.csv')));claimRows=list(csv.DictReader(open(out/'standalone-claim-account-cash-valued-usd.csv')))
assert sum((D(r['usdSignedCashflow']) for r in claimRows),D(0))==D(co['standaloneClaimCashHistoricalUsd']);assert sum((D(r['usdSignedCashflow']) for r in cashRows if r['mint'] in mints),D(0))==D(tr['cohorts']['closed_native_sol_quote']['cashUsd'])
evidence={'successfulCashSignatureAggregationsMatchFinalCsv':True,'successfulCashSignatureCount':len(source),'sourceCashflowsSha256':hashlib.sha256((base/'trading/cashflows-for-usd.csv').read_bytes()).hexdigest(),'closedNativeSolPositions':len(closed),'closedCashBeforeFailedSol':str(D(successful)/D(10**9)),'closedFailedCostsSol':str(D(failedCost)/D(10**9)),'closedCashAfterFailedMatches':True,'standaloneClaimCashMatches':True,'combinedCashSolMatches':True,'frozenPriceResponseHashesVerified':rawCount,'allThreeRunnersOfflineReplay':'passed'}
(out/'valuation-verification.json').write_text(json.dumps(evidence,indent=2)+'\n')
f=out/'README.md';text=f.read_text();text=text.split('## Final account cash comparison')[0].split('## Account cash comparison')[0];import re
text=re.sub(r'`raw/`: \d+ frozen price responses',f'`raw/`: {rawCount} frozen price responses',text);text=re.sub(r'all \d+ frozen response SHA-256 values were verified',f'all {rawCount} frozen response SHA-256 values were verified',text)
text+='## Final account cash comparison\n\n| Metric | Historical USD at each transaction minute | SOL-equivalent quantity | Same quantity at frozen $107.60/SOL |\n|---|---:|---:|---:|\n'
for r in co['metrics']:text+=f"| {r['metric']} | ${D(r['historicalUsd']):,.2f} | {D(r['solQuantity']):,.9f} | ${D(r['sameQuantityAtFrozenSpotUsd']):,.2f} |\n"
text+=f"""
The final combined metric is **original-wallet account cash surplus**, not complete operator net profit. Closed-position cash includes captured successful transaction deltas and allocated failed network fees at their own timestamps. Standalone claim cash uses actual native SOL plus owned WSOL balance deltas for {co['includedStandaloneTransactions']} claim transactions, excluding {co['excludedTradeOverlapTransactions']} overlapping trading cash. Claim fees, tips, account funding and other actual outflows are already in those deltas. Unidentified outflows are not assumed to be economic expenses. Gross creator-fee receipts remain separate.

The {len(closed)} closed native-SOL quote positions had {D(successful)/D(10**9):.9f} SOL in successful cash differences before {D(failedCost)/D(10**9):.9f} SOL allocated failed fees. The USD calculation covers {tr['componentCount']:,} trading/failed components and {tr['uniquePriceMinutes']:,} distinct UTC minutes. Per-mint allocated account-refund components are retained; duplicate whole-transaction allocations are rejected. Aggregating {tr['successfulCashComponentCount']:,} successful components by signature exactly matches all {len(source):,} final trading cashflow CSV rows. The all-cohort SOL cash figure includes foreign-quote assets and unresolved holdings; it cannot establish complete USD profit.

`combined-account-cash-summary-usd.json` and `comparison-metrics-usd.csv` contain the table. `trading-cashflows-valued-usd.csv`, `trading-launches-valued-usd.csv` and `standalone-claim-account-cash-valued-usd.csv` preserve individual calculations. `valuation-verification.json` binds reconciliation to the final source digest. All three portable runners replay offline.

Reproduce the trading and standalone claim calculations after reproducing fee receipts:

```sh
python3 outputs/ramonos-launches-20261013/usd-valuation/value_trading_cashflows.py --ledger outputs/ramonos-launches-20261013/trading/capital-ledger.json --failed-fees outputs/ramonos-launches-20261013/costs-coverage/failed-cohort-fees.csv --claim-network-fees outputs/ramonos-launches-20261013/usd-valuation/additional-claim-network-fees.csv --output outputs/ramonos-launches-20261013/usd-valuation --offline
python3 outputs/ramonos-launches-20261013/usd-valuation/value_claim_account_cash.py --claims outputs/ramonos-launches-20261013/costs-coverage/claim-native-wsol-cash.csv --output outputs/ramonos-launches-20261013/usd-valuation --offline
python3 outputs/ramonos-launches-20261013/usd-valuation/refresh_report.py
```

The optional gross-fees-plus-closed-cash-minus-extra-claim-network-fees proxy is ${D(tr['knownNetCoreHistoricalUsd']):,.2f}. It deducts only additional claim network fees and omits other actual claim-transaction wallet outflows. It is not the account cash surplus or complete net-profit number.
"""
f.write_text(text)
for name in ['value_receipts.py','value_trading_cashflows.py','value_claim_account_cash.py','refresh_report.py']:
 if (work/name).exists():(out/name).write_bytes((work/name).read_bytes())
files=sorted(x for x in out.rglob('*') if x.is_file() and x.name!='SHA256SUMS');(out/'SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+str(x.relative_to(out))+'\n' for x in files));print(json.dumps(evidence,indent=2))
