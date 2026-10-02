import telebot, requests, time
from datetime import datetime
TOKEN="8589946156:AAFaPJm9PjdGBQhpNOHzzBLNXaTxMN21kzY"
bot=telebot.TeleBot(TOKEN)
def get_prices(symbol):
    try:
        headers={'User-Agent':'Mozilla/5.0'}
        url=f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}=X?interval=1h&range=5d"
        r=requests.get(url,headers=headers,timeout=10).json()
        prices=r['chart']['result'][0]['indicators']['quote'][0]['close']
        prices=[p for p in prices if p is not None]
        return prices[-50:]
    except:
        try:
            url2=f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1h&range=5d"
            r=requests.get(url2,headers=headers,timeout=10).json()
            prices=r['chart']['result'][0]['indicators']['quote'][0]['close']
            prices=[p for p in prices if p is not None]
            return prices[-50:]
        except: return None
def calc_rsi(prices,period=14):
    if len(prices)<period+1: return 50
    gains=0;losses=0
    for i in range(1,period+1):
        change=prices[-i]-prices[-i-1]
        if change>0: gains+=change
        else: losses+=abs(change)
    if losses==0: return 70
    rs=gains/losses
    return 100-(100/(1+rs))
@bot.message_handler(commands=['start'])
def start(m):
    mk=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    mk.add("EURUSD","GBPUSD","XAUUSD","BTC-USD")
    bot.send_message(m.chat.id,f"اهلا {m.from_user.first_name}!\nالبوت شغال 24 ساعة ✅",reply_markup=mk)
@bot.message_handler(func=lambda m: m.text in ["EURUSD","GBPUSD","XAUUSD","BTC-USD"])
def quick(m): handle_signal(m,m.text)
@bot.message_handler(commands=['signal'])
def signal_cmd(m):
    p=m.text.split()
    s=p[1].upper() if len(p)>1 else "EURUSD"
    handle_signal(m,s)
def handle_signal(m,symbol):
    bot.send_message(m.chat.id,f"⏳ {symbol}...")
    prices=get_prices(symbol)
    if not prices: bot.send_message(m.chat.id,"❌ Failed");return
    rsi=calc_rsi(prices);price=prices[-1]
    t=datetime.now().strftime("%H:%M")
    if rsi<30: sig=f"🟢 BUY STRONG\n{symbol} {price:.5f}\nRSI {rsi:.1f} {t}"
    elif rsi>70: sig=f"🔴 SELL STRONG\n{symbol} {price:.5f}\nRSI {rsi:.1f} {t}"
    elif rsi<45: sig=f"🟢 BUY\n{symbol} {price:.5f}\nRSI {rsi:.1f} {t}"
    else: sig=f"🔴 SELL\n{symbol} {price:.5f}\nRSI {rsi:.1f} {t}"
    bot.send_message(m.chat.id,sig)
while True:
    try: bot.infinity_polling()
    except: time.sleep(5)
