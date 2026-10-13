# Ramonos current fee routes

All 279 verified launches are covered: 277 Pump accounts were snapshotted; the two Raydium LaunchLab launches are explicitly delegated to the separate LaunchLab analysis. These are current finalized routes, not historical creation defaults.

| Current Pump route | Launches |
|---|---:|
| Ordinary creator wallet (the disclosed Ramonos wallet) | 258 |
| Native sharing to ordinary wallets | 13 |
| Native donation sharing | 1 |
| Native GitHub social sharing | 2 |
| Native holder rewards | 3 |

The two GitHub routes are Flightradar24 (`4wKXnowo19MuWeuhjfCbiVaWM1WNSkjsqWPYwymxpump`) → numeric ID 12810712, and Bold (`EiDpY9QApxYMFYhR4TWXEpy6gANh73S4h3t8eSif32SM`) → UsePaid numeric ID 322216527. Each has an active 100% split. No other social platform appears. Flightradar24's beneficiary lifetime native claim counter is zero; its current above-rent balance is 0.011355366 SOL. Its config creator vault holds 0.135504354 SOL above rent, independently of the curve's zero pending creator-fee counter. Bold's config vault holds 0.001169962 SOL above rent. Both have absent canonical pools and zero observed quote token custody.

UsePaid's native lifetime claim counter is 52,313.813492020 SOL across all its mints and its stable lifetime raw counter is 19,555,437,862,363. Neither is Ramonos-attributable. Its last claim timestamp, 2026-10-13T16:20:52Z, is after the historical census cutoff; no onward settlement is established.

Diamond Hands (`HJE2DEZXvErwUabTU16xzrS629qXVeVyTGvJYJVfpump`), Pussy Up, Money Printer (`wvbhVMz7iknR8DqYEccWfJqdGRWSwzTwnk7cJePpump`), and Peccy (`CKAwvahwXueRcid9F4FZkbinyzp1F2c1wPnQ2QnRpump`) have authoritative current holder-reward flags true. The first two are complete and use valid bound PumpAMM pools; Peccy remains on its curve. Five active route holder flags are absent in legacy account layouts and remain null. They have the ordinary Ramonos creator identity; null has not been changed into false.

All 16 sharing configurations currently match the authoritative active curve/pool creator; nine have admin revoked and seven do not. TRANSEXUAL COIN's recipient is a verified native DonationFeePda, not an ordinary wallet. Native fee account type, account owner and recorded mint distinguish it.

The account capture ran 2026-10-13 16:22:04–16:22:38 UTC at finalized slots 456505923–456506077. Census cutoff is 16:19:01 UTC. This is a multi-slot snapshot. Official pinned IDLs at `639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22` exactly match installed SDK 4.0.0 route-account schemas. Raw IDLs, requests, responses, hashes, rent parameters, owners, discriminators, PDA derivations, mint and quote bindings are retained. All recorded validation checks pass.

`routes.json` / `routes.csv` contain each launch, active route, share basis points and separate counter allocations. Fractions are applied with integer floor to each available pending fee counter, not to an invented combined total. Missing counters remain null. `social-beneficiaries.json` / `beneficiaries.csv` retain pooled lifetime counters and current custody. Vault above-rent or token balances may contain arbitrary funding and are custody, not proven fee revenue. Ordinary creator vaults span many mints: deduplicate address/quote before any sum. No historical fees, direct claims or global revenue total is inferred from this snapshot. No economic effects were performed.
