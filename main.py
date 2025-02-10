# main.py
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

load_dotenv()

# Database setup
Base = declarative_base()
DATABASE_URL = os.getenv("DATABASE_URL")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True)
    target_price = Column(Float)
    notification_method = Column(String, default='telegram')

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Telegram setup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TELEGRAM_TOKEN)

# Binance P2P API configuration
BINANCE_API_URL = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

def fetch_p2p_price():
    payload = {
        "asset": "USDT",
        "fiat": "NPR",
        "tradeType": "BUY",
        "page": 1,
        "rows": 1,
        "countries": []
    }
    
    try:
        response = requests.post(BINANCE_API_URL, json=payload)
        data = response.json()
        return float(data['data'][0]['adv']['price'])
    except Exception as e:
        logging.error(f"Error fetching P2P price: {e}")
        return None

def check_prices():
    current_price = fetch_p2p_price()
    if current_price is None:
        return

    session = Session()
    users = session.query(User).all()
    
    for user in users:
        if user.target_price >= current_price:
            send_notification(user.chat_id, current_price)
    
    session.close()

def send_notification(chat_id, price):
    message = f"🚨 NPR P2P Price Alert! Current Price: {price}"
    bot.send_message(chat_id=chat_id, text=message)

# Telegram command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Welcome to NPR P2P Price Bot!\n"
        "Set your target price using /setprice <amount>"
    )

def set_price(update: Update, context: CallbackContext):
    try:
        chat_id = update.message.chat_id
        price = float(context.args[0])
        
        session = Session()
        user = session.query(User).filter_by(chat_id=chat_id).first()
        
        if not user:
            user = User(chat_id=chat_id, target_price=price)
            session.add(user)
        else:
            user.target_price = price
            
        session.commit()
        session.close()
        
        update.message.reply_text(f"✅ Target price set to NPR {price}")
        
    except (IndexError, ValueError):
        update.message.reply_text("⚠️ Usage: /setprice <desired_price>")

def get_price(update: Update, context: CallbackContext):
    current_price = fetch_p2p_price()
    if current_price:
        update.message.reply_text(f"Current NPR P2P Price: {current_price}")
    else:
        update.message.reply_text("Could not fetch current price")

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(check_prices, 'interval', minutes=1)
scheduler.start()

# Start bot
updater = Updater(TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("setprice", set_price))
dp.add_handler(CommandHandler("getprice", get_price))

updater.start_polling()
updater.idle()