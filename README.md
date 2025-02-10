# botverse

To set up and run the bot:

1. Create .env file:

TELEGRAM_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@localhost/nprbot

2. Install requirements:

pip install -r requirements.txt

3. Run the bot:

python main.py

Key features:

- Users interact via Telegram commands (/start, /setprice, /getprice)

- Checks Binance P2P prices every minute

- Stores user preferences in PostgreSQL

- Sends Telegram notifications when target price is reached


To deploy to production:

1. Create a PostgreSQL database (e.g., on AWS RDS or ElephantSQL)

2. Set up environment variables in your hosting platform

3. Use process manager like PM2:



pm2 start main.py --name npr-bot



Telegram Bot Commands:

- /start - Show welcome message

- /setprice 132.5 - Set target price to 132.5 NPR

- /getprice - Get current P2P price

Note: You'll need to:

1. Create a Telegram bot via @BotFather

2. Enable the Binance P2P API

3. Set up proper error handling and logging

4. Add input validation for prices

5. Implement rate limiting if needed

This implementation provides a foundation that can be extended with additional features like multiple exchange support, price history tracking, or multiple notification channels.