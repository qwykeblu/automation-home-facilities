from src.bot.handlers import setup_bot
import os
from dotenv import load_dotenv

# файл ініціалізації всієї програми

# TODO: зробити так шоб тут все було по мінімуму та зрозуміло

def main():
    load_dotenv()
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if TOKEN is None:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
    application = setup_bot(TOKEN)

    # Начать опрос серверов Telegram
    application.run_polling()

if __name__ == '__main__':
    main()
