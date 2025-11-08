# PRISM Hackathon Bot V8 - Portfolio Optimizer

A sophisticated automated trading bot that combines NLP-based client preference analysis with live market data to build optimized investment portfolios for the PRISM Challenge.

## 🎯 Project Overview

This bot participates in the PRISM Hackathon Challenge by:

1. Receiving client investment profiles from the PRISM Challenge API
2. Analyzing client preferences using Natural Language Processing (NLP)
3. Fetching real-time stock prices from the LIMEX API
4. Building optimized portfolios tailored to each client's risk tolerance and preferences
5. Submitting portfolios and tracking performance metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRISM Challenge API                       │
│           (Provides client contexts & accepts                │
│                    portfolio submissions)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Portfolio Optimizer Bot                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. NLP Context Parser                               │   │
│  │     • Extract budget, age, investment period         │   │
│  │     • Identify sector preferences                    │   │
│  │     • Detect sector avoidances                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. Risk Scoring Engine                              │   │
│  │     • Age-based risk adjustment                      │   │
│  │     • Time horizon analysis                          │   │
│  │     • Generate 10-90 risk score                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. Stock Filter                                     │   │
│  │     • Apply sector preferences                       │   │
│  │     • Exclude avoided sectors                        │   │
│  │     • Match stocks to risk profile                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. Portfolio Builder                                │   │
│  │     • Fetch live prices (LIMEX API)                  │   │
│  │     • Apply risk-based weighting                     │   │
│  │     • Calculate optimal quantities                   │   │
│  │     • Ensure budget compliance                       │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      LIMEX Price API                         │
│              (Provides live market quotes)                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Workflow

### Step 1: Context Acquisition

The bot requests a new client context from the PRISM Challenge API:

```python
GET http://www.prism-challenge.com:8082/request
Headers: X-API-Code: {TEAM_API_CODE}
```

**Example Response:**

```json
{
  "message": "A 35-year-old investor with $50,000 wants to invest from January 1, 2024 to December 31, 2024. They prefer technology and healthcare but avoid energy."
}
```

### Step 2: NLP Parsing

The bot uses regex patterns to extract key information:

| Field | Extraction Method | Example |
|-------|------------------|---------|
| **Budget** | Currency symbols ($, £) or "k" notation | $50,000 |
| **Age** | Pattern: `(\d+)-year-old` | 35 |
| **Period** | Date ranges converted to months | 12 months |
| **Preferences** | Keywords: "prefers", "likes", "wants to invest in" | technology, healthcare |
| **Avoidances** | Keyword: "avoids" | energy |

**Keyword Enhancement:**

- "tech", "ai" → adds "technology"
- "green", "clean" → adds "renewables"
- "safe", "dividend" → adds "consumer goods"
- "oil", "gas" → adds "energy" to avoidances

### Step 3: Risk Scoring

Calculate risk tolerance (10-90 scale):

**Base Score:** 50

**Age Adjustments:**

- < 30 years: +25 (young, high risk tolerance)
- 30-40 years: +15 (moderate-high risk tolerance)
- 40-50 years: +5 (moderate risk tolerance)
- 55-65 years: -15 (lower risk tolerance)
- > 65 years: -25 (conservative)

**Period Adjustments:**
>
- > 24 months: +15 (long-term, can weather volatility)
- 12-24 months: +5 (moderate term)
- < 6 months: -15 (short-term, need stability)

**Example:**

```
35-year-old, 12-month investment
Base: 50 + Age(+15) + Period(+5) = 70 (Moderate-High Risk)
```

### Step 4: Stock Filtering

From the knowledge base of 50+ stocks, filter based on:

1. **Eliminate Avoided Sectors:** Remove all stocks in avoided sectors
2. **Prioritize Preferred Sectors:** If preferences exist, only select from those
3. **Fallback:** If no matches, use all non-crypto stocks

**Stock Knowledge Base Structure:**

```python
{
  "AAPL": {"sector": "Technology", "risk": 40},
  "JNJ": {"sector": "Healthcare", "risk": 20},
  "XOM": {"sector": "Energy", "risk": 65},
  # ... 50+ more stocks
}
```

### Step 5: Live Price Fetching

Use LIMEX API to get real-time prices:

```python
POST https://api.lime.co/marketdata/quotes
Authorization: Bearer {LIMEX_TOKEN}
Content-Type: application/json

["AAPL", "MSFT", "GOOGL", "JNJ", "UNH"]
```

**Response:**

```json
[
  {"symbol": "AAPL", "ask": 178.50, "last": 178.45},
  {"symbol": "MSFT", "ask": 425.30, "last": 425.28},
  ...
]
```

**Price Selection Logic:**

1. Use "ask" price (what we pay when buying)
2. Fallback to "last" price if ask is 0 or missing

### Step 6: Portfolio Construction

**Risk-Based Weighting Strategies:**

| Risk Score | Strategy | Weight Distribution |
|------------|----------|---------------------|
| **> 70** (Aggressive) | Concentrated | [30%, 25%, 15%, 10%, 8%, 6%, 4%, 2%] |
| **40-70** (Moderate) | Balanced | [20%, 18%, 15%, 13%, 12%, 10%, 7%, 5%] |
| **< 40** (Conservative) | Diversified | [15%, 15%, 15%, 15%, 10%, 10%, 10%, 10%] |

**Allocation Process:**

1. Score stocks by risk match: `match_score = 100 - |stock_risk - client_risk|`
2. Sort stocks by match score (best matches first)
3. Select top 8 candidates
4. Fetch live prices via LIMEX
5. Allocate 95% of budget using weight strategy
6. Calculate quantities: `qty = floor(allocation / price)`
7. Ensure total cost ≤ budget

**Example Portfolio:**

```python
[
  {"ticker": "AAPL", "quantity": 50},
  {"ticker": "MSFT", "quantity": 25},
  {"ticker": "GOOGL", "quantity": 15},
  {"ticker": "JNJ", "quantity": 40},
  {"ticker": "UNH", "quantity": 10}
]
```

### Step 7: Submission & Tracking

Submit portfolio to PRISM API:

```python
POST http://www.prism-challenge.com:8082/submit
Headers: X-API-Code: {TEAM_API_CODE}
Content-Type: application/json

[
  {"ticker": "AAPL", "quantity": 50},
  {"ticker": "MSFT", "quantity": 25}
]
```

**Success Response:**

```json
{
  "passed": true,
  "profit": 2340.50,
  "points": 15.75
}
```

**Metrics Tracked:**

- Response time per iteration
- Success rate (successes/total attempts)
- Profit per portfolio
- Points earned
- Performance info every 10 rounds

## 📊 Stock Knowledge Base

The bot maintains a curated database of 50+ stocks across multiple sectors:

### Sectors & Risk Profiles

| Sector | Risk Range | Examples |
|--------|-----------|----------|
| **Technology** | 30-85 | AAPL (40), MSFT (35), NVDA (85) |
| **Healthcare** | 20-45 | JNJ (20), UNH (30), PFE (40) |
| **Consumer Goods** | 15-25 | PG (15), KO (15), WMT (25) |
| **Financial** | 10-60 | BRK-B (10), V (30), GS (60) |
| **Energy** | 60-65 | XOM (65), CVX (65), SHEL (60) |
| **Renewables** | 30-95 | NEE (30), ENPH (80), TSLA (95) |
| **Telecom** | 20-25 | VZ (20), T (25) |
| **Retail** | 35-40 | HD (40), NKE (35) |
| **Entertainment** | 45 | DIS (45) |
| **ETFs** | 20-65 | SPY (50), QQQ (65), GLD (20) |

## 🔧 Technologies Used

### Core Libraries

- **Python 3.14+** - Main programming language
- **requests** - HTTP client for API communication
- **numpy** - Numerical computing for portfolio calculations
- **json** - JSON parsing for API responses
- **re** - Regex for NLP text parsing
- **datetime** - Date/time handling

### APIs

- **PRISM Challenge API** - Contest platform
  - Endpoint: `http://www.prism-challenge.com:8082`
  - Authentication: API key header
  
- **LIMEX Price API** - Live market data
  - Auth: `https://auth.lime.co/connect/token`
  - Quotes: `https://api.lime.co/marketdata/quotes`
  - Authentication: OAuth2 password grant

## 📁 Project Structure

```
Prismchallenge/
├── playground.ipynb          # Main Jupyter notebook
├── README.md                 # This file
└── LICENSE                   # Project license
```

## 🎮 Usage

### Prerequisites

```bash
pip install requests numpy jupyter
```

### Running the Bot

1. **Open the notebook:**

```bash
jupyter notebook playground.ipynb
```

2. **Execute cells in order:**
   - Cell 1-2: Title & imports
   - Cell 3-4: API configuration
   - Cell 5-6: Stock knowledge base
   - Cell 7-8: PRISM API functions
   - Cell 9-10: LIMEX API functions
   - Cell 11-12: NLP parsing
   - Cell 13-14: Risk scoring & filtering
   - Cell 15-16: Portfolio construction
   - Cell 17-18: Main execution loop

3. **Test LIMEX (Optional):**
   - Run cell 20 to verify API connectivity

4. **Run the full bot:**
   - Uncomment cell 19 and execute to start

### Expected Output

```
============================================================
FINAL PORTFOLIO OPTIMIZER V8 - CORRECTED URLS + FAST PRICES
============================================================
Getting Limex (price) token...
SUCCESS: Limex token acquired.

Age:35 Budget:$50000.0 Period:12mo Risk:70
Prefers: technology, healthcare
Fetched prices: {'AAPL': 178.50, 'MSFT': 425.30, ...}
Built portfolio with 5 stocks. Total cost: $47500.00
SUCCESS [2.45s] | Profit: $2340.50 | Points: 15.75

Age:28 Budget:$100000.0 Period:24mo Risk:80
...
```

## 🎯 Performance Optimization

### Speed Features

- **Fast endpoint:** Uses POST `/marketdata/quotes` for bulk price fetching
- **Budget allocation:** Uses 95% of budget to stay safely under limit
- **Token caching:** Reuses LIMEX token until expiration
- **Efficient regex:** Pre-compiled patterns for NLP parsing
- **Smart fallback:** Defaults to SPY ETF if no stocks match

### Error Handling

- Token refresh on 401 errors
- Retry logic for failed API calls
- Empty portfolio submission on failures
- Graceful degradation with fallback stocks

## 📈 Strategy Highlights

### Risk Management

- Dynamic risk scoring based on age and horizon
- Diversification through weighted allocation
- Conservative budget usage (95% max)
- Sector-based filtering

### Price Accuracy

- Real-time LIMEX market data
- Ask price preference (actual buying price)
- Fallback to last price if needed
- Validation of positive prices

### Client Alignment

- NLP-based preference extraction
- Sector avoidance enforcement
- Preferred sector prioritization
- Risk-matched stock selection

## 🔒 Security Notes

⚠️ **Important:** This repository contains API credentials in plaintext for hackathon purposes. In production:

- Use environment variables
- Implement secret management (e.g., AWS Secrets Manager)
- Rotate credentials regularly
- Never commit credentials to public repositories

## 🐛 Troubleshooting

### Issue: "FAILED to get Limex token"

**Solution:** Check credentials in Section 2 (cell 4)

### Issue: "No live prices for any selected stock"

**Solution:** Verify LIMEX API endpoint and network connectivity

### Issue: "Error [CODE: 401]"

**Solution:** Verify PRISM API key is correct

### Issue: Token expires during operation

**Solution:** Automatic refresh implemented - should retry automatically

## 📝 API Rate Limits

- **PRISM Challenge:** No documented limit
- **LIMEX:** Token expires after ~60 minutes (auto-refresh implemented)

## 🏆 Competition Strategy

1. **Speed:** < 10 seconds per response (target: 2-5s)
2. **Accuracy:** Match client preferences exactly
3. **Risk Management:** Align portfolio risk with client profile
4. **Diversification:** 5-8 stocks per portfolio
5. **Budget Compliance:** Never exceed client budget

## 📊 Success Metrics

The bot tracks:

- **Success Rate:** Percentage of accepted portfolios
- **Average Profit:** Mean profit per successful submission
- **Points Earned:** Competition scoring metric
- **Response Time:** Speed of portfolio generation

Example after 10 iterations:

```
============================================================
{'rank': 5, 'total_points': 157.5, 'total_profit': 23405.0}
Success Rate: 9/10
============================================================
```

## 🤝 Contributing

This is a hackathon project, but suggestions welcome:

1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Submit a pull request

## 📄 License

See LICENSE file for details.

## 👥 Team

- **Team API Code:** 044182b416e87e47fdea3eb923d23393
- **Challenge:** PRISM Hackathon 2025

## 🙏 Acknowledgments

- **PRISM Challenge** - For hosting the competition
- **LIMEX** - For providing live market data API
- **Python Community** - For excellent libraries

---

**Built with ❤️ for the PRISM Hackathon**

*Last Updated: November 8, 2025*
