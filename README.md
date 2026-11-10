# Stock Market Prediction Using AI

A Streamlit application for exploring a stock through company fundamentals, technical indicators, financial news sentiment, experimental forecasts, and time-based model evaluation. It is an educational analysis tool, not financial advice.

## What the app does

Choose a listed company, historical period, forecast unit, and forecast duration in the sidebar, then select **Run analysis**. The app retrieves available market data and presents the results in five sections:

1. **Overview** — latest price information, fundamental and technical scores, news sentiment, and a combined three-pillar verdict.
2. **Technical analysis** — historical price chart, moving averages, RSI and MACD, plus a graded technical score.
3. **News & sentiment** — recent articles scored by FinBERT when available, with a simpler lexical fallback.
4. **Forecast** — an experimental future closing-price estimate, uncertainty ranges, and an up/down estimate for the selected horizon.
5. **Model evaluation** — chronological holdout and walk-forward results, baseline comparisons, and a cost-adjusted illustrative backtest.

The stock selector includes more than 100 Nasdaq-100 constituents. Data is cached for 15 minutes; the interface shows the latest available market date and retrieval timestamps. Provider data can be delayed, missing, revised, or subject to quotas.

## Analysis methods

### Fundamental analysis

The fundamental score is a weighted average of available, graded company metrics on a 0–100 scale. It can include P/E, P/B, EV/EBITDA, a three-scenario discounted cash flow (DCF) estimate, profit margin, return on equity (ROE), return on invested capital (ROIC), debt, liquidity, interest coverage, and free cash flow (FCF). The table shows each metric's weight and flags missing values; unavailable metrics are excluded and the remaining weights are renormalized.

When sector-peer observations are available, metrics can be graded by their percentile among those peers. If not, the app marks the grade as a heuristic rather than presenting a made-up sector ranking. The DCF is an illustrative estimate based on simplified pessimistic, base, and optimistic assumptions. It is omitted or flagged as unreliable for financial companies and companies with non-positive FCF. Multi-year trends are displayed only when enough financial statement history is available. A fiscal period-end date is not necessarily the date the information became public.

### Technical analysis

The app derives indicators from historical price and volume data, including SMA 20/50/200, MACD, RSI, ADX with directional indicators, Bollinger Bands, ATR, volume confirmation, recent support and resistance, and distance from the 52-week high. Directional indicators receive continuous grades based on their distance from reference levels; the score averages the available grades. RSI is displayed in oversold, neutral, or overbought zones, not as a simple bullish pass/fail test. ATR and support/resistance provide context rather than a directional vote. The chart can mark SMA 50/200 crossovers.

### News and sentiment

News is collected from Yahoo Finance and Google News RSS, with NewsAPI available as an optional fallback when `NEWSAPI_KEY` is configured. Undated, old, irrelevant, duplicate, and selected transaction-filler headlines are filtered. FinBERT (`ProsusAI/finbert`) scores article text when its dependencies and model are available; otherwise, a lightweight word-based fallback is used and marked as less reliable.

Article scores are combined using recency, an indicative source-quality weight, and a reduced weight for non-English headlines. The aggregate score ranges from **−1 (negative) to +1 (positive)**. The app reports the article count and positive/neutral/negative breakdown, and shows the most influential headlines.

### Combined verdict

The Overview combines fundamental, technical, and sentiment scores into a **Bullish**, **Neutral**, or **Bearish** signal. Default weights are **40% fundamentals, 40% technical analysis, and 20% sentiment**; unavailable pillars are omitted and the remaining weights are normalized.

If at least 100 dated historical snapshots exist for a stock, the app can estimate alternative weights from earlier snapshots and retain them only when they perform better than the defaults on a later chronological validation period. The displayed score strength measures distance from neutral; it is **not** a probability that the verdict will be correct.

### Forecast

The selected forecast horizon is converted into trading sessions (one week is treated as 5 sessions and one month as 21). A model estimates the return over that horizon from historical price features and converts it into an indicative closing price. The app shows an indicative 50% and 90% range, an estimated up/down split based on historical validation residuals, and local feature effects when available for the chosen model.

The ranges use finite-sample conformal order statistics calibrated on walk-forward residuals. Because market errors are time-dependent, their coverage is approximate and not guaranteed. The probability split is empirical, not a promise of accuracy.

### Model evaluation

The evaluation uses chronological training, validation, and test periods, plus expanding walk-forward windows. It does not randomly shuffle dates. The model is compared with simple baselines, including an unchanged price, an always-up forecast, and a 20-session moving-average forecast. Reported measures include MAE, RMSE, MAPE, MASE, directional accuracy, and test sample count.

An illustrative long-or-cash backtest also reports Sharpe ratio, maximum drawdown, and win rate. It assumes 10 basis points of fees and 5 basis points of slippage per position change. It does not model every real-world cost or constraint, such as taxes, dividends, liquidity, or market impact.

The application can record one dated snapshot per stock and market session in `data/pillar_history.csv`. Historical pillar features are only available from the time the app begins recording them; current fundamentals or sentiment are not copied into older dates. Public data does not provide a complete, reliable point-in-time history of financial release dates, and later vendor revisions remain a limitation.

## Data sources and dependencies

- **Prices and company information:** Yahoo Finance through `yfinance`.
- **News:** Yahoo Finance and Google News RSS; optional NewsAPI fallback.
- **Sentiment:** FinBERT through Transformers and PyTorch, with a lexical fallback.
- **Forecast models:** scikit-learn estimators; TensorFlow/Keras is optional for the LSTM model.
- **Interface and charts:** Streamlit, Pandas, NumPy, and Plotly.

Data availability varies by ticker and provider. Missing fields and unavailable analyses are reported rather than invented.

## Project structure

```text
app.py                       Streamlit interface and app orchestration
src/data_loader.py           Prices, company information, and news retrieval
src/fundamental.py           Fundamental metrics, grades, and DCF scenarios
src/technical.py             Technical indicators, score, and charts
src/sentiment.py             FinBERT scoring and lexical fallback
src/preprocessing.py         Time-ordered model features and targets
src/ml_models.py             Model comparison and walk-forward residuals
src/prediction.py            Forecast price, ranges, and direction estimate
src/evaluation.py            Chronological holdout, walk-forward, and backtest
src/pillar_history.py        Locally dated pillar-score snapshots
src/scoring.py               Combined three-pillar verdict
src/i18n.py                  English, French, and Arabic interface text
src/stocks.py                Popular stock universe
tests/                       Existing automated tests
```

## Setup on Windows

Open PowerShell in the project folder and run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

FinBERT is optional because its model packages are large. To install its dependencies:

```powershell
pip install -r requirements-finbert.txt
```

TensorFlow is also optional. Install it separately in a Python environment supported by your TensorFlow version to enable the LSTM model.

To configure NewsAPI for the current PowerShell session, set the key before launching the app:

```powershell
$env:NEWSAPI_KEY = "your-newsapi-key"
```

Keep API keys private and out of source control. Yahoo Finance and Google News RSS do not require this key.

## Run the app

```powershell
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). An internet connection is needed to retrieve current data. Select a stock and history period, choose a forecast horizon, then click **Run analysis**.

## Limitations

- Stock prices are uncertain; historical evaluation cannot guarantee future performance.
- Free data may be delayed, incomplete, rate-limited, or revised.
- Company ratios and DCF outputs depend on provider fields and simplifying assumptions.
- Sector percentiles are shown only when comparable peer data is actually available; heuristic grades are not peer rankings.
- Financial statement period dates do not establish when information was publicly released. Point-in-time historical fundamentals and news are not comprehensively available from the current providers.
- Historical pillar snapshots accumulate only while the app is used. Early forecasts may therefore rely on price-derived features alone.
- News sentiment depends on coverage, language detection, source weighting, and model availability; it is not a measure of the whole market.
- Backtests simplify execution and omit some costs and market conditions. Past results do not predict future results.

**Educational and experimental analysis only. Not financial advice.**
