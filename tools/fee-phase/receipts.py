"""Offline retained fee-payout source tracing, financial execution cap 0 SOL."""
import json,sys,hashlib,collections,csv,pathlib,re
from decimal import Decimal
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from paths import ROOT, CODE_ROOT
import fee_core as C
OUT=ROOT/'outputs/fee-phase-20261014/ramonos-receipts'
P=ROOT/'outputs/ramonos-launches-20261013/own-fees';W='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b';AMM='pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA';PUMP='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'
receipts=json.loads((P/'verified-receipts.json').read_text());txs=json.loads((P/'transactions.json').read_text());ledgers=json.loads((P/'cash-ledgers.json').read_text());manifest=[];rawpages={};rows=[];seenPayments=set();totals=collections.Counter();mints={};directBridge=[]
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pct(n,d):return str(Decimal(n)*100/Decimal(d))
for path in [CODE_ROOT/'schemas/pump.json',CODE_ROOT/'schemas/pump_fees.json',CODE_ROOT/'schemas/pump_amm.json',CODE_ROOT/'tools/fee_core.py',CODE_ROOT/'tools/decoder.py']:
 manifest.append({'path':str(path.relative_to(CODE_ROOT)),'sha256':sh(path)})
for path in [P/'verified-receipts.json',P/'transactions.json',P/'cash-ledgers.json']:
 manifest.append({'path':str(path.relative_to(ROOT)),'sha256':sh(path)})
for r in receipts:
 source=r['rawSource']
 if source not in rawpages:
  rawpages[source]={t['transaction']['signatures'][0]:t for t in C.rows(source)};manifest.append({'path':source,'sha256':sh(ROOT/source)})
 assert txs[r['signature']]==rawpages[source][r['signature']],r['signature']
 t=txs[r['signature']]; evs=C.events(t,source);matches=[e for e in evs if e['payloadSha256']==r['payloadSha256'] and e.get('logIndex')==r.get('logIndex')]
 assert len(matches)==1 and matches[0]['event']==r['event']
 if not r['verified']:continue
 assert all(r['checks'].values()) and r['walletCashLedgerMatches']
 for payment in r['payments']:
  identity=(r['signature'],payment['topIndex'],payment['source'],payment['destination'],payment['amount'],payment.get('type','token_transfer'))
  assert identity not in seenPayments,identity
  seenPayments.add(identity)
 totals[r['name']]+=r['amountLamports']
 if r['name']!='DistributeCreatorFeesEvent':continue
 v=r['sourceVault'];eventTop=sum(bool(re.fullmatch(r'Program \w+ invoke \[1\]',l)) for l in t['meta']['logMessages'][:r['logIndex']+1])-1;dist=[i for i in C.instructions(t,source) if i['name'] in ['distribute_creator_fees','distribute_creator_fees_v2'] and i['accounts'].get('creator_vault')==v and i['accounts'].get('mint')==r['event']['mint'] and i['topLevelInstructionIndex']==eventTop]
 assert len(dist)==1,(r['signature'],r['event']['mint'],dist);d=dist[0]
 transfers=[]
 for ix in C.D.flatten_instructions(t):
  p=ix.get('parsed',{});info=p.get('info',{})
  if ix['programId']==C.SOL and p.get('type')=='transfer' and info.get('destination')==v and ix['topLevelInstructionIndex']<d['topLevelInstructionIndex']:
   transfers.append({'amountLamports':int(info['lamports']),'source':info['source'],'destination':v,'parentProgram':ix['parentProgram'],'topLevelInstructionIndex':ix['topLevelInstructionIndex'],'innerInstructionIndex':ix['innerInstructionIndex']})
 amm=[]
 for x in transfers:
  if x['parentProgram']!=AMM:continue
  ins=[i for i in C.instructions(t,source) if i['name'] in ['transfer_creator_fees_to_pump','transfer_creator_fees_to_pump_v2'] and i['topLevelInstructionIndex']==x['topLevelInstructionIndex'] and i['accounts']['pump_creator_vault']==v and i['accounts']['coin_creator_vault_authority']==x['source'] and i['accounts']['coin_creator']==r['event']['sharing_config']]
  assert len(ins)==1,(r['signature'],x,C.instructions(t,source));bindings=ins[0]['accounts'];assert bindings.get('wsol_mint',bindings.get('quote_mint'))==C.WSOL
  close=[ix for ix in C.D.flatten_instructions(t) if ix['topLevelInstructionIndex']==x['topLevelInstructionIndex'] and ix.get('parsed',{}).get('type')=='closeAccount' and ix.get('parsed',{}).get('info',{}).get('account')==bindings['coin_creator_vault_ata']]
  assert len(close)==1
  token=ledgers[r['signature']]['tokenAccountBindings'][bindings['coin_creator_vault_ata']];assert token['mint']==C.WSOL and token['owner']==x['source']
  x['instructionBinding']=ins[0];x['wsolSourceBinding']=token;amm.append(x)
 A=sum(x['amountLamports'] for x in amm);V=r['availableBeforeDistributionLamports'];B=r['shareBps'];paid=r['amountLamports'];unknownAvailable=max(0,V-A)
 # Strict fungible-custody bounds: source lots need not pay recipients proportionally.
 # Incoming AMM credit that establishes retained rent is not spendable payout custody.
 Aeffective=min(A,V);unknownAvailable=V-Aeffective
 lo=max(0,paid-unknownAvailable);hi=min(paid,Aeffective)
 assert lo<=hi and A<=V+r['observedRetainedVaultReserveLamports']
 row={'signature':r['signature'],'utc':r['utc'],'slot':r['slot'],'mint':r['event']['mint'],'signedLaunchCohort':r['cohortMint'],'shareBps':B,'paidLamports':paid,'availableBeforeDistributionLamports':V,'ammSameTransactionTransferredLamports':A,'ammSpendableInputLamports':Aeffective,'untracedSpendableOpeningLamports':unknownAvailable,'ammOriginPaidLowerBoundLamports':lo,'ammOriginPaidUpperBoundLamports':hi,'unresolvedPaidUpperBoundLamports':paid-lo,'rawSource':source,'eventPayloadSha256':r['payloadSha256'],'distributionInstruction':d,'ammTransfers':amm,'pureTradingFeeOriginProved':False}
 rows.append(row)
 mint=mints.setdefault(row['mint'],collections.Counter());
 for key in ['paidLamports','ammOriginPaidLowerBoundLamports','ammOriginPaidUpperBoundLamports','unresolvedPaidUpperBoundLamports']:mint[key]+=row[key]
 mint['receiptCount']+=1;mint['signedLaunchCohort']=r['cohortMint']
for sig,t in txs.items():
 for i in C.instructions(t,'retained payout transaction'):
  if i['name'] in ['transfer_creator_fees_to_pump','transfer_creator_fees_to_pump_v2'] and i['accounts'].get('pump_creator_vault')=='9shGVTC47GaHPVFGJGEBxK6VQ9yTdsw83eW83L423S6o':directBridge.append(i)
assert dict(totals)=={'CollectCreatorFeeEvent':319655754211,'CollectCoinCreatorFeeEvent':1176225105114,'DistributeCreatorFeesEvent':164405971175}
T=sum(totals.values());SL=sum(r['ammOriginPaidLowerBoundLamports'] for r in rows);SU=sum(r['ammOriginPaidUpperBoundLamports'] for r in rows)
summary={'wallet':W,'retainedCutoffUtc':'2026-10-13T16:19:01Z','verifiedPayoutReceiptsLamports':T,'pumpNativeClaimsVenueUnresolvedLamports':totals['CollectCreatorFeeEvent'],'pumpAMMDirectClaimsLamports':totals['CollectCoinCreatorFeeEvent'],'mintBoundSharingReceiptsLamports':totals['DistributeCreatorFeesEvent'],'sourceAllocationMethod':'Strict fungible custody bounds; no proportional source-lot assumption','sharingAMMOriginLowerBoundLamports':SL,'sharingAMMOriginUpperBoundLamports':SU,'sharingUnresolvedUpperBoundLamports':totals['DistributeCreatorFeesEvent']-SL,'directAMMShareOfAllGrossPayoutReceiptsPercent':pct(totals['CollectCoinCreatorFeeEvent'],T),'directPlusSharingAMMOriginLowerBoundLamports':totals['CollectCoinCreatorFeeEvent']+SL,'directPlusSharingAMMOriginLowerBoundPercentOfAllGrossPayoutReceipts':pct(totals['CollectCoinCreatorFeeEvent']+SL,T),'pumpNativeClaimShareOfAllGrossPayoutReceiptsPercent':pct(totals['CollectCreatorFeeEvent'],T),'sharingShareOfAllGrossPayoutReceiptsPercent':pct(totals['DistributeCreatorFeesEvent'],T),'sharingMints':len(mints),'sharingEvents':len(rows),'observedAMMBridgesIntoOrdinaryWalletNativeVaultInPayoutTransactions':directBridge,'ordinaryWalletNativeVaultAMMBridgePossible':True,'pureTradingFeeOriginProved':False,'limitations':['Gross payouts may include released funding/rent or unrelated deposits; venue-bound payout is not independent pure fee-origin revenue proof.','319.655754211 SOL Pump native claims are pooled custody and cannot be called curve-earned without source-history replay; generic AMM transfer_creator_fees_to_pump supports ordinary creators.','Sharing untraced opening custody can contain earlier curve fees, earlier AMM fees, funding or other inflows.','Direct claims pool mints, no per-token allocation supplied. Sharing mint binding is actual distribute instruction/event, not an arbitrary pool mint assignment.','PumpAMM venue does not by itself independently prove canonical pool graduation for every token.','All history is original wallet-referencing finalized success scope; ATA-only references are not complete.']}
OUT.mkdir(parents=True,exist_ok=True)
for name,x in [('summary.json',summary),('sharing-source-traces.json',rows),('per-mint-sharing.json',mints),('input-manifest.json',manifest)]: (OUT/name).write_text(json.dumps(x,indent=2)+'\n')
with (OUT/'per-mint-sharing.csv').open('w') as f:
 fields=['mint','signedLaunchCohort','receiptCount','paidLamports','ammOriginPaidLowerBoundLamports','ammOriginPaidUpperBoundLamports','unresolvedPaidUpperBoundLamports'];w=csv.DictWriter(f,lineterminator='\n',fieldnames=fields);w.writeheader();w.writerows({'mint':m,**v} for m,v in mints.items())
(OUT/'ordinary-native-vault-bridge-schema.json').write_text(json.dumps(next(i for i in C.IDLS[AMM]['instructions'] if i['name'] in ['transfer_creator_fees_to_pump','transfer_creator_fees_to_pump_v2']),indent=2)+'\n')
print(json.dumps(summary,indent=2))
