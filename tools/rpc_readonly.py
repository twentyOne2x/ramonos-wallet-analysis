"""Allowlisted read-only Solana acquisition; economic cap 0 SOL, no signer.
Offline replay is the default; new observations require RAMONOS_ALLOW_NETWORK=1.
"""
import json, os, urllib.request
ALLOWED_METHODS=frozenset({'getAccountInfo','getMultipleAccounts','getTransactionsForAddress','getAsset','getTransaction','getSignaturesForAddress','getSlot','getBalance','getTokenAccountBalance','getMinimumBalanceForRentExemption'})
PUBLIC_ENDPOINT='https://api.mainnet-beta.solana.com'
def rpc(method,params):
 if method not in ALLOWED_METHODS:raise ValueError('RPC method outside the read-only allowlist')
 if os.environ.get('RAMONOS_ALLOW_NETWORK')!='1':raise RuntimeError('Missing retained response; offline mode. A separate observation requires RAMONOS_ALLOW_NETWORK=1.')
 endpoint=os.environ.get('RAMONOS_RPC_URL',PUBLIC_ENDPOINT)
 if method in {'getTransactionsForAddress','getAsset'} and endpoint==PUBLIC_ENDPOINT:raise RuntimeError('Indexed-provider method unavailable on public Solana RPC; supply a compatible RAMONOS_RPC_URL. No substitute coverage inferred.')
 req=urllib.request.Request(endpoint,data=json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=60) as response:result=json.loads(response.read())
 except Exception:raise RuntimeError('Read-only RPC transport failed; endpoint details omitted') from None
 if 'error' in result or 'result' not in result:raise RuntimeError('Read-only RPC returned no accepted result for '+method)
 return result
