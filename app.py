import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# --- 網頁設定 ---
st.set_page_config(page_title="均線交叉策略回測系統", layout="wide")
st.title("📈 均線交叉策略 (金叉/死叉) 回測系統")
st.markdown("輸入 YFinance 代號，自訂均線參數與資金，系統將自動回測並視覺化輸出。")

# --- 側邊欄：參數設定 ---
st.sidebar.header("⚙️ 策略參數設定")
ticker = st.sidebar.text_input("標的代號 (YFinance)", value="2330.TW", help="例如台積電為 2330.TW，蘋果為 AAPL")
capital = st.sidebar.number_input("初始資金", min_value=1000, value=100000, step=10000)
fast_ma_len = st.sidebar.number_input("短天期均線 (Fast MA)", min_value=2, value=10, step=1)
slow_ma_len = st.sidebar.number_input("長天期均線 (Slow MA)", min_value=5, value=20, step=1)

# 日期區間設定
st.sidebar.subheader("📅 資料抓取區間")
end_date = st.sidebar.date_input("結束日期", value=datetime.today())
start_date = st.sidebar.date_input("開始日期", value=datetime.today() - timedelta(days=365*5)) # 預設抓5年

if st.sidebar.button("開始回測"):
    with st.spinner("正在下載資料並運算回測結果..."):
        try:
            # --- 1. 獲取資料 ---
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if df.empty:
                st.error("找不到該標的的資料，請確認代號或日期區間是否正確。")
            else:
                # 處理 yfinance 可能回傳的 MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(1)
                
                # --- 2. 計算均線與訊號 ---
                df['Fast_MA'] = df['Close'].rolling(window=fast_ma_len).mean()
                df['Slow_MA'] = df['Close'].rolling(window=slow_ma_len).mean()
                
                # 產生交易訊號 (1 為持有, 0 為空手)
                # 當短均線大於長均線時看多
                df['Signal'] = 0.0
                df['Signal'] = np.where(df['Fast_MA'] > df['Slow_MA'], 1.0, 0.0)
                
                # 計算進出場點位 (1 為買進金叉, -1 為賣出死叉)
                df['Position'] = df['Signal'].diff()
                
                # --- 3. 回測計算 ---
                trades = []
                current_capital = capital
                holdings = 0
                buy_price = 0
                
                for index, row in df.iterrows():
                    if row['Position'] == 1.0: # 金叉進場
                        buy_price = row['Close']
                        holdings = current_capital / buy_price # 假設可買碎股以利計算完全報酬
                    elif row['Position'] == -1.0 and holdings > 0: # 死叉出場
                        sell_price = row['Close']
                        profit = (sell_price - buy_price) * holdings
                        profit_percent = (sell_price - buy_price) / buy_price
                        current_capital += profit
                        
                        trades.append({
                            'Buy_Date': index,
                            'Sell_Date': index,
                            'Buy_Price': buy_price,
                            'Sell_Price': sell_price,
                            'Profit': profit,
                            'Profit_Percent': profit_percent
                        })
                        holdings = 0
                
                # 若最後一天仍持有，以最後一天收盤價計算未實現損益
                if holdings > 0:
                    sell_price = df.iloc[-1]['Close']
                    profit = (sell_price - buy_price) * holdings
                    current_capital += profit
                
                # --- 4. 計算分析數據 ---
                total_trades = len(trades)
                winning_trades = sum(1 for t in trades if t['Profit'] > 0)
                losing_trades = total_trades - winning_trades
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                gross_profit = sum(t['Profit'] for t in trades if t['Profit'] > 0)
                gross_loss = abs(sum(t['Profit'] for t in trades if t['Profit'] < 0))
                profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0)
                
                total_return = current_capital - capital
                return_percent = (total_return / capital) * 100
                
                # --- 5. 輸出視覺化圖表 (Plotly) ---
                st.subheader("📊 價格與策略視覺化圖表")
                
                fig = go.Figure()
                
                # Ｋ線圖
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線'))
                # 短均線
                fig.add_trace(go.Scatter(x=df.index, y=df['Fast_MA'], mode='lines', name=f'短均線 ({fast_ma_len})', line=dict(color='orange')))
                # 長均線
                fig.add_trace(go.Scatter(x=df.index, y=df['Slow_MA'], mode='lines', name=f'長均線 ({slow_ma_len})', line=dict(color='blue')))
                
                # 標示買點 (綠色向上箭頭)
                buy_signals = df[df['Position'] == 1.0]
                fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Fast_MA'], mode='markers', name='買進 (金叉)', 
                                         marker=dict(symbol='triangle-up', size=15, color='green')))
                
                # 標示賣點 (紅色向下箭頭)
                sell_signals = df[df['Position'] == -1.0]
                fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Fast_MA'], mode='markers', name='賣出 (死叉)', 
                                         marker=dict(symbol='triangle-down', size=15, color='red')))
                
                # 加入快速日期切換按鈕 (符合您的自訂切分需求)
                fig.update_xaxes(
                    rangeslider_visible=True,
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="近1月", step="month", stepmode="backward"),
                            dict(count=3, label="近3月", step="month", stepmode="backward"),
                            dict(count=6, label="近半年", step="month", stepmode="backward"),
                            dict(count=1, label="近1年", step="year", stepmode="backward"),
                            dict(count=3, label="近3年", step="year", stepmode="backward"),
                            dict(count=5, label="近5年", step="year", stepmode="backward"),
                            dict(step="all", label="全部資料")
                        ])
                    )
                )
                
                fig.update_layout(height=600, template='plotly_dark', margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                # --- 6. 顯示回測分析數據 ---
                st.subheader("📋 策略回測績效")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                col1.metric("期末總資金", f"${current_capital:,.2f}", f"{return_percent:.2f}%")
                col2.metric("總淨利 (報酬金額)", f"${total_return:,.2f}")
                col3.metric("交易總次數", f"{total_trades} 次")
                col4.metric("策略勝率", f"{win_rate:.2f}%")
                col5.metric("獲利因子 (Profit Factor)", f"{profit_factor:.2f}")

        except Exception as e:
            st.error(f"發生錯誤: {e}")