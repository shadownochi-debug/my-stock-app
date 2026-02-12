from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import pytz

app = Flask(__name__)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        # 抓取一個月歷史資料計算 RSI
        df = stock.history(period="1mo")
        
        if not df.empty and len(df) >= 14:
            current_price = df['Close'].iloc[-1]
            rsi_series = calculate_rsi(df['Close'])
            current_rsi = round(rsi_series.iloc[-1], 2)
            
            # --- FBI 投資分數與顏色邏輯 ---
            # 這裡我們模擬妳 HTML 想要的顏色邏輯
            score = round(100 - current_rsi, 1)
            status_text = "觀望中"
            light_color = "白色"
            
            if current_rsi <= 35:
                status_text = "超賣 / 強烈建議買入"
                light_color = "綠色"
            elif current_rsi >= 70:
                status_text = "超買 / 建議減碼"
                light_color = "深紫色"
            elif score > 50:
                status_text = "穩定成長中"
                light_color = "淡紫色"

            # 設定台灣時間
            tw_tz = pytz.timezone('Asia/Taipei')
            now_tw = datetime.now(tw_tz).strftime('%H:%M:%S')

            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "rsi": current_rsi,
                "score": score,
                "status": status_text,
                "light_color": light_color,
                "update_time": now_tw
            }
        return {"status": "error", "message": "數據不足"}
    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def stock_api(symbol):
    data = get_stock_data(symbol.upper())
    # 這裡無論如何都回傳 200，避免前端 JS 噴掉，讓前端去判斷內容
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)