# Independent fee-phase review

**ACCEPT — strict custody attribution correction verified.** Original inputs were preserved; no network, signer, public mutation or spend occurred.

The 135 sharing traces, 22 mint aggregates, source instruction/event bindings and exact gross receipt totals replayed identically against canonical receipts, cash ledgers and original raw transactions. All input hashes match. The 106 AMM bridge credit identities are distinct, no positive repeated native-vault distributions reuse a source credit, and no prior outbound transfer consumes a traced sharing-vault input. Native unwraps are source tracing, not another gross receipt.

The earlier 162.882349165–162.882349242 SOL sharing interval assumed proportional source attribution within fungible mixed custody. At the 100-bps 9KMX distribution, the 34,579,079-lamport untraced opening balance could fund more than its assumed one-percent allocation. A strict custody bound is lower=max(0,P−U), upper=min(P,A), with U=max(0,V−A). Effective A can be clamped to spendable V when the AMM input also funds the retained reserve.

This changes the aggregate sharing interval to **162.867472359–162.882695032 SOL**, and the combined direct-plus-sharing lower bound to **1,339.092577473 / 1,660.286830500 = 80.65429134734%**. The prior lower bound overstates the strict minimum by 0.014876806 SOL. The conclusion that most retained gross payouts passed through AMM custody survives; rounding the corrected lower bound to two decimal places yields 80.65%. PsyopCartoon remains **157.863727454 SOL paid, at least 157.863727383 SOL from same-transaction AMM custody**.

Keep these proof ceilings: 319.655754211 SOL native Pump claims remain origin-phase unresolved; the official generic AMM bridge schema supports ordinary creator vaults. Gross venue custody does not prove pure trading-fee income, mint-exclusive pooled claims, graduation for every AMM pool, or complete ATA-only history.

The exact reviewed artifact hashes and check results are in verification.json. The corrected strict bounds and report were replayed against all 135 raw-backed traces and independently checked row by row. This review is bound to the corrected artifact hashes; no material issue remains within the bounded scope.


This is the Ramonos-only excerpt of the independent review. Portable processors reuse the repository decoder; eight derived documents matched the reviewed results exactly in an isolated offline replay.
