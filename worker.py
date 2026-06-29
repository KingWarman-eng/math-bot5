import os
import google.generativeai as genai
from telegram import Bot
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get from GitHub Secrets
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = "@MatheMachineBot"

# Setup Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def post_daily_quiz():
    """Generate and post quiz"""
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
        
        response = model.generate_content(prompt)
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