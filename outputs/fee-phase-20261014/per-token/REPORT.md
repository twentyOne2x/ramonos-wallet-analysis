# Ramonos per-token creator-fee phase feasibility

Retained census: **279 signed launches**. The retained account snapshots show 48 validated canonical Pump AMM pools, 229 Pump curves marked incomplete without an observed canonical pool, and two LaunchLab pools still funding. These are observed account states; migration timestamps and migration transaction signatures are not established by the route snapshot. Canonical absence is not a lifetime zero-fee proof.

The [mint register](mint-register.json) retains each creation witness, migration-state source, distinct curve/pool snapshot slots and unswept creator-fee buckets. All exact lifetime before-graduation and after-graduation amounts remain null. Null means unknown, not zero.

## Why counters cannot close lifetime totals

`BondingCurve.creator_fee` and `Pool.creator_fees` are **unswept fee buckets**, not cumulative earned counters. Retained official Pump SDK `src/sdk.ts` documents that v3 trade creator fees remain on the curve until `sweep_creator_fee`; `src/onlineSdk.ts` performs curve and pool sweeps before distribution when their buckets are nonzero. Legacy trades transferred fees directly to pooled creator custody. A current zero bucket therefore permits earlier earned and swept fees. Creation-trade fees plus current buckets omit intermediate trades and sweeps.

The original wallet's Pump and AMM payout receipts are pooled by creator/quote and do not establish a mint's lifetime earned fees. A Pump AMM claim identifies its immediate AMM custody source. A Pump native claim identifies only its receipt program: Pump AMM `transfer_creator_fees_to_pump` can feed the native creator vault for an ordinary coin creator without a sharing-config restriction, so its original accrual phase remains unknown unless actual upstream inflows are traced. A receipt dated after graduation can include earlier curve-earned fees. Current recipient splits cannot allocate historic pooled claims.

## Exact retained subsets

[Verified phase subset events](verified-phase-subset-events.json) and [aggregate subsets](verified-phase-subset-summary.json) contain 4,237 evidence rows for 12 mints. They are explicitly **not lifetime totals**. Curve-trade amounts are admitted only from the existing replay's exact verified transfer/direct-lamport reconciliation, event hash, signature and mint. A positive remaining real-token reserve establishes the pre-completion portion of these retained legacy curve trades. One curve-completing trade is retained in a separate unresolved-boundary category. No v3 post-completion trade is included in this pre-graduation classifier; all retained admitted instruction names are legacy buy/sell or v2 variants.

Examples:

| Mint / token | Phase subset | Creator fees | Scope |
|---|---|---:|---|
| `4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump` / Flightradar24 | Before graduation | 0.146041920 SOL | 146 verified config-era curve trades; earlier ordinary-wallet creator trades excluded |
| `EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM` / Bold | Before graduation | 0.620058647 SOL | 374 verified config-era curve trades |
| `DAAXmRU9KUEuyqF8VuddbcL5X4QhQ3tTDMYxDbNgpump` / PsyopCartoon | After graduation | 0.004210952 SOL | AMM ATA inflows since exact zero checkpoint; not lifetime |
| `9KMXMkzyiiKnubfjFkND54zJdnE1EmUyYowq8A3ipump` / this coin will retire you | After graduation | 0.002255404 SOL | AMM ATA inflows since exact zero checkpoint; not lifetime |
| `GiqnV6wrZck1od9ruHrakVHXMYNXDEZcUnbPv1scbonk` / Internet Magic Ticket | Before graduation | 2.000000 USD1 | Exact creation-transaction funding-stage creator fee |
| `7b1otW189NkEpUdiN2P4mVNvrztqnRd9nesAhk3Cbonk` / dog wif pahlavi | Before graduation | 0 SOL | Exact creation trade only; lifetime unknown |

## Smallest path to remaining gaps

1. First decode mint-tagged trade, completion, migration and fee-sweep events already in the retained finalized census transactions. Reuse the existing event decoder and official schema provenance; retain instruction/event identity, asset, payload hash and raw source. This supplies additional *observed subsets*, not full market history, because a wallet census excludes other traders.
2. Inspect retained config-vault histories for pre-config ordinary creator trades, which already appear incidentally in these captures. Add them only after the same exact cash/event binding; do not treat their incidental presence as full historical coverage.
3. For exact lifetime accrual, require complete per-curve and canonical-pool finalized trade/sweep history from creation to the cutoff. Use a bounded pilot on Flightradar24 and one graduated target with existing replay, page caps and declared gaps before expanding. Current counters alone cannot bypass that requirement.
4. For graduated pools, complete replay from pool creation is necessary to fill old AMM accrual. The retained latest-ATA exact-zero checkpoint closes present custody, not lifetime AMM earning. Preserve creator/config transitions and quote assets.
5. Reconcile earned creator fees, swept custody and actual paid recipients separately. Do not assign pooled wallet claims to mint by launch count, elapsed time, current share, trading volume estimate or today's fee rate.

No new network requests and no economic effects were performed. All inputs are retained source artifacts hashed in [summary.json](summary.json).
