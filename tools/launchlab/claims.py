import sys as _sys, pathlib as _pathlib
_sys.dont_write_bytecode = True
_sys.path.insert(0, str(next(p for p in _pathlib.Path(__file__).resolve().parents if (p/'paths.py').is_file())))
from paths import ROOT, CODE_ROOT
exec(open(CODE_ROOT/'tools/launchlab/analyze.py').read().split('addresses=list')[0])
schema=next(i for i in J['instructions'] if i['name']=='claim_creator_fee');tag=bytes(schema['discriminator']);claims=[];seen=set()
for p in sorted((R/'outputs/ramonos-launches-20261013/census/raw').glob('page-*.json')):
 body=json.load(open(p))
 if 'result' not in body:continue
 for tx in body['result']['data']:
  sig=tx['transaction']['signatures'][0]
  if sig in seen:continue
  seen.add(sig)
  for ix in L.instructions(tx):
   if ix.get('programId')!=L.LL or not ix.get('data') or L.unb58(ix['data'])[:8]!=tag:continue
   roles={a['name']:L.key(k) for a,k in zip(schema['accounts'],ix['accounts'])}
   assert roles['creator']=='57rXqaQsvgyBKwebP2StfqQeCBjBS4jsrZFJN5aU2V9b'
   assert roles['creator_fee_vault']==L.pda(L.LL,[L.unb58(roles['creator']),L.unb58(roles['quote_mint'])])['address']
   transfers=[]
   for q in L.instructions(tx):
    parsed=q.get('parsed',{});info=parsed.get('info',{})
    if parsed.get('type') in ['transfer','transferChecked'] and info.get('source')==roles['creator_fee_vault'] and info.get('destination')==roles['recipient_token_account']:
     transfers.append(info)
   signers=[L.key(k) for k in tx['transaction']['message']['accountKeys'] if isinstance(k,dict) and k.get('signer')];assert roles['creator'] in signers
   claims.append({'signature':sig,'slot':tx['slot'],'blockTime':tx.get('blockTime'),'utc':L.utc(tx['blockTime']) if tx.get('blockTime') else None,'successful':tx['meta']['err'] is None,'roles':roles,'matchingTransfers':transfers,'rawSource':str(p.relative_to(R)),'rawSourceSha256':L.sha(p)})
dump('creator-claims.json',{'coverage':'Retained complete original creator transaction census; per creator+quote fee vault withdrawals are not mint-specific','uniqueTransactionsScanned':len(seen),'claims':claims});print(json.dumps(claims,indent=2))
