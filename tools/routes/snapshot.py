import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import sys,pathlib,json,datetime,time,urllib.request,urllib.error,hashlib,subprocess,base64,struct,csv,collections
sys.path.insert(0,str(CODE_ROOT/'tools'));import fee_core as core
OUT=ROOT/'outputs/ramonos-launches-20261013/routes';RAW=OUT/'raw';SDK=CODE_ROOT/'schemas';RENT='SysvarRent111111111111111111111111111111111';TOKEN='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA';TOKEN22='TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb';WALLET='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
for name in ['pump','pump_amm','pump_fees']:
 j=json.loads((RAW/f'{name}-pinned-idl.json').read_text());core.IDLS[j['address']]=j;core.TYPES[j['address']]={t['name']:t['type'] for t in j['types']}
accounts={};values={};receipts=json.loads((OUT/'receipts.json').read_text()) if (OUT/'receipts.json').exists() else [];checks=[];gaps=[]
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2))
def rpc(label,ads):
 params=[ads,{'encoding':'base64','commitment':'finalized'}];req={'jsonrpc':'2.0','id':label,'method':'getMultipleAccounts','params':params};start=utc();rp=RAW/(label+'.request.json');sp=RAW/(label+'.response.json');
 if rp.exists() and json.loads(rp.read_text())['params']!=params:raise RuntimeError('Captured request mismatch')
 if sp.exists():
  res=json.loads(sp.read_text());slot=res['result']['context']['slot']
  for a,v in zip(ads,res['result']['value']):values[a]=v;accounts[a]=core.decode_account(a,v,sp.relative_to(ROOT),slot)
  return
 adapter=core.module('routes_readonly',CODE_ROOT/'tools/rpc_readonly.py');res=adapter.rpc('getMultipleAccounts',params)
 rp.write_text(json.dumps(req));endpoint='configured read-only RPC; credential omitted'
 sp.write_text(json.dumps(res,separators=(',',':')));slot=res['result']['context']['slot'];receipts.append({'startedUtc':start,'completedUtc':utc(),'endpoint':endpoint,'commitment':'finalized','slot':slot,'request':str(rp.relative_to(ROOT)),'response':str(sp.relative_to(ROOT)),'responseSha256':core.sha(sp),'requestSha256':core.sha(rp),'accountCount':len(ads)})
 for a,v in zip(ads,res['result']['value']):
  values[a]=v
  try:accounts[a]=core.decode_account(a,v,sp.relative_to(ROOT),slot)
  except Exception as e:accounts[a]={'address':a,'exists':v is not None,'rawSource':str(sp.relative_to(ROOT)),'slot':slot,'decodeError':str(e)};gaps.append({'address':a,'decodeError':str(e)})
 save('receipts.json',receipts);save('decoded-accounts.json',list(accounts.values()));time.sleep(1)
def fetch(label,ads):
 ads=list(dict.fromkeys(ads))
 for i in range(0,len(ads),100):rpc(f'{label}-{i//100:03}',ads[i:i+100])
from pump_pda import sharing_config, bonding_curve, creator_vault, amm_creator_vault, canonical_pool, quote_ata, social_fee
# Input exclusively uses census-verified signed create + same-transaction mint initialization.
launches=json.loads((ROOT/sys.argv[1]).read_text());launches=launches['launches'] if isinstance(launches,dict) else launches
otherLaunches=[l for l in launches if l['platform']!='Pump'];launches=[l for l in launches if l['platform']=='Pump']
rows=[dict(l,sharingConfig=sharing_config(l['mint']),curve=bonding_curve(l['mint'])) for l in launches];save('derived-route-addresses.json',rows)
fetch('configs-curves',[a for r in rows for a in [r['sharingConfig'],r['curve']]]+[RENT])
for r in rows:
 cd=accounts[r['curve']].get('decoded',{});r['quote']=core.WSOL if cd.get('quote_mint') in [None,core.SOL] else cd['quote_mint'];r['creator']=cd.get('creator');r['configValid']=accounts[r['sharingConfig']].get('type')=='SharingConfig' and accounts[r['sharingConfig']].get('owner')==core.D.FEE_IDL['address'] and accounts[r['sharingConfig']].get('decoded',{}).get('mint')==r['mint']
quotes=list(dict.fromkeys(r['quote'] for r in rows));fetch('quote-mints',quotes)
for r in rows:r['tokenProgram']=accounts[r['quote']].get('owner',TOKEN)
rows=[dict(l,canonicalPool=canonical_pool(l['mint'],l['quote']),cfgVault=creator_vault(l['sharingConfig']),cfgPumpAta=quote_ata(creator_vault(l['sharingConfig']),l['quote'],l['tokenProgram']),cfgAmmAuthority=amm_creator_vault(l['sharingConfig']),cfgAmmAta=quote_ata(amm_creator_vault(l['sharingConfig']),l['quote'],l['tokenProgram'])) for l in rows]
recipients=list(dict.fromkeys(sh['address'] for r in rows if r['configValid'] for sh in accounts[r['sharingConfig']]['decoded']['shareholders']));fetch('pools-recipients',[r['canonicalPool'] for r in rows]+recipients)
# Save initial classification immediately for beneficiary history selection.
social=[a for a in recipients if accounts[a].get('type')=='SocialFeePda' and accounts[a].get('owner')==core.D.FEE_IDL['address']];save('initial-social.json',[accounts[a] for a in social]);save('initial-pools.json',[accounts[r['canonicalPool']] for r in rows]);print('INITIAL '+json.dumps({'launchCount':len(rows),'social':[{**accounts[a]['decoded'],'address':a} for a in social]}),flush=True)
for r in rows:
 pd=accounts[r['canonicalPool']].get('decoded',{});r['poolCreator']=pd.get('coin_creator');r['routeCreators']=list(dict.fromkeys(c for c in [r['creator'],r['poolCreator']] if c));
vaultrows=[dict(mint=l['mint'],creator=c,quote=l['quote'],tokenProgram=l['tokenProgram'],vault=creator_vault(c),pumpAta=quote_ata(creator_vault(c),l['quote'],l['tokenProgram']),ammAuthority=amm_creator_vault(c),ammAta=quote_ata(amm_creator_vault(c),l['quote'],l['tokenProgram'])) for l in rows for c in l['routeCreators']];save('derived-upstream-addresses.json',vaultrows)
satas=[dict(address=a,mint=q,tokenProgram=accounts[q].get('owner',TOKEN),ata=quote_ata(a,q,accounts[q].get('owner',TOKEN))) for a in social for q in quotes]
fetch('vault-custody',[a for v in vaultrows for a in [v['vault'],v['pumpAta'],v['ammAta']]]+[r['ata'] for r in satas]);rb=values.get(RENT);rent=struct.unpack('<QdB',base64.b64decode(rb['data'][0])[:17]) if rb else None

def excess(a):
 x=accounts[a]
 if not x.get('exists'):return '0'
 return str(max(0,int(x['lamports'])-int((128+x['dataLength'])*rent[0]*rent[1]))) if rent else None

def token(a,owner,mint,program):
 v=values[a]
 if v is None:return '0'
 raw=base64.b64decode(v['data'][0]);ok=len(raw)>=165 and v['owner']==program and core.D.b58(raw[:32])==mint and core.D.b58(raw[32:64])==owner;checks.append({'address':a,'check':'token program/mint/authority','passed':ok});return str(int.from_bytes(raw[64:72],'little')) if ok else None
benef=[]
expected=[social_fee(accounts[a]['decoded']['user_id'],int(accounts[a]['decoded']['platform'])) for a in social]
for a,exp in zip(social,expected):
 x=accounts[a];d=x['decoded'];checks.append({'check':'social PDA ID/platform binding','address':a,'expected':exp,'passed':exp==a});benef.append({'address':a,**d,'isUsePaidIntermediary':d['platform']=='2' and d['user_id']=='322216527','nativeLifetimeClaimedLamports':d.get('total_claimed'),'aboveRentLamports':excess(a),'tokenCustody':[{'mint':v['mint'],'ata':v['ata'],'raw':token(v['ata'],a,v['mint'],v['tokenProgram'])} for v in satas if v['address']==a],'slot':x['slot'],'rawSource':x['rawSource'],'counterScope':'All beneficiary lifetime mints; not Ramonos attributable.'})
save('social-beneficiaries.json',benef)
for v in vaultrows:
 v.update(nativeVaultAboveRentLamports=excess(v['vault']),pumpQuoteAtaRaw=token(v['pumpAta'],v['vault'],v['quote'],v['tokenProgram']),ammQuoteAtaRaw=token(v['ammAta'],v['ammAuthority'],v['quote'],v['tokenProgram']));checks.append({'check':'native vault owner','address':v['vault'],'passed':not accounts[v['vault']].get('exists') or accounts[v['vault']].get('owner')==core.SOL})
report=[]
for r in rows:
 c=accounts[r['curve']];p=accounts[r['canonicalPool']];cd=c.get('decoded',{});pd=p.get('decoded',{});cfg=accounts[r['sharingConfig']].get('decoded',{});poolok=p.get('type')=='Pool' and p.get('owner')==core.D.AMM_IDL['address'] and pd.get('base_mint')==r['mint'] and pd.get('quote_mint')==r['quote'];curveok=c.get('type')=='BondingCurve' and c.get('owner')==core.D.IDL['address'];activeCreator=pd.get('coin_creator') if cd.get('complete') is True and poolok else cd.get('creator');activeHolder=pd.get('is_holder_reward') if cd.get('complete') is True and poolok else cd.get('is_holder_reward');configActive=r['configValid'] and activeCreator==r['sharingConfig'];shs=cfg.get('shareholders',[]) if configActive else [];rec=[]
 for sh in shs:
  d=accounts[sh['address']].get('decoded',{});plat=d.get('platform') if sh['address'] in social else None;rec.append({**sh,'platform':plat,'userId':d.get('user_id'),'recipientAccountType':accounts[sh['address']].get('type'),'category':'native donation' if accounts[sh['address']].get('type')=='DonationFeePda' else 'UsePaid GitHub intermediary' if plat=='2' and d.get('user_id')=='322216527' else 'direct GitHub social' if plat=='2' else 'other social' if plat is not None else 'ordinary recipient wallet','shareFractionNumerator':sh['share_bps'],'shareFractionDenominator':'10000'})
 cat='holder rewards' if activeHolder is True else 'GitHub social sharing' if any(v['platform']=='2' for v in rec) else 'other social sharing' if any(v['platform'] is not None for v in rec) else 'native donation sharing' if any(v.get('recipientAccountType')=='DonationFeePda' for v in rec) else 'ordinary wallet sharing' if configActive else 'ordinary creator wallet' if activeCreator and not r['configValid'] else 'ordinary creator wallet (inactive config exists)' if activeCreator and not configActive else 'unknown'
 checks.extend([{'mint':r['mint'],'check':'curve program/PDA','passed':curveok},{'mint':r['mint'],'check':'pool program/PDA/mints if exists','passed':poolok if p.get('exists') else True},{'mint':r['mint'],'check':'config mint/owner if exists','passed':r['configValid'] if accounts[r['sharingConfig']].get('exists') else True}]);report.append({**r,'routeCategory':cat,'activeCreator':activeCreator,'activeHolderReward':activeHolder,'curveHolderReward':cd.get('is_holder_reward'),'poolHolderReward':pd.get('is_holder_reward'),'curveCashback':cd.get('is_cashback_coin'),'poolCashback':pd.get('is_cashback_coin'),'curveComplete':cd.get('complete'),'configActive':configActive,'configStatus':cfg.get('status'),'admin':cfg.get('admin'),'adminRevoked':cfg.get('admin_revoked'),'shareholders':rec,'curvePendingCreatorFeeRaw':cd.get('creator_fee') if curveok else None,'poolPendingCreatorFeeRaw':pd.get('creator_fees') if poolok else None,'custody':[v for v in vaultrows if v['mint']==r['mint']],'curveSlot':c.get('slot'),'poolSlot':p.get('slot'),'curveRaw':c.get('rawSource'),'poolRaw':p.get('rawSource')})

for r in report:
 for sh in r['shareholders']:
  sh['curvePendingFeeFractionFloorRaw']=str(int(r['curvePendingCreatorFeeRaw'])*int(sh['share_bps'])//10000) if r['curvePendingCreatorFeeRaw'] is not None else None
  sh['poolPendingFeeFractionFloorRaw']=str(int(r['poolPendingCreatorFeeRaw'])*int(sh['share_bps'])//10000) if r['poolPendingCreatorFeeRaw'] is not None else None
  sh['allocationNote']='Arithmetic current split applied to separate pending counters; distribution rounding/order and historic split not inferred.'
 checks.append({'mint':r['mint'],'check':'active split totals 10000bps','passed':not r['configActive'] or sum(int(sh['share_bps']) for sh in r['shareholders'])==10000})
save('other-platform-launches.json',[{**l,'routeCategory':'other platform; LaunchLab reviewed separately'} for l in otherLaunches])
save('routes.json',report);save('validation.json',checks);save('derived-social-atas.json',satas);save('decoded-accounts.json',list(accounts.values()))
summary={'launchCount':len(rows),'otherPlatformCount':len(otherLaunches),'totalCensusLaunchCount':len(rows)+len(otherLaunches),'categories':dict(collections.Counter(r['routeCategory'] for r in report)),'socialBeneficiaryCount':len(benef),'githubBeneficiaries':[b for b in benef if b['platform']=='2'],'captureStartedUtc':receipts[0]['startedUtc'],'captureCompletedUtc':receipts[-1]['completedUtc'],'slotMin':min(r['slot'] for r in receipts),'slotMax':max(r['slot'] for r in receipts),'failedChecks':[c for c in checks if not c['passed']],'gaps':gaps,'rentParameters':rent,'limitations':['Current finalized route snapshot spans slots; census historical cutoff separate.','Lifetime beneficiary counters pooled across mints; not creator-attributable.','Vault balances may include arbitrary funding; custody not proven fee revenue.','Missing current layout flags/counters remain null.','UsePaid onward settlement unknown.','Ordinary creator vaults can be shared across many mints: deduplicate by vault/address/quote before any custody sum.','Legacy active holder flag absent is null; ordinary routing relies on actual creator identity and current available flags.']};save('summary.json',summary)
for name,data in [('routes',report),('beneficiaries',benef),('custody',vaultrows)]:
 if not data:continue
 with (OUT/(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for v in data for k in v)));w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in d.items()} for d in data])
(OUT/'REPORT.md').write_text('# Ramonos current fee routes\n\n'+json.dumps(summary,indent=2)+'\n\nAccount bindings, raw requests, response hashes, slots and fractions are retained alongside. No economic effects.\n')
print('FINAL '+json.dumps(summary),flush=True)
