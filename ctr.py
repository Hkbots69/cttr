import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = '5273348413:AAEyht3Ntsydj70_ZImfwCjGh2WLSTUWNEU'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Send me a Terabox link, and I'll process it for you.")

def handle_link(update: Update, context: CallbackContext) -> None:
    link = update.message.text

    try:
        # Use headless browser (selenium) to bypass Cloudflare protection
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)

        # Open the URL in the headless browser
        driver.get(f'https://tera.instavideosave.com/?url={link}')

        # Wait for the page to load (adjust the sleep duration if needed)
        time.sleep(5)

        # Get the page source after waiting
        page_source = driver.page_source

        # Close the browser
        driver.quit()

        # Parse the page source as JSON
        video_info = json.loads(page_source)

        # Get the download link from the response
        download_link = video_info['api']['dlink']

        # Send the download link to the user
        update.message.reply_text(f"Download link: {download_link}")

        # Upload the video file to the user
        video_file_url = video_info['video'][0]['video']
        context.bot.send_video(update.message.chat_id, video_file_url, caption="Here is your video!")

    except Exception as e:
        # Print exception details for debugging
        print(f"Error processing the link. Exception: {e}")
        update.message.reply_text("Error processing the link. Please try again.")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
