import pandas as pd
import yfinance as yf
from flask import Flask, jsonify, render_template
import datetime

app = Flask(__name__)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_fbi_logic(rsi, price, ma50):
    score = 50
    if rsi < 30: score += 40
    elif rsi < 40: score += 20
    elif rsi > 70: score -= 20
    if price < ma50: score += 10
    score = max(0, min(100, score))
    if score >= 81: return score, "綠色", "明顯轉弱 (極度恐懼)"
    if score >= 61: return score, "深紫色", "弱勢 (出現恐懼)"
    if score >= 41: return score, "淡紫色", "趨弱 (開始降溫)"
    return score, "白色", "穩定 (情緒冷靜)"

@app.route('/api/stock/<symbol>')
def get_stock(symbol):
    try:
        symbol = symbol.upper()
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty:
            return jsonify({"error": f"找不到 {symbol} 的數據"}), 404
        df['RSI'] = calculate_rsi(df['Close'])
        df['MA50'] = df['Close'].rolling(window=50).mean()
        current_price = float(df['Close'].iloc[-1])
        current_rsi = float(df['RSI'].iloc[-1])
        current_ma50 = float(df['MA50'].iloc[-1])
        score, light, status = get_fbi_logic(current_rsi, current_price, current_ma50)
        return jsonify({
            "symbol": symbol,
            "price": round(current_price, 2),
            "rsi": round(current_rsi, 2),
            "score": score,
            "light_color": light,
            "status": status,
            "update_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)