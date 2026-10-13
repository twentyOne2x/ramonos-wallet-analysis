# Native creator-vault provenance

Read-only finalized histories through exclusive cutoff 2026-10-13T16:28:38Z; terminal provider pagination for each of 11 exact vaults. Raw requests include timestamps, exact parameters and response hashes. No effects or signing.

| Route | Transactions | Exact distribution paid (lamports) | Proven minted fee lots still in vault | Current above rent (includes possible old funding) |
|---|---:|---:|---:|---:|
| Flightradar24 | 410 | 10778206 | 135263714 | 135504354 |
| Bold | 510 | 618888685 | 1169962 | 1169962 |
| PsyopCartoon | 218 | 210484969915 | None | 240641 |
| this coin will retire you | 1309 | 4751598910 | None | 240641 |
| The Jailed Bull | 15 | 0 | 0 | 0 |
| Bold The Frog | 1231 | 894483013 | 1159235 | 1399875 |
| TRANSEXUAL COIN | 84 | 75395967 | None | 0 |
| Justice For Hsin-Ju | 579 | 0 | 485250644 | 485491284 |
| Pump Cat | 465 | 329017111 | 0 | 240640 |
| Copyrighted Cat © | 638 | 630607838 | 23857 | 264497 |
| RAM | 275 | 107750865 | 123491235 | 123491235 |

Flightradar24 exact minted creator fees 146041920 minus 10778206 distributions leaves 135263714 fee lamports. Historical account funding 890880 is excluded, including 240640 now above lower current rent. Its distribution reached direct GitHub SocialFeePda; parent destination replay proves no target claims. Bold exact minted fees 620058647 minus 618888685 distributions leaves 1169962 fee lamports. Its distributions reached UsePaid SocialFeePda; target developer settlement remains unknown.

Trade creator/config and mint, instruction account vault and payload SHA are bound to exact event-CPI top-level index. Buy fees use actual system transfer amount. Sell program direct lamport mutations use exact transaction cash equality after independent funding transfers. Distribution checks sum actual native transfers from exact vault to event shareholders at the exact top-level index, including multiple distributions of same mint in one transaction.

Ordinary payments are address-level credited balances, not inferred human ownership. Two AMM-heavy ordinary routes retain unresolved native inflows; no pending fee lots are inferred for them. TRANSEXUAL COIN donation distributions exceed minted fees by 240640 historical funding freed by lower rent; treat its DonationFeePda separately and do not claim these as developer/GitHub fees. Proven ordinary pending is currently split arithmetically by configured shares; historical payouts use actual recipients and amounts.

Current account readbacks are later than cutoff; all last-history postbalances match these current balances. Rent source is captured RentSysvar in routes/raw/configs-curves-005.response.json, [5080,1.0,50], (128+dataLength)*5080; historical creation funding remains distinct.

## AMM pending follow-up

Current AMM custody is now proven from each exact final successful ATA close (post-token balance zero) through all subsequent ATA references to the same exclusive cutoff. PsyopCartoon: 53 references, 4210952 WSOL raw units of creator fees; this coin will retire you: 6 references, 2255404 WSOL raw units. Each fee binds pool, base mint, WSOL quote, sharing-config creator, exact derived creator ATA and exact event-CPI instruction to actual SPL transferChecked. No unexplained token movements or decode errors; both terminal post-token balances match finalized current account amounts.

These proofs live in amm-latest-*/replay.json. They close current AMM pending provenance independently of historical entire-ATA replay. Historical full-ATA capture retains partial coverage and does not establish historical fee-income totals. Native unwrap receipts are in amm-native-unwraps.json; 6/6 retire and 92/94 Psyop unwraps exactly match pre-WSOL token balances, while two Psyop sweeps include additional authority-native lamports. Those extra lamports remain unexplained rather than automatically labeled trading fees. Native escrow balances 890881 each and current above-rent240641 remain distinct from proven WSOL pending.

Proven ordinary remaining custody combines 609924971 native SOL fee lamports and 6466356 WSOL raw fee units, totaling 616391327 lamports-equivalent (0.616391327 SOL), before per-recipient allocation floor dust. Native SOL vaults and WSOL ATAs are disjoint custody. Each of the two AMM routes also holds native above-rent240641 whose precise fee-versus-other funding attribution remains unknown and excluded. Parent requested stop of unnecessary historical full-ATA capture after the current pending checkpoint proofs completed; owned capture process terminated, retained historical coverage explicitly partial.
