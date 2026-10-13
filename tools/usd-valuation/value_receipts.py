#!/usr/bin/env python3
"""Read-only SOL/USD historical market valuation; frozen source replay supported."""
import argparse,csv,datetime,decimal,hashlib,json,pathlib,time,urllib.parse,urllib.request
from concurrent.futures import ThreadPoolExecutor
D=decimal.Decimal
UTC=datetime.timezone.utc
BASE='https://api.exchange.coinbase.com'
HEADERS={'User-Agent':'Mozilla/5.0','Accept':'application/json'}
def stamp(s):return int(datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp())
def iso(t):return datetime.datetime.fromtimestamp(t,UTC).isoformat().replace('+00:00','Z')
def fetch(url, raw, offline=False):
    key=hashlib.sha256(url.encode()).hexdigest(); p=raw/(key+'.json'); meta=raw/(key+'.meta.json')
    if p.exists():return json.loads(p.read_text(),parse_float=D),str(p)
    if offline:raise RuntimeError('Missing frozen source '+url)
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=45) as r:
                b=r.read(); hdr=dict(r.headers); status=r.status
            obj=json.loads(b,parse_float=D)
            if isinstance(obj,dict) and 'message' in obj:raise RuntimeError(obj['message'])
            p.write_bytes(b)
            meta.write_text(json.dumps({'url':url,'retrievedUTC':datetime.datetime.now(UTC).isoformat(),'httpStatus':status,'responseHeaders':hdr,'sha256':hashlib.sha256(b).hexdigest()},indent=2))
            time.sleep(.25)
            return obj,str(p)
        except Exception:
            if attempt==3:raise
            time.sleep(1+attempt)
def retrieve_prices(timestamps, raw, offline=False):
    """Returns each exact requested minute and source; absent candles stay absent."""
    raw=pathlib.Path(raw);raw.mkdir(parents=True,exist_ok=True)
    minutes=sorted(set(int(t)//60*60 for t in timestamps)); groups=[]
    for t in minutes:
        if not groups or t-groups[-1][0]>295*60:groups.append([t])
        else:groups[-1].append(t)
    def one(group):
        query=urllib.parse.urlencode({'granularity':60,'start':iso(group[0]-60),'end':iso(group[-1]+60)})
        obj,p=fetch(BASE+'/products/SOL-USD/candles?'+query,raw,offline)
        if not isinstance(obj,list):raise RuntimeError('Unexpected candle body '+p)
        mapped={}
        for a in obj:
            if len(a)!=6:raise RuntimeError('Unexpected candle schema')
            ts=int(a[0]);lo,hi,op,cl,vol=[D(str(v)) for v in a[1:]]
            if not(lo>0 and hi>=lo and lo<=op<=hi and lo<=cl<=hi and vol>=0):raise RuntimeError('Invalid candle')
            if ts in group:mapped[ts]={'minuteUTC':iso(ts),'low':lo,'high':hi,'open':op,'close':cl,'volume':vol,'rawSource':p}
        return mapped
    candles={}
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(one,groups):candles.update(result)
    missing=set(minutes)-candles.keys()
    if missing:raise RuntimeError('Missing minute candles: '+','.join(iso(t) for t in sorted(missing)))
    return candles

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipts',required=True);ap.add_argument('--output',required=True);ap.add_argument('--offline',action='store_true');a=ap.parse_args()
    out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True);raw=out/'raw'
    rows=list(csv.DictReader(open(a.receipts)));chosen=[r for r in rows if r['asset'] in ('SOL','WSOL')]
    assert all(r['verified']=='True' for r in chosen)
    candles=retrieve_prices([stamp(r['utc']) for r in chosen],raw,a.offline)
    valued=[]
    for idx,r in enumerate(rows):
        if r['asset'] not in ('SOL','WSOL'):continue
        t=stamp(r['utc']);c=candles[t//60*60];amount=D(r['amountLamports'])/D(10**9)
        valued.append({**r,'receiptRow1Based':idx+2,'solEquivalent':str(amount),'priceMinuteUTC':c['minuteUTC'],'solUsdMinuteClose':str(c['close']),'solUsdMinuteLow':str(c['low']),'solUsdMinuteHigh':str(c['high']),'usdHistoricalMarketValue':str(amount*c['close']),'usdMinuteLowSensitivity':str(amount*c['low']),'usdMinuteHighSensitivity':str(amount*c['high']),'closeBoundaryMinusReceiptSeconds':str(t//60*60+60-t),'priceRawSource':c['rawSource']})
    with (out/'receipts-valued-usd.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(valued[0]));w.writeheader();w.writerows(valued)
    monthly={}
    for r in valued:
        month=r['utc'][:7];m=monthly.setdefault(month,{'monthUTC':month,'events':0,'sol':D(0),'usd':D(0),'usdLow':D(0),'usdHigh':D(0)})
        m['events']+=1
        for k,v in [('sol','solEquivalent'),('usd','usdHistoricalMarketValue'),('usdLow','usdMinuteLowSensitivity'),('usdHigh','usdMinuteHighSensitivity')]:m[k]+=D(r[v])
    with (out/'monthly-valued-usd.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=['monthUTC','events','sol','usd','usdLow','usdHigh']);w.writeheader();w.writerows(monthly.values())
    total=sum((D(r['solEquivalent']) for r in valued),D(0));usd=sum((D(r['usdHistoricalMarketValue']) for r in valued),D(0))
    ticker,tp=fetch(BASE+'/products/SOL-USD/ticker',raw,a.offline);clock,cp=fetch(BASE+'/time',raw,a.offline)
    price=D(ticker['price']);now=total*price
    summary={'sourceReceipts':a.receipts,'sourceReceiptsSha256':hashlib.sha256(pathlib.Path(a.receipts).read_bytes()).hexdigest(),'source':'Coinbase Exchange SOL-USD public candles','documentation':'https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/products/get-product-candles','method':'Each verified SOL/WSOL receipt amount multiplied by close of its containing 60-second UTC Coinbase SOL-USD candle. Close can occur after receipt within that minute. Low/high sensitivity is an intraminute range, not statistical uncertainty or a cross-exchange bound. No USD conversion or sale is asserted.','receiptEvents':len(valued),'transactionCount':len({r['signature'] for r in valued}),'uniqueReceiptMinutes':len(candles),'firstReceiptUTC':min(r['utc'] for r in valued),'lastReceiptUTC':max(r['utc'] for r in valued),'solEquivalent':str(total),'historicalUsdMarketValue':str(usd),'historicalUsdMinuteLowSensitivity':str(sum((D(r['usdMinuteLowSensitivity']) for r in valued),D(0))),'historicalUsdMinuteHighSensitivity':str(sum((D(r['usdMinuteHighSensitivity']) for r in valued),D(0))),'weightedHistoricalSolUsd':str(usd/total),'currentSolUsdSpot':str(price),'currentSpotTradeUTC':ticker['time'],'providerClockUTC':clock['iso'],'currentSpotRawSource':tp,'providerClockRawSource':cp,'sameSolAtCurrentSpotUsd':str(now),'historicalMinusCurrentSpotUsd':str(usd-now),'excludedNonSolEvents':len(rows)-len(valued),'exclusionReason':'USDC and PUMP are separate assets and are not included in SOL/WSOL valuation.','coverage':f'{len(valued)}/{len(chosen)} verified SOL/WSOL receipts have their exact containing UTC minute candle; no daily approximation or gap fill.'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
