import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,importlib.util,base64,hashlib,datetime,csv
R=ROOT; O=R/'outputs/ramonos-launches-20261013/launchlab'; O.mkdir(exist_ok=True)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
L=mod('ll',CODE_ROOT/'tools/launchlab_decoder.py'); RPC=mod('rpc',CODE_ROOT/'tools/rpc_readonly.py')
J=json.load(open(CODE_ROOT/'schemas/launchlab.json')); T={t['name']:t['type'] for t in J['types']}; rows=json.load(open(R/'outputs/ramonos-launches-20261013/census/launchlab-creation-details.json')); now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat(); dump=lambda n,x:(O/n).write_text(json.dumps(x,indent=2)+'\n')
addresses=list(dict.fromkeys([r[k] for r in rows for k in ['launchlabPool','launchlabPlatformConfig','launchlabGlobalConfig']]+[L.pda(L.LL,[L.unb58(r['initialCreator']),L.unb58(r['initialQuoteMint'])])['address'] for r in rows])); request={'method':'getMultipleAccounts','params':[addresses,{'encoding':'base64','commitment':'finalized'}],'startedUtc':now(),'spendCapSol':'0'}
p=O/'accounts.json'
if not p.exists():
 response=RPC.rpc(request['method'],request['params']); request['completedUtc']=now(); dump('accounts.json',response);dump('accounts.request.json',request)
else:response=json.load(open(p));request=json.load(open(O/'accounts.request.json'))
decoded={}
for addr,v in zip(addresses,response['result']['value']):
 proof={'address':addr,'exists':v is not None,'slot':response['result']['context']['slot']}
 if v:
  raw=base64.b64decode(v['data'][0]);proof.update(owner=v['owner'],lamports=str(v['lamports']),dataLength=len(raw),dataSha256=hashlib.sha256(raw).hexdigest())
  if v['owner']==L.LL:
   schema=next(a for a in J['accounts'] if bytes(a['discriminator'])==raw[:8]);read=L.Reader(raw,T); d={f['name']:read.value(f['type']) for f in T[schema['name']]['fields']};assert read.pos==len(raw),(addr,read.pos,len(raw));proof.update(type=schema['name'],fields=d,unparsedBytes=0)
  else:
   assert v['owner']=='TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA' and len(raw)==165
   proof.update(type='TokenAccount',fields={'mint':L.b58(raw[:32]),'authority':L.b58(raw[32:64]),'amount':str(int.from_bytes(raw[64:72],'little')),'state':raw[108]})
 decoded[addr]=proof
out=[]
for r in rows:
 d=decoded[r['launchlabPool']]['fields'];platform=decoded[r['launchlabPlatformConfig']]['fields'];glob=decoded[r['launchlabGlobalConfig']]['fields']; assert all(d[a]==r[b] for a,b in [('base_mint','mint'),('creator','initialCreator'),('quote_mint','initialQuoteMint'),('platform_config','launchlabPlatformConfig'),('global_config','launchlabGlobalConfig')]);assert glob['quote_mint']==d['quote_mint']
 vault=L.pda(L.LL,[L.unb58(d['creator']),L.unb58(d['quote_mint'])]);vp=decoded[vault['address']];auth=L.pda(L.LL,[b'creator_fee_vault_auth_seed'])['address']
 if vp['exists']:assert vp['fields']['mint']==d['quote_mint'] and vp['fields']['authority']==auth and vp['fields']['state']==1
 tx=json.load(open(R/'outputs/ramonos-launches-20261013/census'/ (r['mint']+'.transaction.json')));events=[]
 etag=bytes(next(e['discriminator'] for e in J['events'] if e['name']=='TradeEvent'))
 for line in tx['meta']['logMessages']:
  if not line.startswith('Program data: '):continue
  raw=base64.b64decode(line[14:])
  if raw[:8]!=etag:continue
  rd=L.Reader(raw,T);event={f['name']:rd.value(f['type']) for f in T['TradeEvent']['fields']};assert rd.pos==len(raw);assert event['pool_state']==r['launchlabPool'];events.append({'fields':event,'payloadSha256':hashlib.sha256(raw).hexdigest()})
 text=lambda x:bytes(map(int,x)).rstrip(b'\0').decode('utf8',errors='replace')
 out.append({'mint':r['mint'],'name':r['name'],'creationUtc':r['utc'],'creationSignature':r['signature'],'originalCreator':d['creator'],'pool':r['launchlabPool'],'currentStatusRaw':d['status'],'currentStatus':{'0':'funding','1':'awaiting_migration','2':'migration_complete'}[d['status']],'quoteMint':d['quote_mint'],'quoteDecimals':d['quote_decimals'],'platform':r['launchlabPlatformConfig'],'platformName':text(platform['name']),'platformWeb':text(platform['web']),'platformFeeWallet':platform['platform_fee_wallet'],'platformNftWallet':platform['platform_nft_wallet'],'currentCreatorFeeRateMillionths':platform['creator_fee_rate'],'currentCreatorFeePercent':str(int(platform['creator_fee_rate'])/10000),'currentPlatformFeeRateMillionths':platform['fee_rate'],'currentProtocolFeeRateMillionths':glob['trade_fee_rate'],'protocolFeeOwner':glob['protocol_fee_owner'],'migrationFeeOwner':glob['migrate_fee_owner'],'currentLpScales':{k:platform[k] for k in ['platform_scale','creator_scale','burn_scale']},'currentPlatformCpCreator':platform['platform_cp_creator'],'cpSwapConfig':platform['cpswap_config'],'currentPoolPlatformFeeCounterRaw':d['platform_fee'],'currentPoolProtocolFeeCounterRaw':d['quote_protocol_fee'],'creatorFeeVault':vp,'creatorFeeVaultDerivation':vault,'creatorFeeVaultAuthority':auth,'creationTransactionTradeEvents':events,'initialFeeRates':'Unknown: initialize_v2/PoolCreateEvent contain config references but no rates; historical config state not obtained. Exact charged fees in any creation-transaction TradeEvent retained separately.','holderFeeDestination':'No holder-reward recipient field in these LaunchLab pool/config schemas; LP rights and burn scale are separate from creator fees.','githubSocialFeeDestination':'Unproved: no GitHub/social payout destination field in decoded on-chain routing; token metadata is outside this task.'})
dump('decoded-accounts.json',decoded);dump('fee-routing.json',{'readOnly':True,'spendCapSol':'0','request':request,'rows':out}); print(json.dumps(out,indent=2))
