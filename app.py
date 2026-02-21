import streamlit as st
from datetime import datetime, timedelta
import requests
API_KEY = st.secrets["POLYGON_API_KEY"]

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



left, right = st.columns([4, 1], vertical_alignment="center")

with left:
    st.title("SmartCatAI")

with right:
    st.image("assets/b553.png", use_container_width=True)



st.write(get_recent_ex_dividend_dates("AAPL"))








fileTrade = st.file_uploader("eTrade Portfolio File", type=["csv"])