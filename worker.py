import os
from telegram import Bot
from datetime import datetime
import logging
import requests
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
CHANNEL_ID = "@MatheMachineBot"  # Change to your channel!

async def post_daily_quiz():
    try:
        logger.info("Generating quiz with DeepSeek...")
        
        prompt = """
        Create 5 math quiz questions for high school students.
        Topics: algebra, geometry, and calculus.
        Include answers and explanations.
        Format:
        Q1: [question]
        A) [option]
        B) [option]
        C) [option]
        D) [option]
        Answer: [correct letter]
        Explanation: [explanation]
        """
        
        # DeepSeek API call
        url = "https://api.deepseek.com/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API Error: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        quiz_text = data['choices'][0]['message']['content']
        
        today = datetime.now().strftime("%B %d, %Y")
        message = f"📚 **Daily Math Quiz - {today}**\n\n"
        message += quiz_text
        message += "\n\n🔗 More at [mathemachine.site](https://mathemachine.site)"
        
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info("✅ Quiz posted successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Running Daily Quiz...")
    asyncio.run(post_daily_quiz())
    logger.info("🏁 Job finished.")