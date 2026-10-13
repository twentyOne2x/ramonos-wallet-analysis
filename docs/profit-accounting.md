# Trading, creator fees and original-wallet net cash

This extension preserves the disclosed wallet and 279-launch census. Read the repository README for the final amounts and dollar comparison. The fee and trading cutoff is October 13, 2026 at 16:19:01 UTC. Later current owner-token-account reads are explicitly labeled by finalized slot rather than backdated.

## What is measured

- Quote trade margin: actual quote debit on buys versus actual quote credit on sales, with venue fees.
- Associated wallet cash: native SOL balance change plus original-wallet-owned canonical WSOL quantity change for admitted transaction components. Wraps and unwraps cancel economically. Successful network fees, tips, account deposits/refunds and external transfers are already inside those balances.
- Closed-position net cash: associated cash for fully matched, closed original-wallet SOL positions, minus their separately captured and witnessed failed-transaction fees.
- Standalone claim cash: actual native plus owned-WSOL balance changes across claim transactions, excluding transaction signatures already assigned to trading.
- Gross creator receipts: actual protocol payout amounts; retained separately from claim cash and mint-attributed trading. Pooled claims are not exclusively attributable to the signed launch cohort.

Cash flow is not automatically profit. Refundable account reserves are capital rather than proved expenses. A transfer to an unidentified destination might be an expense, funding or an internal transfer between wallets whose beneficial ownership is unknown. Open/transferred tokens, other quote assets and activity in other wallets remain outside complete operator-profit proof.

## Coverage and controls

34 terminal pages contain 32,798 finalized successful direct-wallet references. Another 21 terminal pages contain 19,292 failed references. Only the actual fee payer is charged. Every attributed failed transaction has one explicit cohort mint or known token-account instruction witness; unrelated or unallocated failures are kept separate. No associated-account-only history census is asserted.

The trading decoder closes dependencies across Pump, PumpSwap and Raydium LaunchLab. All 2,249 admitted trades have quote identities and exact integer arithmetic. PumpSwap exact-quote input semantics are checked against actual SPL transfer legs under the same parent instruction. LaunchLab admission binds payer, pool, base mint, quote mint and actual quote transfer to official ABI facts. A minimal creator-fee ABI is insufficient for a trading census.

Final classification: 196 closed SOL, 46 transferred, 11 remaining inventory, 19 no observed acquisition, seven closed other quote. All 279 historical last-observed inventory amounts agree with current owner custody in the two token-program snapshots at finalized slot 456560197. That proves the retained custody comparison, not every historical ATA-only transfer.

Nine apparent claim/trade overlaps are zero payout distributions. Their actual transaction cash and fees are counted once. Shared cleanup transactions allocate only exact target-account reserve refund components, not the whole transaction repeatedly.

## Dollar valuation

[Coinbase Exchange candle documentation](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles) specifies the six-field public OHLCV response used here. Each receipt or signed cashflow uses its exact containing 60-second UTC candle close. A minute close can occur after the on-chain receipt within that minute. Low/high columns retain intraminute sensitivity. No daily interpolation, missing-candle fill or actual USD liquidation is asserted.

Historical net cash USD sums each buy, sale, refund, other allocated cash movement and failed fee at its own timestamp. Multiplying a SOL profit by the sale-day price is a different measure. The current comparison multiplies the frozen historical SOL quantity by the captured $107.60 spot price and does not claim present holdings.

## Reproduce

Download the full profit evidence release and verify its SHA256SUMS. Extract it into the repository. Run `python3 tools/replay_profit.py --out /tmp/ramonos-profit-replay` from the repository root. The destination must be empty and outside the input tree. The runner uses frozen raw sources offline and verifies final comparison metrics. It never signs, trades, claims or sends funds.

CSV registers, raw captures, independent reviews, pinned source ABIs and computation tools are retained under `outputs/ramonos-launches-20261013/` and `tools/`. Original evidence release remains available separately.
