# Ramonos launch and fee destination analysis

**The disclosed wallet created 279 tokens. It usually keeps creator fees: 263 of its 277 Pump launches currently allocate 100% to the disclosed wallet. One directly targets GitHub, one uses UsePaid, and three use native holder rewards.**

REUSE existing signed-creation, Pump fee-account, receipt, and official LaunchLab decoding tools. Extend the existing forensic workspace for this wallet; no product, account, signing or financial effects.

The [supplied X post](https://x.com/ramonos/status/2097225944180424705) calls `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b` his wallet and says he uses multiple wallets. The address is a wallet. Public own-launch posts for KYOGRE, CHANCE and FREECOIN match its actual signed mint creation receipts. This report covers all verified launches from this disclosed address, not every wallet the human might control.

## Full disclosed-wallet history and current fee routes

32,798 unique successful finalized transaction references were captured through 2026-10-13T16:19:01Z, with terminal pagination. Each counted mint matches an actual creation event, wallet and mint signatures, and same-transaction mint initialization. Purchases and an unsigned third-party RAM creation are excluded.

| Current destination category | Launches |
|---|---:|
| 100% disclosed launcher | 263 |
| wallet split including disclosed launcher | 2 |
| other wallet addresses; ownership unknown | 6 |
| direct GitHub recipient | 1 |
| UsePaid intermediary | 1 |
| native donation | 1 |
| native holder rewards | 3 |
| LaunchLab | 2 |

The first launch was nippip on December 17, 2025; the last was VERIFIED on September 22, 2026. There were 107 active UTC days, averaging 2.61 launches on those days. Across the 280 calendar days from first to last launch, the mean was 1.00/day. Peak day: May 9, 13 launches. Peak week: 2026-W35, 29. No later launch from this wallet appears through the October 13 cutoff. Daily and weekly tables retain exact source counts.

The three holder coins are Diamond Hands, “Pussy Up, Money Printer,” and Peccy. Their current authoritative flags are true. Five ordinary route accounts have absent legacy holder flags and retain null; their recorded fee creator remains the disclosed wallet. [Pump's holder documentation](https://github.com/pump-fun/pump-public-docs/blob/639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22/docs/HOLDER_REWARDS_README.md) says native holder mode redirects the creator allocation to holders and pays holders automatically; the token creator has no creator fees to claim. This is distinct from unclaimed GitHub developer fees. Actual holder distribution performance was not audited here.

## Claimed and unclaimed mean payment to the intended destination

| Launch | Intended recipient | Current allocation | Claimed by intended developer | Verified fees still unclaimed / settlement |
|---|---|---:|---:|---|
| [Flightradar24](https://pump.fun/coin/4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump) | [Flightradar24 GitHub](https://github.com/Flightradar24), ID 12810712 | 100% | 0 SOL | 0.146041920 SOL unclaimed |
| [Bold](https://pump.fun/coin/EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM) | Metadata says @boldleonidas; native recipient is UsePaid | 100% | Unknown | 0.620058647 SOL generated; downstream settlement unknown |

For Flightradar24, 0.010778206 SOL of mint-tagged fees waits in its social account and 0.135263714 SOL waits in its upstream creator vault. That is **one direct GitHub target, zero claimed targets, one unclaimed target, and 100% of its verified assigned native fees unclaimed**. The social replay excludes 0.002136720 SOL initial account funding; the vault replay excludes 0.000890880 SOL historical funding. Lower current rent frees some original funding, which is not fee revenue. A final same-slot account read at 456509511 confirms the social claim counter remains zero, balances match the replays, and both social splits remain 100%.

Bold's actual creator-vault receipts prove 0.618888685 SOL sent to UsePaid and 0.001169962 SOL still upstream. Its public launch metadata says “Fees to @boldleonidas.” Payment to UsePaid is an intermediary movement. It does not establish that @boldleonidas claimed or did not claim the money. UsePaid's pooled lifetime counters span other launchers and are excluded.

Across eight ordinary wallet-sharing routes, **59.245135418 SOL actually reached nonseed wallet addresses**. Wallet recipients already receive funds once distribution runs; they do not face a GitHub authentication claim. Their human ownership remains unknown and they may be additional Ramonos wallets. The current source-reconciled pending fee amount is 0.609924971 SOL before per-address current share allocation. An additional 0.006466356 WSOL is verified from exact zero-balance checkpoints through terminal finalized history, for 0.616391327 SOL equivalent across separate native SOL and WSOL custody. Current allocation floors leave one raw unit of dust. The two AMM native vaults each retain 240,641 lamports whose fee-versus-funding provenance is unknown and excluded. Old full ATA histories remain explicitly partial; current pending proof does not require those old histories. Unswept curve/pool counters remain separate in the route register and are not folded into this custody subtotal. Address receipt totals can include proven funding releases; they are not automatically pure fee revenue or external-developer income. Donation fees are a separate native DonationFeePda route.

Both LaunchLab tokens use letsbonk.fun platform configurations, with current creator fee rate zero and no GitHub/social recipient established. A creator-signed 22.389774 USD1 transfer to the creator's canonical USD1 account is verified. The current 0.504381 USD1 creator vault spans creator and quote asset, so it cannot establish one mint's earnings. USD1 is not added to SOL totals.

## What the 50/50 model can support

A future regular coin can use defined 5,000/5,000-bps recipients. That could leave half for a named developer to claim and half for the platform. [Official fee-sharing instructions](https://github.com/pump-fun/pump-public-docs/blob/639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22/docs/instructions/CREATOR_FEE_SHARING.md) say the V2 final update first distributes pending funds to the old recipients, then revokes further updates. Existing assigned unclaimed social money does not become platform revenue because its recipient has not claimed it. Holder mode is a separate election, rather than an ordinary developer/platform split.

Had the same two social launches generated the same fees under a 50% platform allocation, the hypothetical platform gross would be **0.3831 SOL over their observed lives**, before expenses. This is not an annual forecast. A meaningful annual estimate requires the frequency of qualifying launches, their realized fee distribution, concentration in a few successful tokens, and capital/operating costs. This disclosed wallet supplies only one direct GitHub fee example; it does not establish a large recurring pool of abandoned developer fees.

## Handoff and evidence

- `ALL-LAUNCHES.csv`: all 279 mints, signed creation receipts, current destination category, shares and bounded claim status.
- `FEE-RECIPIENTS.csv`: every native sharing recipient and exact address allocation.
- `census/`: complete successful address-reference capture, daily/weekly tables, exclusions and verification.
- `routes/`: all 277 current Pump account routes, official IDL pins, recipient and custody bindings.
- `target-fees/`: full direct GitHub social history and exact funding/fee conservation.
- `target-vaults/`: native distribution receipts, fee provenance, recipient receipts and any gaps.
- `launchlab/`: official-program interpretation and actual quote-asset withdrawal proof.
- `identity/`: public social attribution and source URL/hash records; full webpage captures stay outside the public export.
- `review/`: independent checks of creation, pagination, route bindings, amounts and receipt movement.
- `final-check/`: same-slot current recheck of both social routes.

All reads use finalized chain state and retained exact parameters, timestamps, raw sources and hashes. The census, social replay, vault histories and current snapshots have distinct stated cutoffs; they are not presented as one atomic lifetime audit. Financial execution cap remained 0 SOL. Other undisclosed wallets and UsePaid onward developer settlement remain outside verified coverage.
