# Reuse this research

Start with REPORT.md, SUMMARY.json and ALL-LAUNCHES.csv. Mint addresses, not names, identify tokens. Source owners, configured recipients, actual receipt addresses and human attribution are distinct.

Claimed means actual receipt at the intended destination. UsePaid collection does not establish the intended developer's claim. Unknown values remain unknown. Do not sum common ordinary creator vault rows across multiple mints; deduplicate actual vault and quote identity. Do not sum token units with SOL or include original funding in fee revenue.

The archive retains this output directory and task computation scripts. Reused tools/decoders are listed in REUSE.json. RPC provider credentials are deliberately excluded. A successor can use a compatible read-only mainnet provider with the recorded exact RPC method/parameters. Public current snapshots can be rerun via ordinary Solana JSON-RPC. Historical receipt replay requires the indexed getTransactionsForAddress method or an equivalent complete signature+transaction acquisition, retaining its coverage and gaps.

Official account/event schemas are captured in routes/raw. Dependencies used were @pump-fun/pump-sdk 4.0.0, official Pump docs commit 639b87fb45c3adeffa6f7c4a1bf0cb85e392bf22, retained official Raydium LaunchLab schemas, Python standard-library decoders and Solana public-key/PDA derivation. Do not import or expose a provider's credentials in a public artifact.

The narrow successor outcome, if more coverage is requested, is another publicly attributable wallet or token creation lead, followed by the same signed-creation test and recipient-level fee replay. Preserve this register and original evidence. Do not relabel all purchases as launches or infer human control of unrelated recipient wallets.
