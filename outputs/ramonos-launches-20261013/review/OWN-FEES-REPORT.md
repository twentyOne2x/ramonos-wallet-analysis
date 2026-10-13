# Independent own-fee payout review

PASS: 5,787 controls in own-fees-validation.json. No network calls, financial effects or other owners' source/output edits.

All 851 event payloads and selected successful transactions bind to exact retained census raw sources. 845 verified receipts comprise 368 native Pump claims, 342 wallet-owned WSOL PumpAMM claims and 135 native sharing distributions. Six other-quote Pump events are excluded: 16,305,517 USDC raw units and 137,934,053,001 PUMP raw units. Units are kept separate.

Actual receipts total 1,660,286,830,500 lamports-equivalent: 319,655,754,211 native Pump + 1,176,225,105,114 WSOL + 164,405,971,175 native sharing. Exact payment identities are unique: no intermediate-vault sweep or WSOL unwrap is double counted. All WSOL destinations bind to wallet ownership and WSOL mint, with actual source debit and parsed payment equal to the event. Native claims bind canonical source vault debit and exact wallet transfer.

All 568 transaction cash ledgers independently reconstruct the wallet's actual postbalance exactly after network fees, other native transfers, funding, WSOL transfer lamports and closes. Sharing receipts additionally match independently reconstructed running source balances, actual complete shareholder payment totals and the recorded reserve-based floor allocation. Zero events remain in the counts.

Sharing distributions cover 22 mints: 15 signed-deployer cohort mints paid 159,013,155,704 lamports; seven other mints paid 5,392,815,471. Pooled direct creator vaults prevent assigning the complete wallet payout total exclusively to the 279 signed-deployer launches. This is gross protocol payout-instruction receipt evidence, not independent proof every paid lamport originated from trading fees, net profit or strict cohort earnings. ATA-only histories are not separately enumerated.

Current-route ratios are 265/277 = 95.6678700361% receiving at least a partial creator allocation and 263/277 = 94.9458483755% receiving the full creator allocation. Denominator is current Pump routes; the two LaunchLab coins remain separate.
