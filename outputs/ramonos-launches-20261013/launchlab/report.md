# Ramonos: two verified LaunchLab launches — fee routing

Read-only, financial cap 0. Fresh finalized account snapshot 2026-10-13T16:23:23.764599Z–16:23:23.886093Z, slot 456506284. Reused original census birth receipts and 32798 retained transactions; no duplicate RPC capture of birth/history. Both exact pools/config bindings match original creator 57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b and mint. All six program accounts decoded to exact length after owner/discriminator validation; both fee token accounts validated for mint, authority, length and initialized state.

| Mint | Birth | Birth transaction actual creator fee | Current creator fee rate | Current creator/quote vault | Current curve state |
|---|---|---|---|---|---|
| GiqnV6wrZck1od9ruHrakVHXMYNXDEZcUnbPv1scbonk (IMT) | 2026-01-03 00:45:28 UTC | 2 USD1 on 4,000 USD1 buy | 0% | 0.504381 USD1 | funding |
| 7b1otW189NkEpUdiN2P4mVNvrztqnRd9nesAhk3Cbonk (wif) | 2026-04-08 03:57:57 UTC | 0 SOL on 1.488609793 SOL buy | 0% | 0 wSOL | funding |

IMT's initial buy charged protocol 10 USD1, platform 40 USD1 and creator 2 USD1. These realized amounts imply 0.25%, 1%, 0.05% respectively for that trade; they are not an archival config snapshot. Current configs instead give protocol 0.25%, platform 1.25%, creator 0%. Wif initial buy charged 0.003721525 SOL protocol and 0.018607622 SOL platform, with no creator fee. Both initialize_v2 instructions bind config addresses but carry no fee rates, so the historical complete config is unknown.

One successful creator-signed LaunchLab ClaimCreatorFee is proven: 2026-01-03 01:05:33 UTC, [transaction](https://solscan.io/tx/3eJARFuPywa3QeeZin9iggRcbCRFZsvwFQuSEC1cziDbr7QpWvNUCEMBAf2TrNnQTcbqLoFU5EPr2HGcTbUWjz2F), 22.389774 USD1 transferred from creator fee vault 51JEYVzpwQZJvFHyxyUBz8djtJcBKGkmNDewY5vAFNCK to creator's independently derived canonical USD1 ATA 3GeUpU1kWsWrwroemMreE5czDBkRTKN7VR2ypakXbrM5. No successful wSOL ClaimCreatorFee found in retained census. The vaults aggregate creator+quote, so neither this withdrawal nor current balance is asserted to be exclusively earned by the named mint. Zero vault balance is not evidence that no fees ever accrued or were claimed.

Both on-chain platform names are letsbonk.fun; configured current fee wallet is YvWXoyyRpD5fPVZHZV6SY8NS1nuTFmyewxudD3mwuE3, and platform NFT wallet / platform_cp_creator is 5jFLVBsJ6uVdFd89pqfG9eytCLjtqjwcGwTuwYu5ZKQu. Protocol fee owner is rayvTLcCMDs7P5tgpuoNA6ZYeLERegeCphdqLSgdKms; migration fee owner rayHQtJKrtvqUs3HnhDW9RKubHRbu87eESKEYD5xosa. These are configured roles, not proven personal identities or proof of all paid transfers.

Creator fees differ from holder rewards and LP burn/fee rights. Current LP scales are platform 1, creator 0, burn 999999 out of 1,000,000 (0.0001%, 0%, 99.9999%). These are prospective migration settings, not observed completed LP burns. Both pools remain funding; no migrated CPMM fee counter or completed Fee Key ownership is claimed. No GitHub/social payout destination is proven by the decoded routing. Token metadata links alone would not establish a fee recipient.

Primary sources reused: [official IDL](https://github.com/raydium-io/raydium-idl/blob/master/raydium_launchpad/raydium_launchpad.json), pinned interface provenance in schemas/launchlab.source.json and portable decoder in tools/launchlab_decoder.py, and [official creator fee mechanics](https://github.com/raydium-io/raydium-docs-v1/blob/main/products/launchlab/creator-fees.mdx). Current documentation separates bonding-curve creator fees, CPMM creator fees and LP Fee Keys; it also warns migration rules changed in August 2026. Current documentation is not backdated to these launches.

Evidence: fee-routing.json / CSV, decoded-accounts.json, creator-claims.json, accounts.json and request timestamp file; reused birth/history file hashes and source hashes in manifest.json. No sign, send, claim, simulated effect or balance-only historical inference performed.
