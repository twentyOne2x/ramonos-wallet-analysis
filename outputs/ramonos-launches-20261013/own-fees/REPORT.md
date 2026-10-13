# Ramonos own creator-fee receipts

**1,660.286830500 SOL-equivalent was actually paid to the disclosed wallet by verified Pump creator-fee payouts in the retained history, through 2026-10-13 16:19:01 UTC.**

Wallet: `57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b`.

| Receipt mechanism | Verified receipt events | Actual own payments |
|---|---:|---:|
| Direct Pump native creator claim | 368 | 319.655754211 SOL |
| PumpAMM claim to wallet-owned wrapped-SOL account | 342 | 1,176.225105114 WSOL |
| Native creator-fee sharing distributions | 135 | 164.405971175 SOL |
| Total, counting WSOL once | 845 | 1,660.286830500 SOL-equivalent |

The 135 sharing events cover 22 mints. Fifteen mints belong to the 279 signed-deployer launch cohort and paid **159.013155704 SOL**; seven historical mints outside that cohort paid **5.392815471 SOL**. Their actual historical share percentages are used, including historical 10% and 20% shares, rather than today's routes. The earlier 157.953292234 SOL subtotal was only eight ordinary-sharing cohort mints and is not the complete wallet receipt total.

Direct creator vaults pool multiple mints. The total above is therefore all retained on-chain creator-fee receipts to this wallet, not a proven exclusive revenue total for its 279 signed-deployer launches. A separate unsigned-deployer token can share the same fee creator. LaunchLab's independently verified 22.389774 USD1 is a separate asset and is excluded. Six Pump events quoted in USDC/PUMP are also excluded: their raw event totals are 16,305,517 USDC units and 137,934,053,001 PUMP units. They are not SOL and are not added to this table.

## Verification

Every selected successful transaction is retained. Current SDK 4.0.0 official Pump/PumpAMM/Fee IDL event discriminators and typed fields were used; 851 own-recipient events decoded without errors. Historical absent trailing quote fields do not imply an asset: native parsed transfers and the source vault debit independently establish SOL. Direct native claims match canonical creator-vault-to-wallet System transfers and vault pre/post debit. All 342 AMM receipts match exact source/destination token transfers, WSOL mint, wallet recipient ownership and source token pre/post debit. Transfers to sharing intermediaries are not included as wallet claims. WSOL close/unwrapping proceeds are reconciled and counted once.

All 568 selected transaction wallet balances reconstruct exactly using network fees, parsed native transfers, account funding, token transfer lamports for WSOL and account closure proceeds. Rent refunds and other transfers explain balances but do not become fee income. Native sharing payments match exact derived config creator vaults, the complete actual shareholder transfer sum and each integer-floor share of the available pre-distribution balance. Recorded retained reserves of 890,880 and 650,240 lamports explain historical rounding and reserve changes; allocation is not calculated by flooring the already-rounded event distributed total. Zero-value events remain in event counts.

## Coverage and limits

The source census has terminal 34-page pagination covering 32,798 successful finalized wallet-reference transactions, through the fixed cutoff. Every raw page SHA-256 was checked before decoding. The provider query used tokenAccounts=none, so this proves retained wallet-reference receipts; it does not independently enumerate all transactions referencing only a wallet-owned token account. No new network query, transaction, signature or economic action was performed. The source capture begins with the wallet's earliest retained reference on 2025-10-17; this is a provider-history coverage statement, not a separate genesis proof.

These are gross actual creator-fee payout instruction receipts. They are not net profit, and a canonical creator vault can receive non-fee funding; this work does not independently prove the origin of every claimed vault lamport. Fee events, actual verified payments and pooled-versus-mint attribution are kept separate in the evidence.

`verified-receipts.json` / `receipts.csv` bind every event to signature, slot, original raw source, exact payments and checks. `cash-ledgers.json` supplies native balances, fees, transfers, token bindings and reconstructed balances. `events.json`, `transactions.json`, `derived-config-vaults.json`, `summary.json` and `manifest.json` retain the reproducible inputs and outputs.
