"""Independently check retained arithmetic, minute prices and token attribution offline."""
import argparse
import collections
import csv
import datetime
import decimal
import hashlib
import json
import pathlib

D = decimal.Decimal
CASE = pathlib.Path('outputs/ramonos-launches-20261013')
WSOL = 'So11111111111111111111111111111111111111112'
CLOSED = 'bounded_closed_original_wallet_position'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=pathlib.Path, default=pathlib.Path(__file__).resolve().parents[1])
    ap.add_argument('--out', type=pathlib.Path, required=True)
    a = ap.parse_args()
    root, out = a.source.resolve(), a.out.resolve()
    base = root / CASE
    if out == base or out in base.parents:
        ap.error('Output must not replace the evidence directory or its parents')
    inputs = {}

    def read(name, csv_rows=False):
        p = base / name
        inputs[str(CASE / name)] = hashlib.sha256(p.read_bytes()).hexdigest()
        return list(csv.DictReader(p.open())) if csv_rows else json.loads(p.read_text())

    config = read('census/config.json')
    positions = read('trading/positions.json')
    by_mint = {r['mint']: r for r in positions}
    assert len(by_mint) == len(positions) == 279
    failed = read('costs-coverage/failed-cohort-fees.csv', True)
    assert len({r['signature'] for r in failed}) == len(failed)
    failed_by_mint = collections.Counter()
    for r in failed:
        assert r['mint'] in by_mint
        failed_by_mint[r['mint']] += int(r['feeLamports'])
    closed = {r['mint']: r for r in positions if r['positionStatus'] == CLOSED and r['quoteMint'] == WSOL}
    assert len(closed) == 196
    successful = sum(int(r['nativeWsolCashDeltaLamports']) for r in closed.values())
    closed_failed = sum(failed_by_mint[m] for m in closed)
    claims = read('costs-coverage/claim-native-wsol-cash.csv', True)
    assert len({r['signature'] for r in claims}) == len(claims) == 568
    standalone = {r['signature']: r for r in claims if r['includedStandaloneExcludesTradeOverlap'] == 'True'}
    assert len(standalone) == 559
    net_claims = sum(int(r['walletNativeOwnedWsolDeltaLamports']) for r in standalone.values())
    total = D(successful - closed_failed + net_claims) / D(10**9)
    fees = read('own-fees/verified-receipts.json')
    by_signature = collections.defaultdict(list)
    for r in fees:
        if r['asset'] in ('SOL', 'WSOL'):
            assert r['verified'] is True
        by_signature[r['signature']].append(r)
    gross = sum(int(r['amountLamports']) for r in fees if r['asset'] in ('SOL', 'WSOL'))

    raw_prices, price_hashes = {}, {}

    def value(r):
        p = (root / r['priceRawSource']).resolve()
        relative = str(p.relative_to(root))
        if p not in raw_prices:
            b = p.read_bytes()
            digest = hashlib.sha256(b).hexdigest()
            assert digest == json.loads(p.with_suffix('.meta.json').read_text())['sha256']
            raw_prices[p] = {int(c[0]): c for c in json.loads(b, parse_float=D)}
            price_hashes[relative] = digest
        minute = int(datetime.datetime.fromisoformat(r['utc'].replace('Z', '+00:00')).timestamp()) // 60 * 60
        price = D(str(raw_prices[p][minute][4]))
        assert price == D(r['solUsdMinuteClose'])
        sol = D(r['signedSolEquivalent'])
        assert sol * price == D(r['usdSignedCashflow'])
        return sol, sol * price

    cash = read('usd-valuation/trading-cashflows-valued-usd.csv', True)
    trade_totals = collections.defaultdict(lambda: [D(0), D(0)])
    for r in cash:
        sol, usd = value(r)
        trade_totals[r['mint']][0] += sol
        trade_totals[r['mint']][1] += usd
    for mint in closed:
        assert trade_totals[mint][0] == D(int(closed[mint]['nativeWsolCashDeltaLamports']) - failed_by_mint[mint]) / D(10**9)
    claim_values = read('usd-valuation/standalone-claim-account-cash-valued-usd.csv', True)
    assert {r['signature'] for r in claim_values} == set(standalone)
    for r in claim_values:
        c = standalone[r['signature']]
        assert r['utc'] == c['utc']
        assert D(r['signedSolEquivalent']) == D(c['walletNativeOwnedWsolDeltaLamports']) / D(10**9)
    valued_claims = {r['signature']: value(r) for r in claim_values}
    assert sum((s for s, u in valued_claims.values()), D(0)) == D(net_claims) / D(10**9)
    claim_by_mint = collections.defaultdict(lambda: [D(0), D(0), 0])
    for sig, c in standalone.items():
        events = by_signature.get(sig, [])
        mints = {r['event'].get('mint') for r in events}
        if not events or len(mints) != 1 or next(iter(mints)) not in by_mint:
            continue
        if not all(r['verified'] is True and r['name'] == 'DistributeCreatorFeesEvent' and r['asset'] in ('SOL', 'WSOL') and r['cohortMint'] is True for r in events):
            continue
        # Allocate only a sole-mint claim with no cash residual beyond its network fee.
        payout = sum(int(r['amountLamports']) for r in events)
        assert payout - int(c['walletNativeOwnedWsolDeltaLamports']) == int(c['walletPaidFeeLamports'])
        mint = next(iter(mints))
        sol, usd = valued_claims[sig]
        claim_by_mint[mint][0] += sol
        claim_by_mint[mint][1] += usd
        claim_by_mint[mint][2] += 1
    rows = []
    for mint in set(closed) | set(claim_by_mint):
        trade_sol, trade_usd = trade_totals[mint] if mint in closed else (D(0), D(0))
        fee_sol, fee_usd, tx_count = claim_by_mint.get(mint, (D(0), D(0), 0))
        known_sol, known_usd = trade_sol + fee_sol, trade_usd + fee_usd
        p = by_mint[mint]
        rows.append({'mint': mint, 'name': p['name'], 'ticker': '$' + p['symbol'],
                     'positionStatus': p['positionStatus'], 'closedPositionNetSol': str(trade_sol) if mint in closed else '',
                     'attributableNetClaimSol': str(fee_sol), 'attributableClaimTransactions': tx_count,
                     'knownNetCashSol': str(known_sol), 'historicalNetCashUsd': str(known_usd),
                     'shareOfAuditedTotalPercent': str(known_sol / total * D(100)), 'pooledCreatorFeesUnallocated': True})
    rows.sort(key=lambda r: D(r['knownNetCashSol']), reverse=True)
    for rank, r in enumerate(rows, 1):
        r['rank'] = rank
    routes = read('routes/routes.json')
    pump = [r for r in routes if r['platform'] == 'Pump']
    bps = collections.Counter()
    for r in pump:
        if r['shareholders']:
            assert sum(int(s['share_bps']) for s in r['shareholders']) == 10000
            share = sum(int(s['share_bps']) for s in r['shareholders'] if s['address'] == config['wallet'])
        else:
            share = 10000 if r['routeCategory'] == 'ordinary creator wallet' and r['activeCreator'] == config['wallet'] else 0
        bps[share] += 1
    route_manifest = read('routes/manifest.json')
    for r in route_manifest['files']:
        assert hashlib.sha256((root / r['path']).read_bytes()).hexdigest() == r['sha256']
    expected = read('usd-valuation/combined-account-cash-summary-usd.json')
    closed_usd = sum((trade_totals[m][1] for m in closed), D(0))
    claim_usd = sum((u for s, u in valued_claims.values()), D(0))
    assert total == D(expected['metrics'][3]['solQuantity'])
    assert closed_usd + claim_usd == D(expected['metrics'][3]['historicalUsd'])
    assert len(pump) == 277 and bps[10000] == 263
    attributable = sum((v[0] for v in claim_by_mint.values()), D(0))
    receipt = {'offline': True, 'financialExecutionCapLamports': '0', 'auditCutoffUtc': config['cutoffUtc'],
               'launches': len(positions), 'closedSolPositions': len(closed), 'successfulClosedCashSol': str(D(successful) / D(10**9)),
               'allocatedClosedFailedFeesSol': str(D(closed_failed) / D(10**9)), 'closedNetCashSol': str(D(successful - closed_failed) / D(10**9)),
               'standaloneClaimTransactions': len(standalone), 'excludedClaimTradeOverlaps': len(claims) - len(standalone),
               'standaloneNetClaimCashSol': str(D(net_claims) / D(10**9)), 'grossCreatorReceiptsSol': str(D(gross) / D(10**9)),
               'combinedNetCashSol': str(total), 'closedHistoricalUsd': str(closed_usd), 'claimHistoricalUsd': str(claim_usd),
               'combinedHistoricalUsd': str(closed_usd + claim_usd), 'pricedTradingComponents': len(cash),
               'rawPriceResponsesHashVerified': len(price_hashes), 'priceResponseSetSha256': hashlib.sha256(json.dumps(price_hashes, sort_keys=True).encode()).hexdigest(),
               'pumpLaunches': len(pump), 'fullWalletRoutes': bps[10000], 'fullWalletRoutePercent': str(D(bps[10000]) / D(len(pump)) * 100),
               'routeManifestFilesHashVerified': len(route_manifest['files']), 'attributableClaimMints': len(claim_by_mint),
               'attributableClaimTransactions': sum(v[2] for v in claim_by_mint.values()), 'attributableNetClaimSol': str(attributable),
               'unallocatedNetClaimSol': str(D(net_claims) / D(10**9) - attributable), 'sourceFilesSha256': inputs,
               'scope': 'Frozen original-wallet cash. Token amounts are known attributable components, not a complete per-token earnings ranking. No fresh chain observation or USD cashout is asserted.'}
    out.mkdir(parents=True, exist_ok=True)
    (out / 'arithmetic-verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    with (out / 'token-attributable-cash.csv').open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({k: v for k, v in receipt.items() if k != 'sourceFilesSha256'}, indent=2))


if __name__ == '__main__':
    main()
