import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,importlib.util,base64,hashlib,csv
P=ROOT/'outputs/ramonos-launches-20261013/census'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
L=mod('llread',CODE_ROOT/'tools/launchlab_decoder.py');j=json.loads((CODE_ROOT/'schemas/launchlab.json').read_text());T={x['name']:x['type'] for x in j['types']};IX={bytes(x['discriminator']):x for x in j['instructions']};event=next(e for e in j['events'] if e['name']=='PoolCreateEvent');launches=json.loads((P/'launches.json').read_text());details=[]
for launch in launches:
 if launch['platform']!='Raydium LaunchLab':continue
 tx=json.loads((P/(launch['mint']+'.transaction.json')).read_text());matches=[]
 for ix in L.instructions(tx):
  if ix['programId']!=j['address'] or not ix.get('data'):continue
  raw=L.unb58(ix['data']);schema=IX.get(raw[:8])
  if not schema or schema['name']!='initialize_v2':continue
  r=L.Reader(raw,T);args={a['name']:r.value(a['type']) for a in schema['args']};assert r.pos==len(raw)
  roles={a['name']:L.key(b) for a,b in zip(schema['accounts'],ix['accounts'])};assert roles['base_mint']==launch['mint'];assert roles['payer'] in launch['signers'];matches.append({'instruction':schema['name'],'roles':roles,'args':args,'dataSha256':hashlib.sha256(raw).hexdigest(),'unparsedBytes':len(raw)-r.pos})
 assert len(matches)==1
 ev=[]
 for index,line in enumerate(tx['meta']['logMessages']):
  if not line.startswith('Program data: '):continue
  raw=base64.b64decode(line[14:])
  if raw[:8]!=bytes(event['discriminator']):continue
  r=L.Reader(raw,T);vals={f['name']:r.value(f['type']) for f in T['PoolCreateEvent']['fields']};assert r.pos==len(raw);ev.append({'event':vals,'logIndex':index,'payloadSha256':hashlib.sha256(raw).hexdigest(),'unparsedBytes':len(raw)-r.pos})
 assert len(ev)==1
 v=matches[0];e=ev[0]['event'];print(json.dumps({'mint':launch['mint'],'instruction':v,'event':ev},indent=2))
 launch.update(name=v['args']['base_mint_param']['name'],symbol=v['args']['base_mint_param']['symbol'],uri=v['args']['base_mint_param']['uri'],initialCreator=v['roles']['creator'],initialQuoteMint=v['roles']['quote_mint'],launchlabPool=v['roles']['pool_state'],launchlabPlatformConfig=v['roles']['platform_config'],launchlabGlobalConfig=v['roles']['global_config'],launchlabInitializeInstruction=v,launchlabPoolCreateEvent=ev[0]);details.append(launch)
(P/'launches.json').write_text(json.dumps(launches,indent=2));(P/'launchlab-creation-details.json').write_text(json.dumps(details,indent=2))
fields=['utc','name','symbol','mint','platform','deployer','initialCreator','initialCreatorFeeBps','initialHolderReward','initialCashbackEnabled','initialQuoteMint','signature','transactionUrl','rawSource']
with (P/'launches.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(launches)
