from flask import Flask, render_template, jsonify
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)

# 股價抓取函式 (加強穩定版)
def get_stock_data(symbol):
    try:
        # 使用 yfinance 抓取最近一天的資料
        stock = yf.Ticker(symbol)
        # 增加 interval="1m" 確保抓到最新的價格
        df = stock.history(period="1d", interval="1m")
        
        if df.empty:
            # 如果一分鐘資料沒抓到，改抓普通的日資料
            df = stock.history(period="1d")
            
        if not df.empty:
            current_price = float(df['Close'].iloc[-1])
            prev_close = stock.info.get('previousClose', current_price)
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "change": round(change, 2),
                "percent": round(change_percent, 2),
                "status": "success"
            }
        return {"status": "error", "message": "No data found"}
    except Exception as e:
        print(f"抓取 {symbol} 出錯: {e}")
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
    # 這是 Render 部署的關鍵：讀取環境變數 PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)