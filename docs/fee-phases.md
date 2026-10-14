# Creator payouts before versus after graduation

**Most of the disclosed wallet's observed creator payouts come through PumpSwap custody.** At least **1,339.092577473 SOL**, or **80.6543%** of the **1,660.286830500 SOL** gross creator-payout total, is traced to PumpAMM. The remaining **321.194253027 SOL** is unresolved by source and must not be labelled entirely bonding-curve revenue.

Wallet: `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`. Historical payout cutoff: **2026-10-13 16:19:01 UTC**. This is an offline extension of the existing finalized audit. No new claim, trade, transfer or funding occurred.

## Source venue, rather than withdrawal date

| Payout source | SOL equivalent | Share of all gross payouts |
|---|---:|---:|
| Direct PumpAMM claims | 1,176.225105114 | 70.8447% |
| Sharing payouts sourced to same-transaction AMM input, conservative minimum | 162.867472359 | 9.8096% |
| **Combined AMM minimum** | **1,339.092577473** | **80.6543%** |
| Remaining native and sharing payouts | **At most 321.194253027** | **At most 19.3457%** |

The native Pump-claim component is 319.655754211 SOL. The full mint-bound sharing component is 164.405971175 SOL, of which at most 1.538498816 SOL remains untraced here. SOL and canonical WSOL are combined without counting an unwrap as new income.

Pump's native creator vault can receive funds swept from the AMM. The official `transfer_creator_fees_to_pump` instruction accepts a generic `coin_creator`; it does not require a sharing configuration. Therefore a Pump-program claim is not automatically a curve-origin payout. A withdrawal after graduation can also contain fees earned earlier. Fee-source phase and claim timing are distinct.

PumpSwap's normal creator-fee accrual applies to canonical migrated pools. This audit proves payout custody and actual transfers, rather than independently auditing every upstream pool or proving that every paid unit originated in third-party trading. These are gross protocol payouts, not net profit or a fully source-reconciled pure trading-fee total.

## Per-token findings and limits

Pooled direct claims account for **1,495.880859325 SOL** and do not identify individual tokens. Sharing payouts identify **22 mints**: 15 signed-launch cohort mints and seven other mints. A token's identified sharing receipts can be a partial component of its overall creator income.

For [PsyopCartoon](https://pump.fun/coin/DAAXmRU9KUEuyqF8VuddbcL5X4QhQ3tTDMYxDbNgpump), identified sharing payouts total **157.863727454 SOL**. At least **157.863727383 SOL** is sourced to same-transaction AMM custody, leaving only 71 lamports untraced. Effectively all of these identified payouts came from the AMM side.

For [this coin will retire you](https://pump.fun/coin/9KMXMkzyiiKnubfjFkND54zJdnE1EmUyYowq8A3ipump), identified sharing receipts total **0.089564780 SOL**. The strict AMM-source minimum is **0.018491623 SOL**. Opening custody remains unresolved, so this small component does not establish a full token-lifetime majority.

At the retained route snapshot, **48 of 277 Pump launches** have validated canonical AMM pools, about **17.33%**. Another 229 have incomplete curves without an observed canonical pool. Two LaunchLab launches remain in funding. These account-state counts differ from monetary receipt percentages.

The complete 279-mint register leaves exact lifetime pre/post fee totals **unknown**. Current `BondingCurve.creator_fee` and `Pool.creator_fees` are unswept buckets, not cumulative lifetime revenue counters. Verified accrual subsets cover twelve mints; Flightradar24's 0.146041920 SOL and Bold's 0.620058647 SOL are checked curve/configuration-period fees toward their configured targets, not receipts by the disclosed launcher.

## Fee rates and interpretation

Pump's [fee page](https://pump.fun/docs/fees), last updated October 8, 2026, lists **30 bps curve creator fees** and **95 bps canonical AMM creator fees at 420–1,470 SOL market cap**. Below 420 SOL the listed AMM creator rate is 30 bps; higher tiers generally decline. Custom pairs use a separate flat schedule. Historical amounts in this audit use actual events and transfers rather than today's rate schedule.

At 30 versus 95 bps, the same 100 SOL of quote trading principal yields 0.30 versus 0.95 SOL of gross creator fees, a 3.1667-times difference. Two-sided trading volume can greatly exceed the net capital accumulated toward graduation. These observations support the importance of graduated AMM activity to this wallet's observed payouts, without assuming equal income per launch.

## Evidence and reproduction

- [Receipt-channel summary and strict bounds](../outputs/fee-phase-20261014/ramonos-receipts/summary.json)
- [Every mint-bound sharing component](../outputs/fee-phase-20261014/ramonos-receipts/per-mint-sharing.csv)
- [Source-transfer and distribution witnesses](../outputs/fee-phase-20261014/ramonos-receipts/sharing-source-traces.json)
- [279-mint register with explicit attribution gaps](../outputs/fee-phase-20261014/per-token/mint-register.csv)
- [Verified token-specific accrual subsets](../outputs/fee-phase-20261014/per-token/verified-phase-subset-summary.json)
- [Independent review](../outputs/fee-phase-20261014/review/REPORT.md)

The strict custody lower bound for a sharing payout is `max(0, recipient_payment - untraced_spendable_custody)`. It does not presume proportional attribution of fungible source lots. An earlier proportional estimate was corrected during independent review; it is not the headline result.

First extract the existing raw audit inputs and run the original `tools/replay.py --full` workflow into an isolated output workspace. Then run `tools/fee-phase/receipts.py` and `tools/fee-phase/per_token.py` with `RAMONOS_RESEARCH_ROOT` pointing there. The original replay creates the transaction ledger required by the phase processor. Both phase processors use retained inputs and make no network request. Raw provider credentials are excluded; event amounts, signatures, slots, account ownership and input hashes remain retained.
