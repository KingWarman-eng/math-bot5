import os
from telegram import Bot
from datetime import datetime
import logging
from google import genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = "@MatheMachineBot"

# New Gemini client
client = genai.Client(api_key=GEMINI_KEY)

def post_daily_quiz():
    try:
        logger.info("Generating quiz...")
        
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
        
        # USING gemini-1.5-flash (confirmed working)
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        quiz_text = response.text
        
        today = datetime.now().strftime("%B %d, %Y")
        message = f"📚 **Daily Math Quiz - {today}**\n\n"
        message += quiz_text
        message += "\n\n🔗 More at [mathemachine.site](https://mathemachine.site)"
        
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(
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
    post_daily_quiz()
    logger.info("🏁 Job finished.")