# Ramonos gross receipts by source venue

Wallet: `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`. Retained successful finalized wallet-reference history cutoff: 2026-10-13 16:19:01 UTC. No new claims, transfers, spend, or network acquisition.

The denominator is **1,660.286830500 SOL-equivalent gross creator-payout receipts**, combining native SOL and canonical WSOL without counting unwraps again. This is actual original-wallet receipt accounting, not an independent proof of pure trading-fee income or profit.

| Payout channel | Original-wallet gross receipts | Percent of all gross receipts | Venue conclusion |
|---|---:|---:|---|
| Direct PumpAMM WSOL claims | 1,176.225105114 SOL | 70.844693% | PumpAMM custody; pooled across mints |
| Direct Pump native claims | 319.655754211 SOL | 19.253044% | Origin venue unresolved; pooled across mints |
| Mint-bound sharing payouts | 164.405971175 SOL | 9.902263% | Mixed source custody; traced below |

Sharing transaction traces identify **162.867472359–162.882695032 SOL** of the original wallet's payouts as coming from PumpAMM WSOL unwraps and native transfers immediately preceding distribution. The interval reflects strict source-custody uncertainty: fungible source lots need not pay individual recipients proportionally. At most **1.538498816 SOL** of sharing payouts remains untraced to a source venue here.

Thus direct PumpAMM claims plus the conservative sharing lower bound are **1,339.092577473 / 1,660.286830500 SOL = 80.654291347340781%** of all gross payout receipts. This establishes that most retained gross payout receipts came through PumpAMM custody. It does not independently establish graduation for every pool or pure fee generation.

**Do not call the remaining 319.655754211 SOL “before graduation.”** The official `transfer_creator_fees_to_pump` schema derives the native Pump vault from a generic `coin_creator`; it does not require that creator to be a sharing config. Consequently an ordinary original-wallet creator vault can hold AMM-origin transfers, rent/funding and other native inflows. No such ordinary-vault AMM bridge appears among the retained 568 payout transactions, but those transactions do not supply the vault's full inflow history.

## Per-token evidence

[Per-mint sharing CSV](per-mint-sharing.csv) and [JSON](per-mint-sharing.json) cover 22 actual mint-bound distribution identities. Attribution binds the mint-bearing distribution instruction/event to its sharing-config vault and the exact original-wallet recipient. These are **sharing payouts only**: direct pooled claims cannot be distributed over these mints or the 279 signed launches without additional source provenance.

| Mint | Sharing paid | PumpAMM origin lower bound | Unresolved upper bound |
|---|---:|---:|---:|
| `DAAXmRU9KUEuyqF8VuddbcL5X4QhQ3tTDMYxDbNgpump` | 157.863727454 | 157.863727383 | 0.000000071 |
| `A6FJ12TYV8K79QovsWzkZEC5PWPD7EFzvC4JKZsypump` | 5.252602907 | 4.985253353 | 0.267349554 |
| `FVQ6JzKRz9GfxNv8wDR14xQMRyweeMoXZbjPtukYpump` | 0.875823725 | 0 | 0.875823725 |
| `9KMXMkzyiiKnubfjFkND54zJdnE1EmUyYowq8A3ipump` | 0.089564780 | 0.018491623 | 0.071073157 |

All table amounts are SOL equivalents. Zero in the traced source column means this bounded replay did not identify same-transaction AMM input; it does not establish curve origin. Noncohort distributions remain included as actual wallet receipts, clearly marked in the CSV.

## Verification and exact bounds

[Source traces](sharing-source-traces.json) retain every signature, slot, raw page, event payload hash, distribution instruction, AMM instruction, WSOL account binding and transfer location. Every retained receipt transaction was matched exactly against its original raw page; event payloads were re-decoded using the retained official schemas. Receipt payments were checked for duplicate instruction identities. The strict source bounds were corrected after independent review identified a proportional source-allocation assumption in one mixed payout. The three original-wallet receipt totals were independently summed and matched exact raw integer totals. Raw inputs were preserved.

For each distribution, V is spendable native custody before payout, A is verified same-transaction PumpAMM native input, and P is actual wallet payment. The AMM input remaining available for distribution is Aeffective = min(A,V), accounting conservatively for incoming credit retained as rent. Untraced spendable custody U = V−Aeffective. The strict AMM-origin payout bounds are:

- Lower = max(0, P−U).
- Upper = min(P, Aeffective).

These are fungible-custody bounds: they do not assume each source lot pays the original wallet in proportion to its basis-point share. The whole observed payout uses the actual historical share and is preserved. The trace checks A ≤ V + retained reserve. Opening residue, including earlier curve fees, earlier AMM transfers, funding and unrelated deposits, remains unresolved. No amount of opening residue is relabeled as curve-origin merely because the distribution executes through Pump.

Reproduction: run `python3 tools/fee-phase/receipts.py` with RAMONOS_RESEARCH_ROOT pointing to the isolated replay workspace. [Input hashes](input-manifest.json) bind the retained pages, ledger, receipt inputs and decoder schemas. This computation is local and read only toward all original inputs. Wallet-reference history excludes ATA-only references; successful fee payouts do not represent failed network-fee history.
