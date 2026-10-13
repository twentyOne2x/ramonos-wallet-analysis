import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import json,pathlib,hashlib,csv,importlib.util
R=ROOT;O=R/'outputs/ramonos-launches-20261013/launchlab'; data=json.load(open(O/'fee-routing.json'));claims=json.load(open(O/'creator-claims.json'));s=importlib.util.spec_from_file_location('L',CODE_ROOT/'tools/launchlab_decoder.py');L=importlib.util.module_from_spec(s);s.loader.exec_module(L)
for c in claims['claims']:
 a=c['roles'];derived=L.pda('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL',[L.unb58(a['creator']),L.unb58(a['token_program']),L.unb58(a['quote_mint'])])['address'];assert derived==a['recipient_token_account'];c['recipientCanonicalCreatorAtaValidated']=True
(O/'creator-claims.json').write_text(json.dumps(claims,indent=2)+'\n')
flat=[]
for row in data['rows']:
 v=row['creatorFeeVault'];row['currentQuoteVaultBalanceUi']=str(int(v['fields']['amount'])/10**int(row['quoteDecimals']));row['creatorVaultBalanceIsMintSpecific']=False;row['creatorVaultClaimability']='Protocol creator/quote PDA with validated mint and authority; balance readback only, no simulation or signing.';row['successfulCreatorQuoteClaims']=[c for c in claims['claims'] if c['successful'] and c['roles']['quote_mint']==row['quoteMint']];flat.append({k:v for k,v in row.items() if isinstance(v,(str,int,bool))})
(O/'fee-routing.json').write_text(json.dumps(data,indent=2)+'\n')
with (O/'fee-routing.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
report='''# Ramonos: two verified LaunchLab launches — fee routing

Read-only, financial cap 0. Fresh finalized account snapshot 2026-10-13T16:23:23.764599Z–16:23:23.886093Z, slot 456506284. Reused original census birth receipts and 33,000+ retained transactions; no duplicate RPC capture of birth/history. Both exact pools/config bindings match original creator 57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b and mint. All six program accounts decoded to exact length after owner/discriminator validation; both fee token accounts validated for mint, authority, length and initialized state.

| Mint | Birth | Birth transaction actual creator fee | Current creator fee rate | Current creator/quote vault | Current curve state |
|---|---|---|---|---|---|
| GiqnV6wrZck1od9ruHrakVHXMYNXDEZcUnbPv1scbonk (IMT) | 2026-01-03 00:45:28 UTC | 2 USD1 on 4,000 USD1 buy | 0% | 0.504381 USD1 | funding |
| 7b1otW189NkEpUdiN2P4mVNvrztqnRd9nesAhk3Cbonk (wif) | 2026-04-08 03:57:57 UTC | 0 SOL on 1.488609793 SOL buy | 0% | 0 wSOL | funding |

IMT's initial buy charged protocol 10 USD1, platform 40 USD1 and creator 2 USD1. These realized amounts imply 0.25%, 1%, 0.05% respectively for that trade; they are not an archival config snapshot. Current configs instead give protocol 0.25%, platform 1.25%, creator 0%. Wif initial buy charged 0.003721525 SOL protocol and 0.018607622 SOL platform, with no creator fee. Both initialize_v2 instructions bind config addresses but carry no fee rates, so the historical complete config is unknown.

One successful creator-signed LaunchLab ClaimCreatorFee is proven: 2026-01-03 01:05:33 UTC, [transaction](https://solscan.io/tx/3eJARFuPywa3QeeZin9iggRcbCRFZsvwFQuSEC1cziDbr7QpWvNUCEMBAf2TrNnQTcbqLoFU5EPr2HGcTbUWjz2F), 22.389774 USD1 transferred from creator fee vault 51JEYVzpwQZJvFHyxyUBz8djtJcBKGkmNDewY5vAFNCK to creator's independently derived canonical USD1 ATA 3GeUpU1kWsWrwroemMreE5czDBkRTKN7VR2ypakXbrM5. No successful wSOL ClaimCreatorFee found in retained census. The vaults aggregate creator+quote, so neither this withdrawal nor current balance is asserted to be exclusively earned by the named mint. Zero vault balance is not evidence that no fees ever accrued or were claimed.

Both on-chain platform names are letsbonk.fun; configured current fee wallet is YvWXoyyRpD5fPVZHZV6SY8NS1nuTFmyewxudD3mwuE3, and platform NFT wallet / platform_cp_creator is 5jFLVBsJ6uVdFd89pqfG9eytCLjtqjwcGwTuwYu5ZKQu. Protocol fee owner is rayvTLcCMDs7P5tgpuoNA6ZYeLERegeCphdqLSgdKms; migration fee owner rayHQtJKrtvqUs3HnhDW9RKubHRbu87eESKEYD5xosa. These are configured roles, not proven personal identities or proof of all paid transfers.

Creator fees differ from holder rewards and LP burn/fee rights. Current LP scales are platform 1, creator 0, burn 999999 out of 1,000,000 (0.0001%, 0%, 99.9999%). These are prospective migration settings, not observed completed LP burns. Both pools remain funding; no migrated CPMM fee counter or completed Fee Key ownership is claimed. No GitHub/social payout destination is proven by the decoded routing. Token metadata links alone would not establish a fee recipient.

Primary sources reused: [official IDL](https://github.com/raydium-io/raydium-idl/blob/master/raydium_launchpad/raydium_launchpad.json), factual read-only ABI subset and source revision/hash in schemas/launchlab.source.json, and [official creator fee mechanics](https://github.com/raydium-io/raydium-docs-v1/blob/main/products/launchlab/creator-fees.mdx). Current documentation separates bonding-curve creator fees, CPMM creator fees and LP Fee Keys; it also warns migration rules changed in August 2026. Current documentation is not backdated to these launches.

Evidence: fee-routing.json / CSV, decoded-accounts.json, creator-claims.json, accounts.json and request timestamp file; reused birth/history file hashes and source hashes in manifest.json. No sign, send, claim, simulated effect or balance-only historical inference performed.
'''
report=report.replace('33,000+ retained transactions',str(claims['uniqueTransactionsScanned'])+' retained transactions');(O/'report.md').write_text(report)
paths=list(O.glob('*'))+[R/'outputs/ramonos-launches-20261013/census/launchlab-creation-details.json']+[R/'outputs/ramonos-launches-20261013/census'/(r['mint']+'.transaction.json') for r in data['rows']]
(O/'manifest.json').write_text(json.dumps({'spendCapSol':'0','readOnly':True,'schemas':[{'path':str(p.relative_to(CODE_ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((CODE_ROOT/'schemas').rglob('*')) if p.is_file()],'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths if p.is_file() and p.name!='manifest.json']},indent=2)+'\n');print(claims['uniqueTransactionsScanned'])
