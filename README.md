# SIGNAL — Market Intelligence

A personal, single-page financial market intelligence dashboard. Live at:
**https://bipula7-jpg.github.io/Bipula.Market.Intelligence-/**

Not affiliated with Bloomberg, TradingView, FRED, or any financial data
provider. Personal project — informational only, not investment advice.

## What's on it

- **Macro** — live Bloomberg Business News stream, a market overview
  (indices, commodities, bond futures, crypto), key yields & the dollar,
  an intraday SPY chart, and an upcoming economic events calendar.
- **Sectors** — S&P 500 sector heatmap and a sector ETF screener.
- **Rates** — the full Treasury yield curve (1Y–30Y), the 10Y–2Y and
  10Y–3M yield spreads, the effective Fed Funds Rate, the US Dollar
  Index, and a 10-year yield chart.
- **Hours** — live market-session status (NYSE/Nasdaq pre-market,
  regular, after-hours) plus session clocks for London, Frankfurt,
  Tokyo, Hong Kong, and Sydney. Optional audible bell on session change.
- **News** — real-time market, corporate, and economic/rates headlines.
- **AI Intel** — on-demand AI-generated market summary, plus a live
  watchlist of stocks with a Wall Street "Strong Buy" consensus rating.

## How it's built

Everything lives in one file, **`index.html`** — no build step, no
framework. It's plain HTML/CSS/JS plus embedded third-party widgets:

| Data | Source | Refresh |
|---|---|---|
| Indices, commodities, crypto, charts, news, heatmap, screener, calendar | [TradingView](https://www.tradingview.com/) embedded widgets | Live, in-browser |
| Treasury yield curve (1Y–30Y), Dollar Index | TradingView (`TVC:` symbols) | Live, in-browser |
| **10Y–2Y spread, 10Y–3M spread, Fed Funds Rate** | [FRED](https://fred.stlouisfed.org/) (Federal Reserve Bank of St. Louis) via `scripts/fetch_fred_data.py` | Once daily, weekdays, via GitHub Actions |
| AI market summary | [Pollinations.ai](https://pollinations.ai/) (free, no key required) | On demand (button click) |
| Market session status, world clocks, bell | Computed client-side from the visitor's local clock | Live |

TradingView doesn't support arbitrary `FRED:`-prefixed symbols in its
free embeddable widgets, so the yield-spread and Fed Funds figures are
pulled directly from FRED's own API instead and cached as static JSON —
see [Data pipeline](#data-pipeline) below.

## Repo structure

```
index.html                              the entire dashboard (single page)
scripts/
  fetch_fred_data.py                    pulls FRED data, writes data/fred.json
  requirements.txt                      Python deps for the script above
data/
  fred.json                             cached FRED output the page reads
.github/workflows/
  update-fred-data.yml                  runs the script on a schedule
```

## Data pipeline

`update-fred-data.yml` runs on GitHub's servers (not in the visitor's
browser) on a schedule — weekdays at 21:30 UTC, roughly matching when
FRED's daily series actually update — plus on-demand via the Actions
tab's "Run workflow" button. It calls `fetch_fred_data.py`, which hits
the FRED API and writes the result to `data/fred.json`, then commits
that file if it changed. `index.html` fetches that JSON file directly
— visitors never call the FRED API themselves, and the API key never
touches the browser.

### One-time setup
The script needs a free [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html),
stored as a **GitHub Actions repository secret** named `FRED_API_KEY`
(Settings → Secrets and variables → Actions → New repository secret).
It is never committed to the repo or written into `index.html`.

## Making changes

Since it's one file, most edits are: open `index.html` in GitHub's web
editor (pencil icon), change it, commit to `main`. GitHub Pages rebuilds
automatically within a minute or two — hard-refresh (Ctrl/Cmd+Shift+R)
to see it.

To change what the FRED pipeline pulls, edit the `SERIES` dictionary in
`scripts/fetch_fred_data.py` (any [FRED series ID](https://fred.stlouisfed.org/tags/series)
works) and add a matching card in `index.html`'s Rates section plus an
entry in the `FRED_IDS` array in the `<script>` block.

## Disclaimer

Data is provided for informational purposes only and may contain
inaccuracies or delays. Not investment advice. Always verify with your
broker or a primary source before making decisions.
