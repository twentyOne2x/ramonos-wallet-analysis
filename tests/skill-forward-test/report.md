# Forward test: supplied transaction fee receipts

The disclosed wallet `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b` received **51.465459929 SOL equivalent in canonical creator-fee payouts** across all six distinct supplied successful transactions: **5.723492808 native SOL + 45.741967121 canonical WSOL**. Each WSOL payout entered its own wallet-owned token account and was unwrapped into that wallet in the same transaction; unwraps and rent returns are not additional receipts.

The four transactions in `wallet-transactions.json` alone prove **50.499007419 SOL equivalent**. The two additional supplied social-route transactions include **0.966452510 SOL equivalent** of direct wallet receipts before the route change, producing the combined amount above. There are no duplicate signatures across the files.

A separate payout of **16.305078 USDC** (`EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`, six decimals) is excluded from SOL totals.

| Transaction prefix | Native SOL receipt | WSOL receipt |
|---|---:|---:|
| 5CJ2YGy1wkUd | 0.129439372 | 0.133299659 |
| 2j5dukrXzN1E | 0.203001499 | 0 |
| 477HecPyXLsZ | 4.387787589 | 44.518460171 |
| iKVtpyUHoWnF | 0.040463958 | 1.086555171 |
| 3cE6S2cJZFP5 | 0.962800390 | 0.003652120 |
| 5N9DBKGwjGZD | 0 | 0 |

[Receipt ledger](receipt-ledger.json) retains complete signatures, timestamps, slots, instruction positions, event hashes, source payload hashes, actual transfer sources/destinations, destination owners, mints and raw integer amounts. Native receipts match canonical Pump inner system transfers and source-account debits. AMM receipts match canonical Pump AMM token transfers, exact vault debits, wallet-owned account initialization, canonical WSOL mint and nine decimals. Missing legacy `quote_mint` event fields remain missing; native denomination is established independently by actual system-transfer instructions.

Combined net native wallet cash movement is **51.443154221 SOL**, after **0.000054588 SOL** transaction fees and **0.022251120 SOL** retained account funding/rent. This reconciles to the gross receipts; it is not profit. Canonical payout amounts are proven, but older pooled-vault funding/fee lots were not supplied, so pure fee-origin lifetime revenue and attribution to individual mints are not established.

## Configured developer routes and claims

Both supplied current routes allocate 100% (10,000/10,000 basis points) to a social custody account. Snapshot slot: **456506067**. Route identity labels are supplied annotations, not independent human-ownership verification.

- **Flightradar24** (`4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump`) routes to direct GitHub identity `12810712`, custody account `qNG5wnFQWzDHm1zGTMnqddwGp861LK7srHv3prtn1Dv`. The supplied transaction `5N9DBKGwjGZD…` proves a **0.010778206 SOL** fee distribution into this account, with matching source debit and recipient credit. The account began with **0.002136720 SOL** creation funding. Snapshot balance **0.012914926 SOL** equals those two amounts exactly; `total_claimed=0`, `last_claimed=0`, `total_stable_claimed=0`. Thus the supplied counter reports **no claims**, and **0.010778206 SOL** is the observed unclaimed fee lot consistent with retained current custody. No developer-wallet receipt is shown. Selected history does not prove uninterrupted replay to the snapshot, so this is not a complete account-history proof.
- **Bold** (`EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM`) routes to the supplied UsePaid GitHub intermediary identity `322216527`, custody account `FfLpuH4WPn2MR8Lqn1MpwQc1HtAPPqL3qvMWZjnFHGpv`. Its current account reports aggregate native claims of **52,313.813492020 SOL** (`total_claimed=52313813492020` raw). These establish an aggregate claim counter for the intermediary account, not Bold-specific claimed fees and not a receipt by `@boldleonidas`. No claim transaction or recipient wallet is supplied. Metadata saying “Fees to @boldleonidas” does not prove downstream settlement. `total_stable_claimed=19555437862363` is retained raw; no stable mint/decimals are supplied to assign asset units safely. Current native account balance is **0.003687493 SOL**, but initial funding/history are absent, so its remaining fee-origin balance is **unknown**, not zero and not the full balance. Any hypothetical subtraction of the other account's rent amount would be an unsupported fee estimate.

Both supplied route annotations list current curve pending raw amount zero. No raw curve account or pool state is supplied; pool pending is null. These annotations do not establish complete upstream pending accounting.

## Coverage and skill feedback

This is a selected-successful-transaction audit (dates 2025-12-17 through 2026-06-28), not full wallet or lifetime revenue. Account snapshot timing is separate. No network, claims, transfers, publication or input modifications occurred. No decoding errors occurred; only permitted generic decoder/schema modules were imported.

The skill's accounting contract correctly prevented asset mixing, WSOL double counting, present-route rewrites of historical payouts, and intermediary-to-human attribution. The documented retained commands require a larger named-input workspace and do not directly accept these fixture files; a small read-only adaptation was necessary. The supplied account snapshots contain decoded state and hashes but omit raw serialized account bytes, preventing independent owner/PDA/account decoding verification. Retained schema metadata says version 0.1.0; schema files are pinned by SHA-256 in the manifest, but an upstream source revision cannot be verified within the permitted input scope. No complete social replay is supplied, so the strongest custody/funding proof required by the skill remains unavailable; balances are not automatically fee-origin amounts.

Reproduce with `python3 audit.py`; the script imports the permitted decoder from the adjacent repository and writes only this result directory.
