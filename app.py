from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

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
        # 抓取過去一個月的歷史資料來計算 RSI
        df = stock.history(period="1mo")
        
        if not df.empty and len(df) >= 14:
            current_price = df['Close'].iloc[-1]
            prev_close = stock.info.get('previousClose', current_price)
            
            # 計算 RSI
            rsi_series = calculate_rsi(df['Close'])
            current_rsi = rsi_series.iloc[-1]
            
            # 簡單的投資分數邏輯 (可以根據 RSI 定義)
            # RSI < 30 (超賣) 分數高, RSI > 70 (超買) 分數低
            score = 100 - current_rsi 
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(current_price - prev_close, 2),
                "percent": round(((current_price - prev_close) / prev_close) * 100, 2),
                "rsi": round(current_rsi, 2),
                "score": round(score, 1),
                "status": "success"
            }
        return {"status": "error", "message": "Data insufficient"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<symbol>')
def stock_api(symbol):
    data = get_stock_data(symbol.upper())
    if data["status"] == "success":
        return jsonify(data)
    else:
        return jsonify(data), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)