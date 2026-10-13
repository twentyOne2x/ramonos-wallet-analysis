"""Offline quote-asset, CPI transfer and wallet-cash proof; no network."""
import os,pathlib,json,collections,hashlib
ROOT=pathlib.Path(os.environ.get('RAMONOS_RESEARCH_ROOT',pathlib.Path.cwd())).resolve();P=ROOT/'outputs/ramonos-launches-20261013/trading';J=json.loads((P/'capital-ledger.json').read_text());W=J['wallet'];WS='So11111111111111111111111111111111111111112';S='11111111111111111111111111111111';by=collections.defaultdict(list);counts=collections.Counter()
for row in J['launches']:
 assert row['inventoryLedgerMatchesLastObserved'] and row['cashComponentSumMatches']
 for tx in row['economicTransactions']:by[tx['rawSource']].append((row,tx))
for source,rows in by.items():
 data={t['transaction']['signatures'][0]:t for t in json.loads((ROOT/source).read_text())['result']['data']}
 for row,entry in rows:
  tx=data[entry['signature']];keys=[a['pubkey'] if isinstance(a,dict) else a for a in tx['transaction']['message']['accountKeys']];groups={g['index']:g['instructions'] for g in tx['meta'].get('innerInstructions',[])};counts['allocatedCashComponents']+=1
  if entry['kind']!='exact_target_ata_reserve_refund_component':
   native=tx['meta']['postBalances'][keys.index(W)]-tx['meta']['preBalances'][keys.index(W)];wsol=0
   for stage,sign in [('preTokenBalances',-1),('postTokenBalances',1)]:
    for v in tx['meta'].get(stage,[]):
     if v['owner']==W and v['mint']==WS:wsol+=sign*int(v['uiTokenAmount']['amount'])
   assert int(entry['nativeDeltaLamports'])==native and int(entry['ownedWsolDeltaRaw'])==wsol and int(entry['nativeWsolDeltaLamports'])==native+wsol
   counts['wholeTransactionCashBalances']+=1
  for trade in entry.get('trades',[]):
   if trade['venue']=='Pump':
    v=trade['eventWitness']['event'];q=v.get('quote_mint');q=WS if q in [None,S] else q;assert q==row['quoteMint'];counts['pumpEventsQuoteIdentity']+=1
   if trade['venue']=='PumpSwap':
    total=0
    for leg in trade['actualQuoteTransferWitness']:
     info=groups[leg['topLevelInstructionIndex']][leg['innerInstructionIndex']]['parsed']['info'];assert info['mint']==row['quoteMint'];amount=int(info.get('amount',info.get('tokenAmount',{}).get('amount',0)));assert str(amount)==leg['amountRaw'];total+=amount;counts['ammActualQuoteTransferLegs']+=1
    assert total==int(trade['actualQuoteTransferRaw']);counts['ammTradesActualTransferTotals']+=1
   if trade['venue']=='LaunchLab':
    event=trade['eventWitness'];parent=event['topLevelInstructionIndex'];ix=tx['transaction']['message']['instructions'][parent];accounts=ix['accounts'];assert accounts[0]==W and accounts[9]==row['mint'] and accounts[10]==row['quoteMint'];qacct=accounts[6];total=0
    for transfer in groups.get(parent,[]):
     p=transfer.get('parsed',{});info=p.get('info',{}) if isinstance(p,dict) else {}
     if p.get('type') not in {'transfer','transferChecked'}:continue
     if (trade['isBuy'] and info.get('source')==qacct) or (not trade['isBuy'] and info.get('destination')==qacct):
      if info.get('mint') is not None:assert info['mint']==row['quoteMint']
      total+=int(info.get('amount',info.get('tokenAmount',{}).get('amount',0)));counts['launchlabActualQuoteTransferLegs']+=1
    assert total==int(trade['actualQuoteTransferRaw']),(entry['signature'],total,trade['actualQuoteTransferRaw']);counts['launchlabPayerMintAndQuoteChecks']+=1
   actual=int(trade['actualQuoteTransferRaw']);principal=int(trade['quoteRaw']);fees=int(trade['venueFeesRaw']);assert actual==(principal+fees if trade['isBuy'] else principal-fees);counts['quotePrincipalFeesActual']+=1
assert not J['decoderErrors']
proof={'success':True,'counts':dict(counts),'capitalLedgerSha256':hashlib.sha256((P/'capital-ledger.json').read_bytes()).hexdigest(),'sourceManifestSha256':hashlib.sha256((ROOT/'outputs/ramonos-launches-20261013/census/history-manifest.json').read_bytes()).hexdigest(),'financialExecutionCapLamports':'0','scope':'Retained successful direct-wallet references and exact allocated transaction components. Failed history and ATA-only history remain separate.'};(P/'verification.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
