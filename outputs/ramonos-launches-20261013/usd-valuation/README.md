# Ramonos fee receipts: historical USD market valuation

The verified 1,660.286830500 SOL-equivalent creator-fee receipts were worth **$199,731.89** using the SOL/USD price in each receipt's own minute. Applying the frozen current quote of **$107.60/SOL** to the same quantity gives **$178,646.86**, a **$21,085.03** difference. The latter is a hypothetical comparison of the original receipt quantity, not a statement of today's wallet balance.

| Asset | Receipt events | Quantity in SOL units | Historical USD market value |
|---|---:|---:|---:|
| Native SOL | 503 | 484.061725386 | $57,526.56 |
| Wrapped SOL | 342 | 1,176.225105114 | $142,205.33 |
| Total | 845 | 1,660.286830500 | $199,731.89 |

Coverage is all 845 verified SOL/WSOL receipt events, across 565 distinct transactions and 544 UTC minutes, from December 17, 2025 at 20:40:24 UTC through October 10, 2026 at 16:03:22 UTC. The source CSV's 851 total events span 568 transactions; its four PUMP and two USDC events are excluded from this SOL valuation.

For every receipt, the calculation is amountLamports / 1,000,000,000 multiplied by the close of its containing 60-second UTC Coinbase Exchange SOL-USD candle. The price is an exchange market proxy: a minute close can occur after the receipt within that minute. It is not the exact transaction-second trade price, proof of conversion to USD, or realized USD sale proceeds. The weighted historical price is $120.299628944 per SOL. Applying every minute's low and high instead gives $199,649.38–$199,863.47. This is an intraminute sensitivity range, not a guaranteed cross-exchange or statistical error bound. No missing-minute approximation was needed.

The frozen current quote was Coinbase Exchange's last trade of $107.60 at 2026-10-13T19:35:41.545450310Z; provider clock response was 2026-10-13T19:35:43.579Z. No future-date assumption was needed.

These are gross creator-fee receipts, not trading profit. Gas, purchase costs, later trading gains/losses and other-asset fees are outside this total. Trading profit in USD requires pricing each purchase and sale at its own time.

## Files and reproduction

- `receipts-valued-usd.csv`: all 845 individual receipt valuations, signatures, receipt time, candle time, close/low/high, and frozen source path.
- `monthly-valued-usd.csv`: monthly sums calculated without intermediate rounding.
- `summary.json`: exact decimal totals, method, source digest, spot timestamp and limitations.
- `raw/`: 444 frozen price responses across fee and cashflow valuation, including current ticker and provider clock; each response has URL, retrieval time, HTTP status, response headers and SHA-256 metadata.
- `value_receipts.py`: portable Python standard-library reproduction script; `retrieve_prices()` is reusable for purchase/sale cashflows.

From the investigation root, reproduce without network access:

```sh
python3 outputs/ramonos-launches-20261013/usd-valuation/value_receipts.py --receipts outputs/ramonos-launches-20261013/own-fees/receipts.csv --output outputs/ramonos-launches-20261013/usd-valuation --offline
```

Offline replay succeeded. Independent row sums match the summary; all 444 frozen response SHA-256 values were verified.

Source: [Coinbase Exchange historical candle documentation](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles). The documented schema is timestamp, low, high, open, close, volume; 60-second granularity is supported. Source endpoints: [SOL-USD ticker](https://api.exchange.coinbase.com/products/SOL-USD/ticker) and [provider clock](https://api.exchange.coinbase.com/time). Exact historical request URLs are retained in `raw/*.meta.json`.


## Final account cash comparison

| Metric | Historical USD at each transaction minute | SOL-equivalent quantity | Same quantity at frozen $107.60/SOL |
|---|---:|---:|---:|
| Gross verified SOL/WSOL creator-fee receipts | $199,731.89 | 1,660.286830500 | $178,646.86 |
| Closed 196 positions original-wallet cash after allocated failed fees | $195,964.71 | 1,674.323228104 | $180,157.18 |
| Standalone claim-transaction original-wallet native+WSOL cash | $196,532.97 | 1,629.080316235 | $175,289.04 |
| Combined closed positions + standalone claim account cash surplus | $392,497.68 | 3,303.403544339 | $355,446.22 |

The final combined metric is **original-wallet account cash surplus**, not complete operator net profit. Closed-position cash includes captured successful transaction deltas and allocated failed network fees at their own timestamps. Standalone claim cash uses actual native SOL plus owned WSOL balance deltas for 559 claim transactions, excluding 9 overlapping trading cash. Claim fees, tips, account funding and other actual outflows are already in those deltas. Unidentified outflows are not assumed to be economic expenses. Gross creator-fee receipts remain separate.

The 196 closed native-SOL quote positions had 1676.617576116 SOL in successful cash differences before 2.294348012 SOL allocated failed fees. The USD calculation covers 5,262 trading/failed components and 1,312 distinct UTC minutes. Per-mint allocated account-refund components are retained; duplicate whole-transaction allocations are rejected. Aggregating 2,637 successful components by signature exactly matches all 2,460 final trading cashflow CSV rows. The all-cohort SOL cash figure includes foreign-quote assets and unresolved holdings; it cannot establish complete USD profit.

`combined-account-cash-summary-usd.json` and `comparison-metrics-usd.csv` contain the table. `trading-cashflows-valued-usd.csv`, `trading-launches-valued-usd.csv` and `standalone-claim-account-cash-valued-usd.csv` preserve individual calculations. `valuation-verification.json` binds reconciliation to the final source digest. All three portable runners replay offline.

Reproduce the trading and standalone claim calculations after reproducing fee receipts:

```sh
python3 outputs/ramonos-launches-20261013/usd-valuation/value_trading_cashflows.py --ledger outputs/ramonos-launches-20261013/trading/capital-ledger.json --failed-fees outputs/ramonos-launches-20261013/costs-coverage/failed-cohort-fees.csv --claim-network-fees outputs/ramonos-launches-20261013/usd-valuation/additional-claim-network-fees.csv --output outputs/ramonos-launches-20261013/usd-valuation --offline
python3 outputs/ramonos-launches-20261013/usd-valuation/value_claim_account_cash.py --claims outputs/ramonos-launches-20261013/costs-coverage/claim-native-wsol-cash.csv --output outputs/ramonos-launches-20261013/usd-valuation --offline
python3 outputs/ramonos-launches-20261013/usd-valuation/refresh_report.py
```

The optional gross-fees-plus-closed-cash-minus-extra-claim-network-fees proxy is $395,696.09. It deducts only additional claim network fees and omits other actual claim-transaction wallet outflows. It is not the account cash surplus or complete net-profit number.
