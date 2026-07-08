import os
from telegram import Bot
from datetime import datetime
import logging
import requests
import asyncio
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
CHANNEL_ID = -1003850393774  # Your channel ID

def clean_text(text):
    """Clean up LaTeX and formatting for better readability"""
    # Remove LaTeX math delimiters
    text = re.sub(r'\\\(|\\\)', '', text)  # Remove \( and \)
    text = re.sub(r'\\\[|\\\]', '', text)  # Remove \[ and \]
    text = re.sub(r'\$', '', text)  # Remove $ signs
    
    # Fix common LaTeX commands
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)  # Simplify fractions
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', text)  # Simplify square roots
    text = re.sub(r'\\times', 'x', text)  # Fix multiplication
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s+', '\n', text)
    
    return text.strip()

async def post_daily_quiz():
    try:
        logger.info("Generating quiz with DeepSeek...")
        
        prompt = """
        Create 5 math quiz questions for high school students.
        Topics: algebra, geometry, and calculus.
        
        FORMAT EXACTLY LIKE THIS:
        
        Q1: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Answer: [Letter]
        Explanation: [Brief explanation]
        
        Q2: [Question text]
        ...
        
        DO NOT use LaTeX symbols like \\(, \\), \\frac, \\sqrt. Use plain text instead.
        Use 'x' for multiplication, 'sqrt()' for square roots, and '/' for fractions.
        Keep each question and its options on separate lines.
        Make sure questions are clear and easy to read.
        """
        
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
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API Error: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        raw_quiz = data['choices'][0]['message']['content']
        
        # Clean up the formatting
        quiz_text = clean_text(raw_quiz)
        
        today = datetime.now().strftime("%B %d, %Y")
        message = f"📚 **Daily Math Quiz - {today}**\n\n"
        message += quiz_text
        message += "\n\n---\n"
        message += "🔗 **MatheMachine.site** - Learn more at [mathemachine.site](https://mathemachine.site)"
        
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Quiz posted successfully to channel!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Running Daily Quiz...")
    asyncio.run(post_daily_quiz())
    logger.info("🏁 Job finished.")