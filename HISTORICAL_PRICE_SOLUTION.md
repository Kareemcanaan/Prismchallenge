# Historical Price Solution - The Right Approach

## 🎯 The Core Problem

**Current Approach (WRONG)**:

```
1. PRISM sends: "Invest from January 1st 2024 to December 31st 2024, budget $87"
2. Bot fetches: CURRENT prices (November 2025)
3. Bot builds portfolio: $498.17 worth at Nov 2025 prices
4. PRISM evaluates: Using Jan 2024 prices → Portfolio actually costs $87 at Jan 2024 prices
5. Result: Budget breach because prices are completely different!
```

**Correct Approach**:

```
1. PRISM sends: "Invest from January 1st 2024 to December 31st 2024, budget $87"
2. Bot extracts: START_DATE = "2024-01-01"
3. Bot fetches: HISTORICAL prices from January 1st 2024
4. Bot builds portfolio: $87 worth at Jan 2024 prices
5. PRISM evaluates: Using Jan 2024 prices → Perfect match!
```

---

## 🔍 Investigation: Does LIMEX Support Historical Data?

### Option 1: LIMEX Historical API (BEST)

LIMEX may have endpoints like:

- `/marketdata/history/{symbol}?date=2024-01-01`
- `/marketdata/quotes?date=2024-01-01` with date parameter
- `/marketdata/ohlc/{symbol}?from=2024-01-01&to=2024-01-01`

**Action**: Check LIMEX API documentation or test with date parameters.

### Option 2: Parse Start Date from Context

```python
# Extract start date from message
dates = re.findall(r'(\w+ \d+(?:st|nd|rd|th)?, \d{4})', msg)
if len(dates) >= 2:
    start_date = dates[0]  # "January 1st, 2024"
    # Convert to ISO format: "2024-01-01"
```

### Option 3: Alternative Data Sources

If LIMEX doesn't support historical:

- **Yahoo Finance API**: Free historical data
- **Alpha Vantage**: Free tier available
- **Polygon.io**: Historical stock prices
- **IEX Cloud**: Historical end-of-day prices

---

## 💡 Proposed Solution

### Step 1: Extract Start Date from Context

```python
def parse_context(context_text):
    # ... existing code ...
    
    # Extract investment START date
    start_date = None
    dates = re.findall(r'(\w+ \d+(?:st|nd|rd|th)?, \d{4})', msg)
    if len(dates) >= 2:
        try:
            # Parse first date (start date)
            start_date_str = dates[0].replace(',', '')
            start_date = datetime.strptime(start_date_str, "%B %d %Y")
        except:
            pass
    
    return {
        "budget": budget,
        "age": age,
        "period": period,
        "start_date": start_date,  # NEW!
        "avoids": avoids,
        "prefers": prefers
    }
```

### Step 2: Fetch Historical Prices from LIMEX (if supported)

```python
def get_historical_prices_bulk(symbols, date):
    """
    Get historical prices for a list of symbols on a specific date.
    """
    global LIMEX_TOKEN
    if not LIMEX_TOKEN:
        get_limex_token()
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LIMEX_TOKEN}'
    }
    
    # Try LIMEX with date parameter (need to check API docs)
    params = {
        'date': date.strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.post(
            LIMEX_QUOTES_URL, 
            headers=headers, 
            data=json.dumps(symbols),
            params=params,  # Pass date as query parameter
            timeout=5
        )
        
        # ... handle response ...
    except Exception as e:
        print(f"Historical prices not available, falling back to live prices")
        return get_live_prices_bulk(symbols)  # Fallback
```

### Step 3: Use Yahoo Finance as Backup

```python
import yfinance as yf

def get_yahoo_historical_prices(symbols, date):
    """
    Fallback to Yahoo Finance for historical prices.
    """
    prices = {}
    date_str = date.strftime('%Y-%m-%d')
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Get data for that specific day
            hist = ticker.history(start=date_str, end=(date + timedelta(days=1)).strftime('%Y-%m-%d'))
            if not hist.empty:
                # Use opening price (what we'd buy at that day)
                prices[symbol] = hist['Open'].iloc[0]
        except Exception as e:
            print(f"Could not fetch historical price for {symbol}: {e}")
    
    return prices
```

---

## 🚀 Implementation Plan

### Phase 1: Test LIMEX Historical Support (15 min)

```python
# Test if LIMEX supports date parameter
test_cell = """
# Test LIMEX Historical Prices
from datetime import datetime, timedelta

test_date = datetime(2024, 1, 1)
test_symbols = ["AAPL", "MSFT"]

# Try with date parameter
params = {'date': '2024-01-01'}
response = requests.post(
    LIMEX_QUOTES_URL,
    headers={'Authorization': f'Bearer {LIMEX_TOKEN}', 'Content-Type': 'application/json'},
    data=json.dumps(test_symbols),
    params=params
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
"""
```

### Phase 2: Implement Yahoo Finance Fallback (30 min)

```bash
# Install yfinance
pip install yfinance
```

```python
def get_historical_prices_bulk(symbols, date):
    """Try LIMEX first, fallback to Yahoo Finance."""
    
    # Try LIMEX historical (if available)
    # ... LIMEX code ...
    
    # Fallback to Yahoo Finance
    print(f"Fetching historical prices from Yahoo Finance for {date.strftime('%Y-%m-%d')}")
    return get_yahoo_historical_prices(symbols, date)
```

### Phase 3: Update Portfolio Builder (10 min)

```python
def build_portfolio(filtered_stocks, inv, risk_score):
    # ... existing code ...
    
    # NEW: Use historical prices if start_date available
    if inv.get('start_date'):
        live_prices = get_historical_prices_bulk(top_tickers, inv['start_date'])
        print(f"Using historical prices from {inv['start_date'].strftime('%Y-%m-%d')}")
    else:
        live_prices = get_live_prices_bulk(top_tickers)
        print(f"WARNING: No start date found, using current prices (may cause budget errors)")
```

---

## 📊 Expected Impact

### Current (with budget safety margins)

```
Budget: $87
Safe Budget: $65 (75% to be safe)
Portfolio: Might only use $65, leaving money on table
Success Rate: ~85%
```

### With Historical Prices

```
Budget: $87
Safe Budget: $83 (95% - no need for huge margin!)
Portfolio: Uses full $83 at historical prices
Success Rate: ~98%
Points: Significantly higher (better capital utilization)
```

---

## 🎯 Next Steps

1. **Test LIMEX**: Check if date parameter works
2. **Install yfinance**: `pip install yfinance` as backup
3. **Implement extraction**: Add `start_date` to parse_context
4. **Add historical fetch**: Create get_historical_prices_bulk
5. **Update builder**: Use historical prices when available
6. **Test thoroughly**: Run 10 iterations to verify

---

## ⚠️ Considerations

### Date Format Issues

- PRISM uses: "January 1st, 2024"
- APIs use: "2024-01-01"
- Need robust date parsing

### Weekend/Holiday Handling

- If start date is Saturday/Sunday, market is closed
- Solution: Use next trading day (Monday)
- Or use previous Friday's close

### Missing Historical Data

- Some stocks might not have data for that date (newly listed)
- Solution: Filter out stocks without historical prices

### Rate Limits

- Yahoo Finance has rate limits
- Solution: Cache prices, batch requests efficiently

---

## 💭 Why This Is Better

1. **Eliminates Price Mismatch**: No more budget breach errors
2. **Better Capital Utilization**: Can use 95% budget instead of 75%
3. **Fairer Comparison**: Evaluating apples-to-apples
4. **Higher Point Scores**: More money deployed = better returns
5. **Production Ready**: Matches how PRISM evaluates internally
