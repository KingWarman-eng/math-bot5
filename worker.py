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
    """Remove ALL LaTeX and clean up formatting"""
    # Remove all LaTeX delimiters
    text = re.sub(r'\\\(|\\\)', '', text)
    text = re.sub(r'\\\[|\\\]', '', text)
    text = re.sub(r'\$', '', text)
    
    # Convert LaTeX fractions to plain text
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    
    # Convert square roots
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', text)
    
    # Fix other LaTeX
    text = re.sub(r'\\times', 'x', text)
    text = re.sub(r'\\cdot', '*', text)
    text = re.sub(r'\\pm', '+/-', text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s+', '\n', text)
    
    return text.strip()

async def post_daily_quiz():
    try:
        logger.info("Generating quiz with DeepSeek...")
        
        prompt = """
        Create 5 math quiz questions for high school students.
        Topics: algebra, geometry, and calculus.
        
        CRITICAL FORMATTING RULES:
        1. Use NO LaTeX notation. NO \\(, \\), \\frac, \\sqrt, \\times.
        2. Write everything in PLAIN TEXT.
        3. Use '^' for powers (like x^2).
        4. Use '/' for fractions (like 1/2).
        5. Use 'sqrt()' for square roots.
        6. Each question MUST be on its own line.
        7. Format each question EXACTLY like this:

        Q1: [Question text]
        A) [Option]
        B) [Option]
        C) [Option]
        D) [Option]
        Answer: [Letter]
        Explanation: [Brief explanation]

        Q2: [Question text]
        ...

        Use this example format:
        Q1: Solve for x: 2x^2 + 5x - 3 = 0
        A) x = -3 or x = 1/2
        B) x = 3 or x = -1/2
        C) x = -1 or x = 3/2
        D) x = 1 or x = -3/2
        Answer: A
        Explanation: Using the quadratic formula: x = (-5 +/- sqrt(25 + 24))/4 = (-5 +/- 7)/4, so x = -3 or x = 1/2.

        DO NOT use any symbols that look like LaTeX. Use plain text only.
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
        
        # Clean up any remaining LaTeX
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
        
        logger.info(f"✅ Quiz posted successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Running Daily Quiz...")
    asyncio.run(post_daily_quiz())
    logger.info("🏁 Job finished.")