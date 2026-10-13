# Independent recheck, October 14, 2026

This recheck uses the frozen October 13 evidence and computation tools from published revision `6f3cbb16c6f095bb805009d0c2965cfade3a33d9`. It adds no fresh chain observation, signing, claims or transfers. Execution cap: 0 SOL. Audit cutoff: October 13 at 16:19:01 UTC. Route captures retain their separate observation times.

## Reproduced results

| Measure | SOL | Historical USD |
|---|---:|---:|
| 196 closed SOL positions after allocated failed fees | 1,674.323228104 | $195,964.71 |
| 559 separate claim transactions, net native and owned WSOL cash | 1,629.080316235 | $196,532.97 |
| Combined original-wallet cash surplus | 3,303.403544339 | $392,497.68 |
| Gross creator payouts, separate from net claim cash | 1,660.286830500 | $199,731.89 |

All eight offline profit replay stages completed. The trading verification checked 2,411 whole-transaction cash balances, 1,378 PumpSwap quote-transfer legs and 25 LaunchLab quote-transfer legs. All 279 inventory and cash equations passed, with no trading decoder errors. Nine zero-payout claim/trade overlaps are excluded from separate claim cash, avoiding duplicate costs.

The independent arithmetic checker verified 5,262 trading and failed-cost components and 559 net claim transactions against exact containing-minute Coinbase SOL/USD closes. All 338 used raw price-response hashes matched retained metadata. Dollar values are historical cashflow valuations, not actual USD cashouts. Failed costs are already included in the priced trading table and are not subtracted twice.

Current route counts remain 263 of 277 Pump launches assigning 100% to the disclosed wallet, or 94.95%. All 41 route-manifest member hashes matched. Current routes do not prove launch-time routing or historical fee-value percentages.

## Per-token attribution

108 standalone claim transactions across six cohort mints have one identified mint, verified SOL/WSOL payouts and no cash residual beyond network fees. Their net claim cash is 159.011821279 SOL. Combining these claims with closed-position cash identifies 1833.335049383 SOL of token-attributable components. The remaining 1470.068494956 SOL is pooled or otherwise unallocated claim cash.

[Token-attributable cash CSV](token-attributable-cash.csv) includes exact mints, full names, $tickers, position status, closed-position cash, attributable claim cash, historical dollars and each known component's percentage of the 3,303.403544339 SOL total. Empty trading cash means the position is unresolved. Zero attributable claim cash does not establish zero earned fees. The table is not a complete per-token earnings ranking.

Complete operator profit remains unproved because of transferred/open inventory, other quote assets, unknown beneficial ownership of transfers, pooled claims and incomplete associated-account-only lifetime coverage.

## Reproduce

Extract the existing profit evidence release into the repository root, then run from that root:

```sh
python3 tools/recheck.py --out /tmp/ramonos-independent-recheck
```

The checker uses Python's standard library and performs no network calls. Input hashes are retained in [arithmetic-verification.json](arithmetic-verification.json). [profit-replay-validation.json](profit-replay-validation.json), [trading-replay-verification.json](trading-replay-verification.json) and [usd-independent-check.json](usd-independent-check.json) retain this chat's independent checks.
