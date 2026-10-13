import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
import pathlib,json,hashlib,collections,importlib.util
P=ROOT/'outputs/ramonos-launches-20261013/census';M=json.loads((P/'history-manifest.json').read_text());L=json.loads((P/'launches.json').read_text());W=M['wallet'];s=importlib.util.spec_from_file_location('core',CODE_ROOT/'tools/fee_core.py');C=importlib.util.module_from_spec(s);s.loader.exec_module(C)
sigs=[];last=-1;fee=[];errs=[];mints={x['mint'] for x in L};counts=collections.Counter()
for pg in M['pages']:
 p=ROOT/pg['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==pg['sha256'];b=json.loads(p.read_text())['result'];assert len(b['data'])==pg['count'];assert b.get('paginationToken')==pg['cursorOut']
 for tx in b['data']:
  assert tx['meta']['err'] is None;assert 0<=tx['blockTime']<M['cutoff'];assert tx['blockTime']>=last;last=tx['blockTime'];sig=tx['transaction']['signatures'][0];sigs.append(sig)
  keys=[C.key(x) for x in tx['transaction']['message']['accountKeys']];assert W in keys
  for ix in C.D.flatten_instructions(tx):
   if ix['programId'] in ('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA','TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'):
    pr=ix.get('parsed');counts['parsedTokenInstruction' if isinstance(pr,dict) else 'unparsedTokenInstruction']+=1
  for e in C.events(tx,pg['path'],errs):
   if e['name'] in {'TradeEvent','BuyEvent','SellEvent','CreateEvent'}:continue
   v=e['event']
   if v.get('mint') in mints or any(z in mints for z in v.values() if isinstance(z,str)):fee.append(e)
assert len(sigs)==len(set(sigs));assert M['terminal'] and M['pages'][-1]['cursorOut'] is None
assert len(L)==len(mints)
for x in L:
 assert W in x['signers'];assert x['mint'] in x['signers'];assert x['mintInitialization']['info']['mint']==x['mint'];assert x['mintInitialization']['signature']==x['signature']
 if x['platform']=='Pump':assert x['createEvent']['event']['user']==W
 else:
  assert x['launchlabInitializeInstruction']['roles']['creator']==W;assert x['launchlabPoolCreateEvent']['event']['creator']==W;assert x['launchlabPoolCreateEvent']['event']['pool_state']==x['launchlabPool'];assert x['launchlabPoolCreateEvent']['event']['base_mint_param']==x['launchlabInitializeInstruction']['args']['base_mint_param']
(P/'fee-routing-events.json').write_text(json.dumps(fee,indent=2));(P/'verification.json').write_text(json.dumps({'success':True,'pages':len(M['pages']),'transactionCount':len(sigs),'uniqueSignatures':len(set(sigs)),'distinctLaunchMints':len(mints),'allLaunchedMintsSigned':True,'successfulOnly':True,'ascendingOrder':True,'rawResponseHashesVerified':True,'terminalPage':M['pages'][-1],'feeRoutingEventCount':len(fee),'decodeErrors':errs,'tokenInstructionCounts':dict(counts)},indent=2));print(json.dumps({'transactions':len(sigs),'launches':len(L),'tokenInstructions':dict(counts),'feeEvents':len(fee),'errors':len(errs)}))
