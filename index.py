import os
import google.generativeai as genai
from telegram import Bot
from datetime import datetime
import logging
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get keys from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')
CHANNEL_ID = "@MatheMachineBot"

# Setup Gemini AI
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

async def post_daily_quiz():
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
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        logger.info("✅ Quiz posted successfully!")
        return {"status": "success", "message": "Quiz posted!"}
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "MathMachine Bot is running!", "status": "ok"}

@app.get("/api/quiz")
async def quiz_endpoint():
    result = await post_daily_quiz()
    return result

# IMPORTANT: This makes it work on Vercel!
handler = Mangum(app)