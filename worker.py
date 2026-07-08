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
    """Clean up formatting and ensure Unicode math symbols"""
    # Remove LaTeX delimiters
    text = re.sub(r'\\\(|\\\)', '', text)
    text = re.sub(r'\\\[|\\\]', '', text)
    text = re.sub(r'\$', '', text)
    
    # Convert common LaTeX to Unicode
    replacements = {
        r'\\frac\{1\}\{2\}': '½',
        r'\\frac\{1\}\{3\}': '⅓',
        r'\\frac\{1\}\{4\}': '¼',
        r'\\frac\{2\}\{3\}': '⅔',
        r'\\frac\{3\}\{4\}': '¾',
        r'\\frac\{([^}]+)\}\{([^}]+)\}': r'\1/\2',
        r'\\sqrt\{([^}]+)\}': r'√(\1)',
        r'\\times': '×',
        r'\\cdot': '·',
        r'\\pm': '±',
        r'\\infty': '∞',
        r'\\sum': '∑',
        r'\\int': '∫',
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\theta': 'θ',
        r'\\pi': 'π',
        r'\\Delta': 'Δ',
        r'\\rightarrow': '→',
        r'\\left': '',
        r'\\right': '',
        r'\\\{': '{',
        r'\\\}': '}',
    }
    
    for latex, unicode_char in replacements.items():
        text = re.sub(latex, unicode_char, text)
    
    # Convert x^2 to x², x^3 to x³, etc.
    text = re.sub(r'\^2', '²', text)
    text = re.sub(r'\^3', '³', text)
    text = re.sub(r'\^4', '⁴', text)
    text = re.sub(r'\^5', '⁵', text)
    text = re.sub(r'\^6', '⁶', text)
    text = re.sub(r'\^7', '⁷', text)
    text = re.sub(r'\^8', '⁸', text)
    text = re.sub(r'\^9', '⁹', text)
    text = re.sub(r'\^0', '⁰', text)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Add proper spacing between questions
    # Split by Q1:, Q2:, etc. and add extra newlines
    text = re.sub(r'(Q\d+:)', r'\n\n\1', text)
    
    # Add spacing between options
    text = re.sub(r'(A\)|B\)|C\)|D\))', r'\n\1', text)
    
    # Add spacing before Answer and Explanation
    text = re.sub(r'(Answer:)', r'\n\n\1', text)
    text = re.sub(r'(Explanation:)', r'\n\1', text)
    
    # Clean up extra newlines at start
    text = text.strip()
    
    return text

async def post_daily_quiz():
    try:
        logger.info("Generating quiz with DeepSeek...")
        
        prompt = """
        Create 5 math quiz questions for high school students.
        Topics: algebra, geometry, and calculus.
        
        FORMATTING RULES:
        1. Use LaTeX for equations but I will convert them to Unicode.
        2. Use \\( and \\) for inline equations.
        3. Use \\frac{1}{2} for fractions, \\sqrt{} for square roots.
        4. Each question MUST be formatted like this:

        Q1: [Question text with equations]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Answer: [Letter]
        Explanation: [Brief explanation]

        Q2: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Answer: [Letter]
        Explanation: [Brief explanation]

        Make sure questions are appropriate for high school level.
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
        
        # Clean up and convert to Unicode with proper spacing
        quiz_text = clean_text(raw_quiz)
        
        today = datetime.now().strftime("%B %d, %Y")
        message = f"📚 **Daily Math Quiz - {today}**\n\n"
        message += quiz_text
        message += "\n\n---\n"
        message += "🔗 **MatheMachine.site** - [mathemachine.site](https://mathemachine.site)"
        
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