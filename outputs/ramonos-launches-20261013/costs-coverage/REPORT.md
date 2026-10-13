# Costs and coverage — fixed wallet / cutoff

Wallet `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`; finalized indexed direct references before `2026-10-13T16:19:01Z`. Read-only acquisition; economic cap zero.

Failed history terminates at an empty page after 19,292 unique failed references (21 retained pages, zero duplicates). The wallet itself paid 7,654 of these transactions, costing **8.455562498 SOL**. The remaining fees were paid by other actors and are not this wallet's expense. Every failed wallet native balance delta matches its actual fee debit exactly; no failed non-fee cash residual exists.

Only **2,625 wallet-paid failed transactions / 4.205252519 SOL** have an explicit instruction reference to a cohort mint or a token account proven to hold that cohort mint. This is a bounded cohort-purpose cost witness, even if the transaction stopped before that instruction. The other **5,029 wallet-paid failures / 4.250309979 SOL** contain other token-balance mint witnesses and no cohort instruction witness; retain them outside cohort costs. No unknown wallet-paid failed costs remain under this classification, but other-token balances do not prove exhaustive human purpose. Never subtract all lifetime failed fees from the 279-launch cohort.

The 568 retained creator-fee receipt transactions have 557 wallet-paid network fees totalling **0.004927790 SOL**. The 279 signed launch transactions cost **0.043478743 SOL** in network fees, and wallet-funded system create-account instructions deposit **3.742284662 SOL**. These deposits include refundable rent/custody principal and cannot all be labelled expense. System transfers are retained by destination; a transfer is not labelled tip without destination evidence.

Native wallet deltas already contain fees, setup deposits, refunds, tips and transfers. Do not subtract them a second time from the trading worker's native+WSOL cash ledger. Claim native deltas sum to **1629.019965453 SOL**, which is not the 1660.286830500 SOL-equivalent gross payout total: token custody, funding and other legs must be reconciled. Canonical payout amounts can release rent (known old/current rent reserve 890,880/650,240 lamports); pure fee-origin profit requires those lots separated.

There is one launch/claim overlap and nine allocated trading/claim overlaps. All nine are verified zero-payout distribution events: total payout overlap **0 SOL**, so gross creator payout receipts do not double-count trade cash. Their **0.000115400 SOL** network fees are already counted by trading cash and must not be subtracted twice. Additional fees for all 559 remaining claim-event transactions are **0.004812390 SOL** (548 wallet-paid). Positive SOL/WSOL payouts alone use 555 transactions and **0.004797060 SOL** wallet-paid fees (545 wallet-paid); all have no trading signature overlap.

All cohort-witness wallet-paid failed fees assign to one exact cohort mint each: **4.205252519 SOL**, zero multi-mint ambiguity. `per-mint-failed-fees.json` retains exact signatures and integer cost per mint. `summary.json` groups them by the trading ledger's position status; this permits a closed-position subtotal without subtracting failures from other/open/transfer positions.

Coverage is terminal provider-indexed `tokenAccounts:none` direct wallet history. It does not independently establish arbitrary associated-account history, off-chain spend, other human-owned wallets, ownership of external transfer recipients, USD quote conversion, or the recoverable valuation of open/transferred inventory.

## Reproduce

`python3 work/ramonos-launches-20261013/costs-coverage/analyze.py` derives the ledgers from retained raw history and cohort/claim inputs without network. Acquisition code uses the existing local read-only provider adapter; retained requests omit credentials. `source-manifest.json` pins every source payload. `failed-fee-ledger.json` pins each failure to its payload, signature, payer, fee, scope and instruction witness. `successful-cost-witnesses.json` retains setup and native-transfer evidence without treating refundable deposits as expense.


## Claim native/WSOL cash boundary

All 568 claim-event transactions produce **1629.002187675 SOL** in native plus wallet-owned canonical WSOL cash. The nine zero-distribution trade/configuration overlaps have negative setup cash already included by the trading ledger. Removing their entire cash movements leaves **1629.080316235 SOL** across 559 standalone transactions; this already includes **0.004812390 SOL** successful network fees and **0.244900000 SOL** official Jito tips. Positive SOL/WSOL payout transactions alone (555) produce **1629.081531565 SOL**; that differs from gross payout receipts by **31.205298935 SOL**.

Wallet-source system transfers across all 568 transactions are **31.147216155 SOL**, comprising official Jito tips **0.245600000 SOL** and other destinations **30.901616155 SOL**. Pre/post token owner/mint bindings and parsed initialization/associated creation prove no destination in these transfers is an internal wallet-owned WSOL or other token account. Beneficial ownership and economic purpose of the 166 other destinations remain unproved; do not call all of this business expense. Wallet-funded account creates deposit **0.836804369 SOL**, retained as custody/funding evidence.

The exact native ledger reconciles: 484.061725386 SOL inbound transfers plus 1176.947188381 SOL account-close credits minus 31.147216155 SOL system transfers, 0.836804369 SOL create funding and 0.004927790 SOL fees equals 1629.019965453 SOL native cash. Wallet-owned WSOL changes by -0.017777778 WSOL, yielding the combined native/WSOL cash above. Account-close credits include WSOL unwraps and reserves; they are not additional fee income.

Classification and original transaction source hashes are in `claim-cash-summary.json`; all per-transaction cash and overlap flags with UTC timestamps are in `claim-native-wsol-cash.csv`. Jito recipient identities reuse the pinned public first-party `getTipAccounts` response; official documentation: https://docs.jito.wtf/lowlatencytxnsend/#gettipaccounts. This establishes original-wallet cash rather than the operator's business profit.


## Final full-schema grouping

Final trading ledger SHA-256 `e260be692ada40d0bed2538a984ed8d04d769a2d6b1dc0a88b8d086a552ab909` includes the retained official LaunchLab TradeEvent schema. Closed SOL/WSOL positions total **196**. Their attributable failed fees are **2.294348012 SOL**, leaving **1674.323228104 SOL** associated original-wallet native/WSOL cash after failed fees. All 272 SOL-quote launches retain **4.124842519 SOL** failed costs. Standalone claim cash and the nine zero-payout overlap proof remain unchanged. These are the final hash-bound groups; earlier 195-position figures were superseded by schema closure.
