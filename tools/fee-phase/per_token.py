"""Offline mint register and source-bound accrual subsets; no network/effects."""
import json,csv,hashlib,pathlib,collections,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from paths import ROOT
B=ROOT/'outputs/ramonos-launches-20261013'; O=ROOT/'outputs/fee-phase-20261014/per-token'
O.mkdir(parents=True,exist_ok=True)
launches=json.load(open(B/'census/launches.json')); routes={r['mint']:r for r in json.load(open(B/'routes/routes.json'))}; accounts={r['address']:r for r in json.load(open(B/'routes/decoded-accounts.json'))}; ll={r['mint']:r for r in json.load(open(B/'launchlab/fee-routing.json'))['rows']}
register=[]; subset=[]; sources=set()
def rel(p): return str(p.relative_to(ROOT))
for l in launches:
 r=routes.get(l['mint']); row={'mint':l['mint'],'name':l['name'],'platform':l['platform'],'creationSignature':l['signature'],'creationSlot':l['slot'],'creationUtc':l['utc'],'creationSource':l['rawSource'],'beforeGraduationLifetimeCreatorFeesRaw':None,'afterGraduationLifetimeCreatorFeesRaw':None,'lifetimeFeeCoverage':'unproved; retained wallet history and pending counters are insufficient','migrationSignature':None,'migrationUtc':None}
 if r:
  c=accounts.get(r['curve'],{}); p=accounts.get(r['canonicalPool'],{}); pd=p.get('decoded',{}); validated_pool=p.get('exists') is True and p.get('type')=='Pool' and pd.get('base_mint')==l['mint'] and str(pd.get('index'))=='0'
  status='canonical_amm_pool_present' if validated_pool else ('curve_complete_pool_not_observed' if r['curveComplete'] is True else 'curve_incomplete_pool_not_observed' if r['curveComplete'] is False else 'unknown')
  row.update(quoteMint=r['quote'],quoteDecimals=9 if r['quote']=='So11111111111111111111111111111111111111112' else None,curve=r['curve'],canonicalPool=r['canonicalPool'],migrationStatus=status,migrationStatusSource=r['poolRaw'] if validated_pool else r['curveRaw'],curveComplete=r['curveComplete'],canonicalPoolExists=p.get('exists'),curveSnapshotSlot=c.get('slot'),poolSnapshotSlot=p.get('slot'),curveUnsweptCreatorFeesRaw=r.get('curvePendingCreatorFeeRaw'),poolUnsweptCreatorFeesRaw=r.get('poolPendingCreatorFeeRaw'))
 else:
  d=ll[l['mint']]; row.update(quoteMint=d['quoteMint'],quoteDecimals=int(d['quoteDecimals']),curve=d['pool'],canonicalPool=None,migrationStatus='launchlab_'+d['currentStatus'],migrationStatusSource=rel(B/'launchlab/fee-routing.json'),curveComplete=None,canonicalPoolExists=None,curveSnapshotSlot=456506284,poolSnapshotSlot=None,curveUnsweptCreatorFeesRaw=None,poolUnsweptCreatorFeesRaw=None)
  for e in d['creationTransactionTradeEvents']:
   v=e['fields']; subset.append({'mint':l['mint'],'name':l['name'],'phase':'before_graduation','sourcePhase':'launchlab_funding_trade','scope':'creation transaction only; not lifetime','amountRaw':v['creator_fee'],'quoteMint':d['quoteMint'],'quoteDecimals':int(d['quoteDecimals']),'signature':l['signature'],'slot':l['slot'],'payloadSha256':e['payloadSha256'],'source':rel(B/'launchlab/fee-routing.json'),'verification':'retained decoded TradeEvent binds pool_state and Fund pool_status'})
 register.append(row)
by_mint={r['mint']:r for r in register}
for f in sorted((B/'target-vaults').glob('*/replay.json')):
 d=json.load(open(f)); s=d['summary']; mint=s['mint']; sources.add(rel(f));
 if f.parent.name.startswith('amm-latest-'):
  # Proven post-migration source bucket since exact zero checkpoint; not lifetime.
  if s.get('feeProvenanceReconciled') is True:
   subset.append({'mint':mint,'name':by_mint[mint]['name'],'phase':'after_graduation','sourcePhase':'pump_canonical_amm','scope':'verified inflows since retained exact-zero ATA checkpoint; not lifetime','amountRaw':s['verifiedCreatorFeeInRaw'],'quoteMint':by_mint[mint]['quoteMint'],'quoteDecimals':by_mint[mint]['quoteDecimals'],'checkpointSignature':s['baselineSignature'],'lowerBound':s['lowerBound'],'cutoffUtc':s['cutoffUtc'],'source':rel(f),'verification':'retained feeProvenanceReconciled=true; exact zero checkpoint + uninterrupted replay'})
  continue
 events={(e['signature'],e['payloadSha256']):e for e in d.get('events',[]) if e['name']=='TradeEvent' and e.get('program')=='6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P'}
 for tx in d.get('transactions',[]):
  for detail in tx.get('details',[]):
   if detail.get('name')!='TradeEvent' or detail.get('verified') is not True: continue
   e=events.get((tx['signature'],detail['payloadSha256']));
   if not e or e['event'].get('mint')!=mint:continue
   v=e['event']; tokenreserve=v.get('real_token_reserves'); before= tokenreserve is not None and int(tokenreserve)>0 and detail.get('instructionName') in ('buy','sell','buy_exact_sol_in','buy_v2','sell_v2','buy_exact_quote_in_v2')
   subset.append({'mint':mint,'name':by_mint[mint]['name'],'phase':'before_graduation' if before else 'curve_source_completion_boundary_unknown','sourcePhase':'pump_bonding_curve','scope':'verified configuration-era trade only; earlier route history may be missing','amountRaw':detail['amountLamports'],'quoteMint':by_mint[mint]['quoteMint'],'quoteDecimals':9,'signature':tx['signature'],'slot':tx['slot'],'utc':tx['utc'],'payloadSha256':detail['payloadSha256'],'source':rel(f),'rawSource':tx['rawSource'],'verification':detail['verification'],'postTradeRealTokenReservesRaw':tokenreserve})
# Deduplicate exactly the same event or same AMM checkpoint aggregate.
seen=set();clean=[]
for r in subset:
 k=(r['mint'],r.get('signature'),r.get('payloadSha256'),r.get('checkpointSignature'))
 assert k not in seen,k
 seen.add(k);clean.append(r)
subset=clean
aggregates=[]
for mint in sorted({s['mint'] for s in subset}):
 for phase in sorted({s['phase'] for s in subset if s['mint']==mint}):
  rr=[s for s in subset if s['mint']==mint and s['phase']==phase]; assets={(s['quoteMint'],s['quoteDecimals']) for s in rr}; assert len(assets)==1
  quote,dec=next(iter(assets)); aggregates.append({'mint':mint,'name':by_mint[mint]['name'],'phase':phase,'observedSubsetCreatorFeesRaw':str(sum(int(s['amountRaw']) for s in rr)),'quoteMint':quote,'quoteDecimals':dec,'evidenceRows':len(rr),'isLifetime':False,'sources':sorted({s['source'] for s in rr})})
for name,obj in [('mint-register.json',register),('verified-phase-subset-events.json',subset),('verified-phase-subset-summary.json',aggregates)]: (O/name).write_text(json.dumps(obj,indent=2)+'\n')
with open(O/'mint-register.csv','w') as f:
 w=csv.DictWriter(f,lineterminator='\n',fieldnames=list(register[0]));w.writeheader();w.writerows(register)
summary={'mintCount':len(register),'migrationStatusCounts':dict(collections.Counter(r['migrationStatus'] for r in register)),'exactLifetimeBeforeGraduationCount':sum(r['beforeGraduationLifetimeCreatorFeesRaw'] is not None for r in register),'exactLifetimeAfterGraduationCount':sum(r['afterGraduationLifetimeCreatorFeesRaw'] is not None for r in register),'verifiedSubsetMintCount':len({s['mint'] for s in subset}),'verifiedSubsetEvidenceRows':len(subset),'readOnly':True,'economicEffectsSol':'0','newNetworkCalls':0,'nullMeans':'unknown, not zero','inputHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'census/launches.json',B/'routes/routes.json',B/'routes/decoded-accounts.json',B/'launchlab/fee-routing.json']+[ROOT/s for s in sorted(sources)]}}
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='inputHashes'},indent=2));print(json.dumps(aggregates,indent=2))
