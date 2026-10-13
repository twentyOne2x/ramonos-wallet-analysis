# Ramonos disclosed-wallet launch census

**279 verified new token launches signed by `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`: 277 Pump, 2 Raydium LaunchLab.** This is the complete terminal provider-indexed successful direct-wallet reference history for this address through fixed exclusive cutoff **2026-10-13T16:19:01Z**, not a census of every wallet controlled by a human.

## Coverage and launch test

Captured 32,798 successful transaction references in 34 ascending finalized pages, from 2025-10-17T20:23:08Z through 2026-10-13T16:16:28Z. Page 32 contains 798 rows and a continuation token; page 33 contains zero rows with no continuation token. Raw response/request timestamps, exact method/parameters, hashes and cutoff are retained. No economic effects; cap 0 lamports.

A counted Pump launch requires successful actual Pump CreateEvent, disclosed wallet signer and `event.user` deployer, and same-signature parsed mint initialization. Every counted mint also signed. LaunchLab launches additionally match official retained `initialize_v2` account roles/arguments and PoolCreateEvent creator/pool/metadata, decoded with zero trailing bytes. All 133,897 SPL Token/Token-2022 instructions in this history are parsed; no unparsed token instructions were encountered. All 32,798 signatures are unique; response hashes, ascending times, successful status, exact cutoff and terminal page verified. Decoder errors: zero.

Purchases and token transfers are not launches. One third-party RAM/Ramonos creation (`xSPpDPb9qU7qgiwZ8hpmAucE5M91FqJn6LjKpNbvump`, 2026-01-17) appears in the wallet reference history but wallet did not sign it; it was created by `6pg9s1bVUhpdZBZkAi5BedoF6bU4Bxynxdw1uHhRDiF5` and is excluded.

## First, last and cadence

- First: **nippip**, 2025-12-17T20:37:55Z, `2TuMmzmC2oaKXWwE7VhWAAD7ggjrtDNGbG8RFeHFpump`.
- Last: **Verified Coin / VERIFIED**, 2026-09-22T00:49:23Z, `HjD79aBPVvqFA9xkLworGzfDvmajEcncnEFLEU4cpump`.
- Launches occurred on **107 UTC days** and **32 ISO UTC weeks**. Peak day: **2026-05-09, 13 launches**. Peak week: **2026-W35, 29 launches**. Between first and last creation, 279/280 calendar days = 0.996 launches/day; active-day mean = 2.607. No further counted launch through cutoff.
- Daily/weekly frequency rows are in `daily-cadence.csv`, `weekly-cadence.csv`; rows include active periods only.

## Initial creator and native flags

276 of 279 creation receipts name the disclosed wallet as initial creator (274 Pump + both LaunchLab). Three Pump events name another on-chain creator, all with native `is_holder_reward=true`:

| Token | Mint | Initial creator |
|---|---|---|
| Diamond Hands | HJE2DEZXvErwUabTU16xzrS629qXVeVyTGvJYJVfpump | Ai8cniP7Pqd24Shex5SeoZizGLxAJ2xhxRhf4w2ZMNUL |
| Pussy Up, Money Printer | wvbhVMz7iknR8DqYEccWfJqdGRWSwzTwnk7cJePpump | GjdpCJ5e7VeogHzHP4Z3ktRHbuVU4dT1SQyxfEn9dDyk |
| Peccy | CKAwvahwXueRcid9F4FZkbinyzp1F2c1wPnQ2QnRpump | Hq1XhosYq8FU1SSadFBrCeoW5cAKzXBeRVoQu7aJAx5D |

Pump initial holder-reward flag: true 3, false 3, absent in historical payload 271. Missing historical fields stay unknown; they are never reconstructed as false. Current fee routes are a separate finalized-account snapshot owned by the fee-route worker; creation events alone do not prove current recipients or human control of those recipient addresses. `fee-routing-events.json` retains 179 selected mint-linked non-trade events observed in this wallet reference history; it does not prove complete third-party fee administration.

LaunchLab IMT (`GiqnV6wrZck1od9ruHrakVHXMYNXDEZcUnbPv1scbonk`) was created 2026-01-03T00:45:28Z with USD1 quote; dog wif pahlavi/wif (`7b1otW189NkEpUdiN2P4mVNvrztqnRd9nesAhk3Cbonk`) was created 2026-04-08T03:57:57Z with WSOL quote. Both exact creation instructions and PoolCreateEvents identify disclosed wallet as creator. Named native flags and initial fee parameters are retained when present; fee destinations require program-specific account interpretation.

## Files and proof ceiling

`launches.csv` is the compact complete 279-mint register with explorer URLs. `launches.json` includes CreateEvent, mint-initialization and LaunchLab creation details. `history-manifest.json`, raw page/request files and `verification.json` bind the terminal provider evidence. `excluded.json` retains the unsigned creation. Reused provider adapter and decoders stay read-only; credentials/endpoints are omitted.

The X post is a public self-attribution lead, not cryptographic human-ownership proof. Other undisclosed wallets are outside this census. Provider-indexed direct-wallet references do not establish every action performed through another account or private infrastructure. Metadata names/symbols/URIs here are on-chain creation values, not fetched off-chain JSON. Token names can be duplicated; mint addresses are canonical.
