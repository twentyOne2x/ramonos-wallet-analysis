"""Build the README's static charts from retained tables; no network calls."""
import csv,collections,pathlib,datetime,html,json
ROOT=pathlib.Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs';OUT=ROOT/'outputs/ramonos-launches-20261013';DOCS.mkdir(exist_ok=True)
rows=list(csv.DictReader((OUT/'own-fees/receipts.csv').open()));monthly=collections.Counter()
for row in rows:
    if row['verified']=='True':monthly[row['utc'][:7]]+=int(row['amountLamports'])
assert sum(monthly.values())==1660286830500
with(DOCS/'monthly-creator-fees.csv').open('w',newline='')as f:
    writer=csv.writer(f);writer.writerow(['monthUtc','grossReceivedSolEquivalent','rawLamportsEquivalent'])
    writer.writerows((k,f'{v/1e9:.9f}',v)for k,v in sorted(monthly.items()))
rows=list(csv.DictReader((OUT/'census/weekly-cadence.csv').open()));keys=list(rows[0]);weekly={r[keys[0]]:int(r[keys[1]])for r in rows}
start=datetime.date(2025,12,15);end=datetime.date(2026,10,12);items=[]
while start<=end:
    year,week,_=start.isocalendar();key=f'{year}-W{week:02}'
    items.append((start.strftime('%b %d'),weekly.get(key,0)));start+=datetime.timedelta(days=7)
assert sum(value for _,value in items)==279
def plot(name,title,subtitle,items,decimals=0):
    width=1040;height=320;left=76;right=24;top=76;bottom=60
    pw=width-left-right;ph=height-top-bottom;maximum=max(value for _,value in items)*1.14 or 1;bw=pw/len(items)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(title)}" viewBox="0 0 {width} {height}">',
         f'<rect width="{width}" height="{height}" rx="14" fill="#f6f8fa"/>',
         f'<text x="{left}" y="31" font-family="Arial,sans-serif" font-size="20" font-weight="700" fill="#1f2328">{html.escape(title)}</text>',
         f'<text x="{left}" y="54" font-family="Arial,sans-serif" font-size="12" fill="#57606a">{html.escape(subtitle)}</text>']
    for i in range(5):
        value=maximum*i/4;y=top+ph-ph*i/4
        svg.append(f'<path d="M{left},{y:.1f} H{width-right}" stroke="#d8dee4"/><text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial,sans-serif" font-size="11" fill="#57606a">{value:.0f}</text>')
    for i,(label,value)in enumerate(items):
        x=left+i*bw+bw*.18;h=ph*value/maximum;y=top+ph-h
        if value:svg.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bw*.64:.2f}" height="{h:.2f}" rx="3" fill="#635bff"><title>{html.escape(label)}: {value:.{decimals}f}</title></rect>')
        step=1 if len(items)<=12 else 5
        if i%step==0 or i==len(items)-1:svg.append(f'<text x="{left+(i+.5)*bw:.2f}" y="{top+ph+25}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" fill="#57606a">{html.escape(label)}</text>')
        if len(items)<=12:svg.append(f'<text x="{left+(i+.5)*bw:.2f}" y="{y-7:.2f}" text-anchor="middle" font-family="Arial,sans-serif" font-size="11" font-weight="600" fill="#1f2328">{value:.1f}</text>')
    svg.append('</svg>');(DOCS/name).write_text('\n'.join(svg))
plot('monthly-creator-fees.svg','Gross creator-fee payouts to the disclosed wallet','SOL equivalent · native SOL + wallet-owned WSOL receipts · other tokens excluded',[(datetime.date.fromisoformat(k+'-01').strftime('%b %y'),v/1e9)for k,v in sorted(monthly.items())],1)
plot('weekly-launches.svg','Verified launches by ISO week','UTC · 279 signed creations · zero-launch weeks included · final week is partial',items)
print(json.dumps({'monthlyTotalSolEquivalent':sum(monthly.values())/1e9,'weeklyTotal':sum(v for _,v in items),'weeks':len(items),'monthly':{k:v/1e9 for k,v in sorted(monthly.items())}},indent=2))
