import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from paddleocr import PaddleOCR
import aiofiles
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Initialize bot and dispatcher
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the .env file.")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Create a directory for saving images
SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)

# Handle the /start command
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Welcome! Send me an image to extract text.")
    print("Bot responded to /start")

# Handle image messages sent as photos
@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    print("Photo received.")
    await message.answer("Processing your photo...")

    # Get the highest resolution photo
    try:
        photo = message.photo[-1]  # Get the highest resolution photo
        file = await bot.get_file(photo.file_id)
        downloaded_file = await bot.download(file.file_path)
        print("Photo downloaded successfully.")
    except Exception as e:
        print(f"Failed to download photo: {e}")
        await message.answer("Failed to download the photo.")
        return

    # Save the photo locally
    image_path = f"{SAVE_DIR}/{photo.file_unique_id}.png"
    async with aiofiles.open(image_path, 'wb') as f:
        await f.write(downloaded_file)
    print(f"Photo saved at: {image_path}")
    await message.answer(f"Photo saved at {image_path}. Now processing...")

    # Process with OCR
    try:
        result = ocr.ocr(image_path)
        if not result or not result[0]:
            await message.answer("No text found in the image.")
            return
        extracted_text = '\n'.join([line[1][0] for line in result[0]])
        await message.answer(f"Extracted text:\n{extracted_text}")
    except Exception as e:
        print(f"Error during OCR: {e}")
        await message.answer("An error occurred during text extraction.")

# Main entry point to start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
