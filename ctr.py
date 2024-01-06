import requests
import json
import os
import random
import string
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Video Downloader Bot! Send me a URL to download and share with you.")

def handle_text(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    url = update.message.text

    # Process the URL and send the downloaded file
    send_downloaded_file(user_id, url)

def extract_dlink_and_name_data(response):
    try:
        # Parse the response JSON
        data = response.json()

        # Check if "api" key exists in the JSON data
        if 'api' in data:
            api_data = data['api']

            # Check if "dlink" and "name" keys exist in the "api" data
            if 'dlink' in api_data and 'name' in api_data:
                return api_data['dlink'], api_data['name']
            else:
                print("No 'dlink' or 'name' key found in the 'api' data.")
        else:
            print("No 'api' key found in the JSON data.")
    except json.JSONDecodeError:
        print("Error decoding JSON response.")

    return None, None

def download_and_save_file(dlink, name):
    # Generate a random file name with the provided "name" and a .mp4 extension
    file_name = f"{name}.mp4"

    # Make the request to download the file
    response = requests.get(dlink, stream=True)

    # Check if the download was successful (status code 200)
    if response.status_code == 200:
        # Get the total file size from the Content-Length header
        total_size = int(response.headers.get('Content-Length', 0))

        # Initialize variables for progress tracking
        downloaded_size = 0
        chunk_size = 1024  # You can adjust the chunk size if needed

        # Save the downloaded file
        with open(file_name, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                downloaded_size += len(data)

        return file_name
    else:
        print("Error: Unable to download file. Status Code:", response.status_code)
        return None

def send_downloaded_file(user_id, url):
    # Combine the base URL and additional path
    full_url = f'https://tera.instavideosave.com/?url={url}'

    # Set the headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://tera.instavideosave.com/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # Make the HTTP request
    response = requests.get(full_url, headers=headers)

    # Check if the response is successful (status code 200)
    if response.status_code == 200:
        # Extract "dlink" and "name" data from the response
        dlink_data, name_data = extract_dlink_and_name_data(response)

        if dlink_data and name_data:
            # Download the file using the extracted "dlink" and save with the "name"
            file_name = download_and_save_file(dlink_data, name_data)

            if file_name:
                # Send the downloaded file to the user
                context.bot.send_document(chat_id=user_id, document=open(file_name, 'rb'))
                os.remove(file_name)  # Remove the downloaded file after sending
            else:
                context.bot.send_message(chat_id=user_id, text="Error downloading the file.")
        else:
            context.bot.send_message(chat_id=user_id, text="No 'dlink' or 'name' information found in the response.")
    else:
        context.bot.send_message(chat_id=user_id, text=f"Error: Unable to fetch data. Status Code: {response.status_code}")

def main():
    # Set your Telegram Bot token here
    token = 'YOUR_TELEGRAM_BOT_TOKEN'

    updater = Updater(token, use_context=True)

    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
