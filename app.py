import csv
import io
import streamlit as st
from datetime import datetime, timedelta
import requests
API_KEY = st.secrets["POLYGON_API_KEY"]

class CPortItem:
    def __init__(self, symbol):
        self.symbol = symbol       

    def __repr__(self):
        return f"{self.symbol}"
    
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

left, right = st.columns([4, 1], vertical_alignment="center")

with left:
    st.title("SmartCatAI")

with right:
    st.image("assets/b553.png", use_container_width=True)

fileTrade = st.file_uploader("eTrade Portfolio File", type=["csv"])

if fileTrade is not None:
    with st.spinner("Please wait..."):
        aReport = []
        aPort = load_port(fileTrade)
        for item in aPort:
            st.write(f"Processing {item.symbol}")