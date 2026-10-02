from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from stock import Stock

st.set_page_config(layout="wide", page_title="Stock Price Analysis")
st.title("Stock Analysis")

st.sidebar.title("Inputs")
ticker = st.sidebar.text_input("Enter stock ticker symbol", value="AAPL").upper()
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", date.today() - timedelta(days=365))
end_date = col2.date_input("End Date", date.today())
ma_window = st.sidebar.slider("Moving Average", min_value=5, max_value=200, value=50)
run_analysis = st.sidebar.button("Run Analysis", type="primary")


@st.cache_data
def get_stock(ticker, start, end, ma_window):
    return Stock(ticker, start, end, ma_window)


tab1, tab2 = st.tabs(["Single Stock Analysis", "Portfolio Comparison"])
tickers = tab2.text_input("Enter ticker symbols separated by commas", value="AAPL, MSFT, GOOG")

if run_analysis:
    with tab1:
        with st.spinner(f"Fetching {ticker} data..."):
            stock = get_stock(ticker, start_date, end_date, ma_window)
        if stock.data is None:
            st.error(stock.message)
        else:
            st.success(stock.message)
            df = stock.data
            col1, col2, col3 = st.columns(3)
            col1.metric("Last Close", f"${df['Close'].iloc[-1]:.2f}")
            col2.metric("Cum. Return", f"{df['return'].sum():.2%}")
            col3.metric("Trading Days", len(df))
            st.plotly_chart(px.line(df, y=["Close", "MA"], title=f"{ticker} Close and {ma_window}-Day Moving Average"))
            st.plotly_chart(stock.plot_performance())
            st.plotly_chart(stock.plot_return_dist())
            st.subheader("Daily Return Statistics")
            st.dataframe(df["return"].describe())

    with tab2:
        performance = {}
        for symbol in [t.strip().upper() for t in tickers.split(",") if t.strip()]:
            with st.spinner(f"Fetching {symbol} data..."):
                stock = get_stock(symbol, start_date, end_date, ma_window)
            if stock.data is None:
                st.error(stock.message)
            else:
                # Subtract the first return so every line starts at exactly 0.0
                performance[symbol] = stock.data["return"].cumsum() - stock.data["return"].iloc[0]
        if performance:
            fig = px.line(pd.DataFrame(performance), title="Zero-Based Cumulative Performance",
                          labels={"value": "Cum. Return", "variable": "Ticker"})
            fig.update_layout(yaxis_tickformat=".1%", hovermode="x unified")
            st.plotly_chart(fig)
