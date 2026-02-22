import csv
import io
import streamlit as st
from datetime import datetime, timedelta
import requests
import html
import pytz

API_KEY = st.secrets["POLYGON_API_KEY"]

class CPortItem:
    def __init__(self, symbol):
        self.symbol = symbol       

    def __repr__(self):
        return f"{self.symbol}"
    
class CReportItem:
    def __init__(self, symbol, dates, has_dates, score):
        self.symbol = symbol
        self.dates = dates
        self.has_dates = has_dates
        self.score = score

    def __repr__(self):
        return f"{self.symbol} - {self.dates} - {self.has_dates} - {self.score}"
def load_port(file):
    a = []
    try:
        text_stream = io.TextIOWrapper(fileTrade, encoding="utf-8")
        reader = csv.reader(text_stream)
        
        for _ in range(11):
            next(reader)

        for row in reader:
            try:
                if row[0] == "CASH":
                    return a
                cPI = CPortItem(row[0])
                a.append(cPI)               
            except:
                continue
    
    except FileNotFoundError:
        st.error("File not found. Please check the file path and try again.")   

    return a

def get_recent_ex_dividend_dates(ticker):
    url = 'https://api.polygon.io/v3/reference/dividends'
    params = {
        'ticker': ticker,
        'order': 'desc',  # Most recent first
        'sort': 'ex_dividend_date',
        'limit': 24,  # Get last 24 months
        'apiKey': API_KEY
    }

    dtPast = datetime.now() - timedelta(days=52)
    response = requests.get(url, params=params)
    data = response.json()

    aData = []
    print(f"Count: {len(data['results'])}")
    if 'results' in data:
        for dividend in data['results']:
            #print(dividend["ex_dividend_date"])
            if datetime.strptime(dividend['ex_dividend_date'], "%Y-%m-%d") > dtPast:
                aData.append(dividend['ex_dividend_date'])

        return aData
    return []



def to_est(unix_ts):
    """
    Convert a Unix timestamp (ms or s) to Eastern Time.
    Returns a datetime object in EST/EDT.
    """
    # Detect milliseconds vs seconds
    if unix_ts > 1e12:  # ms
        unix_ts /= 1000.0

    # Create timezone objects
    utc = pytz.UTC
    est = pytz.timezone("US/Eastern")

    # Convert
    dt_utc = datetime.fromtimestamp(unix_ts, utc)
    dt_est = dt_utc.astimezone(est)
    
    return dt_est

def get_stock_prices(ticker):
    aReturn = []
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    print(f"Start Date: {start_date}")
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    print(f"End Date: {end_date}")

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 5000,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200: 
        data = response.json()
        for item in data.get('results', []):
            print(to_est(item['t']) , str(item['c']))
            aReturn.append(item['c'])  # 'c' is the closing price
    
    return aReturn

def moving_average(prices, window):
    """
    Returns the latest simple moving average (SMA) over `window` days.
    Pure Python (no numpy/pandas).
    """
    if window <= 0:
        raise ValueError("window must be a positive integer.")
    if len(prices) < window:
        raise ValueError(f"Need at least {window} prices to compute the moving average.")
    
    last_window = prices[-window:]
    return sum(last_window) / window

def moving_average_slope(prices, window, lookback=10):
    """
    Returns the slope of the moving average over `lookback` days:
    MA(window) today minus MA(window) from `lookback` trading days ago.
    """
    if window <= 0 or lookback <= 0:
        raise ValueError("window and lookback must be positive integers.")
    # We need enough prices to compute MA today AND MA lookback days ago.
    # The MA value `lookback` days ago requires a full `window` ending at index -lookback-1.
    required = window + lookback
    if len(prices) < required:
        raise ValueError(f"Need at least {required} prices to compute MA slope (window={window}, lookback={lookback}).")
    
    # MA today (uses last `window` prices)
    ma_today = sum(prices[-window:]) / window
    
    # MA from `lookback` days ago (uses the `window` that ends at index -lookback-1)
    end_idx = len(prices) - lookback
    start_idx = end_idx - window
    ma_past = sum(prices[start_idx:end_idx]) / window
    
    return ma_today - ma_past

def score_stock_trend(ticker, aPrices):
    
    ma50 = moving_average(aPrices, window=50)
    ma100 = moving_average(aPrices, window=100)
    ma200 = moving_average(aPrices, window=200)
    print(f"MA50: {ma50} MA100: {ma100} MA200: {ma200}")

    slope50 = moving_average_slope(aPrices, window=50, lookback=10)
    slope100 = moving_average_slope(aPrices, window=100, lookback=10)
    slope200 = moving_average_slope(aPrices, window=200, lookback=10)
    print(f"Slopes 50 {slope50} 100 {slope100} 200 {slope200}")

    pct_slope50 = slope50 / ma50
    pct_slope100 = slope100 / ma100
    pct_slope200 = slope200 / ma200
    print(f"Pct Slopes 50 {pct_slope50} 100 {pct_slope100} 200 {pct_slope200}")

    trend_strength = (
        pct_slope50 * 0.5 +
        pct_slope100 * 0.3 +
        pct_slope200 * 0.2
    )
    print(f"Trend Strength: {trend_strength}")

    return round(trend_strength, 4)

def get_recent_ex_dividend_dates(ticker):
    url = 'https://api.polygon.io/v3/reference/dividends'
    params = {
        'ticker': ticker,
        'order': 'desc',  # Most recent first
        'sort': 'ex_dividend_date',
        'limit': 24,  # Get last 24 months
        'apiKey': API_KEY
    }

    dtPast = datetime.now() - timedelta(days=52)
    response = requests.get(url, params=params)
    data = response.json()

    aData = []
    print(f"Count: {len(data['results'])}")
    if 'results' in data:
        for dividend in data['results']:
            #print(dividend["ex_dividend_date"])
            if datetime.strptime(dividend['ex_dividend_date'], "%Y-%m-%d") > dtPast:
                aData.append(dividend['ex_dividend_date'])

        return aData
    return []

def render_zebra_table(headers, rows):
    # Escape text to avoid HTML injection / rendering issues
    def esc(x):
        return html.escape(str(x))

    thead = "".join(f"<th>{esc(h)}</th>" for h in headers)

    tbody_rows = []
    for r in rows:   
        html_dates = r.dates.replace(", ", "<br/>")     
        tds = (
            f"<td>{esc(r.symbol)}</td>"
            #f"<td style='text-align:center;'>{'✅' if r.has_dates else '—'}</td>"
            #f"<td>{esc(r.dates)}</td>"
            f"<td>{html_dates}</td>"
            f"<td style='text-align:center;'>{esc(r.score)}</td>"
        )
        
        tbody_rows.append(f"<tr>{tds}</tr>")  
    
    tbody = "".join(tbody_rows)

    return f"""
    <style>
      .zebra-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
      }}
     .zebra-table thead th {{
        background: #203C50;
        color: white;
        text-align: left;
        padding: 12px 12px;
        font-weight: 800;
        letter-spacing: 0.4px;
        text-transform: none;
        border-bottom: 1px solid rgba(255,255,255,0.25);
        font-size: 1.02rem;
        text-shadow: 0 1px 0 rgba(0,0,0,0.25);
      }}

      .zebra-table tbody td {{
        padding: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
      }}
      .zebra-table tbody tr:nth-child(even) {{
        background-color: rgba(0, 0, 0, 0.06);
      }}
    </style>

    <table class="zebra-table">
      <thead><tr>{thead}</tr></thead>
      <tbody>{tbody}</tbody>
    </table>
    """

left, right = st.columns([4, 1], vertical_alignment="center")

with left:
    st.title("SmartCatAI")

with right:
    st.image("assets/b553.png", use_container_width=True)

fileTrade = st.file_uploader("eTrade Portfolio File", type=["csv"])

headers = ["Ticker", "Dates", "Score"]

nIndex = 0
aReport = []
if fileTrade is not None:
    with st.spinner("Please wait..."):
        aReport = []
        aPort = load_port(fileTrade)

        for item in aPort:
            dScore = -666
            aPrices = get_stock_prices(item.symbol)
            if len(aPrices) >= 210:
                dScore = score_stock_trend(item.symbol, aPrices)
            
            strDates = ""
            aDates = get_recent_ex_dividend_dates(item.symbol)
            for dtDate in aDates:
                strDates = strDates + dtDate + ", "

            bHasGreater = False
            for dtDate in aDates:
                if datetime.strptime(dtDate, "%Y-%m-%d") >= datetime.now():
                    bHasGreater = True
                    break

            if not bHasGreater or dScore < 0:
                aReport.append(CReportItem(item.symbol, strDates, bHasGreater, dScore))

            # if nIndex > 3:
            #     break
            # nIndex = nIndex + 1
        st.markdown(render_zebra_table(headers, aReport), unsafe_allow_html=True)

