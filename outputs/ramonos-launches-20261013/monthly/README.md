# Monthly launches, trading cash, creator fees and SOL launch buys

The disclosed wallet launched 279 verified tokens from **December 17, 2025 through September 22, 2026**. Actual admitted buy/sell activity also ends September 22. Verified SOL/WSOL creator receipts continue through **October 10, 2026**; this audit stops at **October 13, 2026 16:19:01 UTC**. December and October are partial months.

All amounts in the table are SOL equivalent. Launch counts and initial buy statistics use creation month. Cash and receipt columns use the individual UTC transaction/receipt month.

| UTC month | Launches | All SOL trading net cash | Closed-position net cash | Gross creator fees | Median positive creation buy |
|---|---:|---:|---:|---:|---:|
| Dec 2025 | 12 | 365.230 | 237.267 | 382.968 | 17.50 |
| Jan 2026 | 56 | 1,513.922 | 1,020.606 | 855.145 | 9.23 |
| Feb | 43 | 172.181 | 120.569 | 95.537 | 2.12 |
| Mar | 30 | 66.612 | 49.648 | 44.214 | 2.12 |
| Apr | 30 | 63.525 | 63.547 | 21.032 | 5.00 |
| May | 21 | 0.959 | 0.981 | 1.741 | 3.00 |
| Jun | 8 | 50.260 | 50.202 | 39.282 | 11.79 |
| Jul | 20 | -35.808 | 35.071 | 89.896 | 8.10 |
| Aug | 43 | 66.847 | 83.062 | 59.922 | 2.00 |
| Sep | 16 | 14.968 | 13.368 | 70.475 | 3.97 |
| Oct to cutoff | 0 | 0.002 | 0.002 | 0.076 | — |
| **Total / overall median** | **279** | **2,278.698** | **1,674.323** | **1,660.287** | **4.99** |

## What the columns mean

All SOL trading cash covers the 272 SOL-quote launches and includes transferred or remaining inventory. Closed-position cash covers the 196 fully matched, closed original-wallet SOL positions. Both include associated successful cash movements and witnessed failed transaction fees, counted once. They remain account-cash measures with the original audit's ownership/purpose limits. Seven launches in other quote assets are excluded from SOL trading and buy-in statistics but included in launch counts.

Creator fees are gross actual SOL/WSOL payouts received by this wallet in each month. Claims pool mints and cannot all be assigned to that month's newly created tokens. Separate net claim cash, combined net account cash and historical dollar values are retained in the full CSV; gross fees must not be added as if they were net claim cash. The small October trading amount is an allocated account refund, with no new launch or buy/sell in that month.

## Typical launch buy

- 230 launches had positive SOL buys in the creation transaction: median **4.9925925915 SOL**, mean **8.4259411432 SOL**, middle 50% **1.849333663–10.125000003 SOL**, and maximum **39.999999999 SOL**.
- Across all 272 SOL-quote launches, including zero creation buys: median **3.121788286 SOL**.
- The 42 zero creation buys comprise 23 launches first bought later and 19 without an observed acquisition.
- First observed SOL buy, including buys after creation: median **3.824763905 SOL** among 253 acquired launches.
- Cumulative creation buys total **1,937.966462938 SOL**. This counts spending across the full sequence of launches. Venue fees are included; setup, network fees and account rent are separate.

December–January contributed **75.13%** of the closed-position net cash and **74.57%** of gross creator-fee receipts. January had the highest launch count, **56**. This wallet's later months generated substantially less cash than that initial period.

## Reproduce

Run from the repository root:

```sh
python3 tools/monthly/build.py
```

The processor uses only published derived source files and performs no network calls or financial actions. `monthly.csv` contains monthly net claim cash, combined cash, historical dollar amounts and additional denominator/median columns. `per-launch-buy-in.csv` binds each launch's creation buy and first observed buy. `source-manifest.json` binds all inputs by SHA-256. Global totals and independently computed monthly figures agree exactly.
