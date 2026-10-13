# Disclosed-wallet launch trading ledger

This is read-only evidence for `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b` and the fixed successful-wallet-reference cutoff `2026-10-13T16:19:01Z`. Financial execution cap: 0 SOL.

`summary.json` separates closed SOL/WSOL trading margin, observed associated wallet cash, other quote assets, transfers and open inventory. `positions.csv` retains all 279 mint identities. `trades.csv` retains each buy/sell and actual quote transfer; `transactions.csv` retains native/WSOL cash once per allocated component. `cashflows-for-usd.csv` groups shared cleanup components once per signature and supplies signed SOL cash and transaction UTC. A closed target position in another quote asset is not SOL trading profit.

The trade margin equals sale quote receipts less buy quote cost, including venue fees. Associated observed native+WSOL wallet cash already incorporates paid successful network fees, tips, funded accounts, returned account reserves and other associated native movements. Do not subtract those costs again. Separately acquired failed network fees remain outside this ledger. Creator receipts are excluded; the nine apparent claim/configuration overlaps are verified zero distributions, as recorded in `overlap-proof.json`.

For Pump AMM, fields have different meanings between ordinary and exact-quote buys. Actual quote movement is proved from parsed owner quote-token transfers under the CPI-bound AMM instruction. Event `user_quote_amount_in` is the reserve principal for the retained exact-quote buy witness, not total wallet debit. `capital-ledger.json` retains individual transfer legs and event payload hashes.

Successful direct-wallet pagination is terminal, but `tokenAccounts=none` does not enumerate ATA-only history. Last-observed inventories reconcile to the later same-slot finalized SPL and Token2022 owner snapshots in `current-inventory/`. Those current snapshots do not retroactively establish custody at the history cutoff. Incoming/outgoing transfers have unresolved acquisition basis or downstream proceeds; open inventory is unvalued. Aggregate cash surplus for these groups is not complete economic profit.

Offline replay uses the existing public portable tools and schemas. Place `build.py` and `report.py` under `tools/trading/`; from the repository root run:

```sh
python3 tools/trading/build.py
python3 tools/trading/report.py
python3 tools/trading/verify.py
```

A separate data workspace can be selected with `RAMONOS_RESEARCH_ROOT`. `RAMONOS_CODE_ROOT` optionally selects the repository supplying `tools/decoder.py`, `tools/fee_core.py` and pinned `schemas/`. No network is used by either computation. Required retained inputs are the census history manifest/pages, census launches, own-fee verified receipts, two current-inventory snapshots and `trading/inputs/jito-tip-accounts.json`. `schema-provenance.json` binds the existing official schema inputs by SHA-256.

The full LaunchLab ABI facts needed for buy/sell admission are retained separately in `inputs/launchlab-idl.json`: official Raydium revision `e7e0c96fe77bcf6a020b84a44c47a722aac8e359`, original source hash and stripped ABI-facts hash in the neighboring `.source.json`. This extends the older creator-fee-only minimal public schema; 25 LaunchLab trade CPI witnesses are validated.
