import os
from telegram import Bot
from datetime import datetime
import logging
import requests
import asyncio
import re
import base64
import json
import subprocess
import tempfile
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
CHANNEL_ID = -1003850393774

def generate_equation_image(latex_code, output_path="equation.png"):
    """Convert LaTeX to image using klatexformula or similar tool"""
    try:
        # Method 1: Using klatexformula (if installed)
        cmd = [
            "klatexformula",
            "--latexinput", latex_code,
            "--output", output_path,
            "--format", "png"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return output_path
        
        # Method 2: Using online API as fallback
        return generate_equation_online(latex_code, output_path)
        
    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        return None

def generate_equation_online(latex_code, output_path):
    """Use online LaTeX to image API as fallback"""
    try:
        # Using QuickLaTeX API (free)
        url = "https://www.quicklatex.com/latex3.f"
        
        payload = {
            "formula": latex_code,
            "fsize": "18px",
            "fcolor": "000000",
            "mode": "0"
        }
        
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            # Get the image URL from response
            image_url = response.text.strip()
            img_response = requests.get(image_url)
            
            with open(output_path, 'wb') as f:
                f.write(img_response.content)
            
            return output_path
        
        return None
        
    except Exception as e:
        logger.error(f"Online API failed: {e}")
        return None

def extract_latex_blocks(text):
    """Extract LaTeX expressions from text"""
    # Find all LaTeX expressions between \( \) or \[ \]
    pattern = r'\\\(.*?\\\)|\\\[.*?\\\]'
    matches = re.findall(pattern, text)
    return matches

def replace_with_images(text):
    """Replace LaTeX expressions with image placeholders"""
    latex_blocks = extract_latex_blocks(text)
    
    for i, block in enumerate(latex_blocks):
        # Clean up the block
        clean = block.replace('\\(', '').replace('\\)', '').replace('\\[', '').replace('\\]', '')
        # Generate image
        img_path = f"eq_{i}.png"
        generate_equation_image(clean, img_path)
        # Replace with image tag (will be sent separately)
        text = text.replace(block, f"[IMAGE_{i}]")
    
    return text, latex_blocks

async def post_daily_quiz():
    try:
        logger.info("Generating quiz with DeepSeek...")
        
        prompt = """
        Create 5 math quiz questions for high school students.
        Topics: algebra, geometry, and calculus.
        
        FORMATTING RULES:
        1. Use LaTeX for ALL equations with these delimiters:
           - Use \\( and \\) for inline equations
           - Use \\[ and \\] for displayed equations
        2. Each question MUST be formatted like this:

        Q1: [Question text with \\(equations\\)]
        A) \\(Option A\\)
        B) \\(Option B\\)
        C) \\(Option C\\)
        D) \\(Option D\\)
        Answer: [Letter]
        Explanation: [Brief explanation with \\(equations\\)]

        Q2: ...
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
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API Error: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        raw_quiz = data['choices'][0]['message']['content']
        
        # Extract LaTeX blocks and generate images
        processed_text, latex_blocks = replace_with_images(raw_quiz)
        
        today = datetime.now().strftime("%B %d, %Y")
        message = f"📚 **Daily Math Quiz - {today}**\n\n"
        message += processed_text
        message += "\n\n---\n"
        message += "🔗 **MatheMachine.site** - [mathemachine.site](https://mathemachine.site)"
        
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Send the text
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode='Markdown'
        )
        
        # Send each equation as an image
        for i, latex in enumerate(latex_blocks):
            clean = latex.replace('\\(', '').replace('\\)', '').replace('\\[', '').replace('\\]', '')
            img_path = f"eq_{i}.png"
            if generate_equation_image(clean, img_path):
                with open(img_path, 'rb') as img:
                    await bot.send_photo(
                        chat_id=CHANNEL_ID,
                        photo=img,
                        caption=f"Equation {i+1}"
                    )
                os.remove(img_path)
        
        logger.info(f"✅ Quiz posted with images!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Running Daily Quiz...")
    asyncio.run(post_daily_quiz())
    logger.info("🏁 Job finished.")