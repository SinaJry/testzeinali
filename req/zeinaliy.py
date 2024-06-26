import requests
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes, JobQueue,Updater
import nest_asyncio
import asyncio
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests




 # Replace with your channel username or ID

# Example job categories and their corresponding keywords for API query
# JOB_CATEGORIES = {
#     'Back-End': 'Back-End',
#     'Front-End': 'Front-End',
#     'Full-Stack': 'Full-Stack',
#     # Add more categories as needed
# }

CATEGORIES = {
    #"Job Search": None,  # This category won't have subcategories
    "Technology": {
        "Back-End": "Back-End",
        "Front-End": "Front-End",
        "Sports": "sports_news",
    },
    # ... (add more categories and subcategories)
}



headers = {
    'User-Agent': 'Your User Agent',
    # Add any necessary headers
}




async def crawl_website(keyword):
    """Function to crawl website and fetch data via API call."""
    url = 'https://candidateapi.jobvision.ir/api/v1/JobPost/List'
    json_data = {
        'pageSize': 5,  # Adjust as needed
        'requestedPage': 1,
        'keyword': keyword,
        'sortBy': 1,
        'searchId': None,
    }

    try:
        response = requests.post(url, headers=headers, json=json_data)

        jposts = response.json()['data']['jobPosts']

        return jposts
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []




# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Start command handler."""
#     keyboard = [
#         [InlineKeyboardButton(category, callback_data=keyword)]
#         for category, keyword in JOB_CATEGORIES.items()
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text('Please choose a job category:', reply_markup=reply_markup)

async def start(update: Updater, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Start command handler."""
  keyboard = []
  for category, subcategories in CATEGORIES.items():
    button_data = category  # Use category name as callback data for now
    button = InlineKeyboardButton(category, callback_data=button_data)
    keyboard.append([button])  # Create single-button rows
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text('Choose a category:', reply_markup=reply_markup)





# async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Callback function to handle button clicks."""
#     query = update.callback_query
#     category = query.data
#     job_posts = crawl_website(category)



async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback function to handle button clicks."""
    query = update.callback_query
    data = query.data

    if data in CATEGORIES:  # Category selection
        category = data
        subcategories = CATEGORIES[category]

        keyboard = [[InlineKeyboardButton(subcat, callback_data=f"{category}-{subcat}")]
                    for subcat in subcategories.values()]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(f"Choose a subcategory for {category}:", reply_markup=reply_markup)

    else:  # Subcategory selection
        subcategory = data.split('-',1)[1]

        job_posts = await crawl_website(subcategory)  # Crawl using subcategory only

        if job_posts:
            for post in job_posts:
                message = (
                                f"Company: {post['company']['nameFa']}\n"
                                f"Title: {post['title']}\n"
                                f"Labels: {'-'.join(post['labels'])}\n"
                                f"Gender: {post['gender']['titleFa']}\n"
                                f"First Activation Time: {post['firstActivationTime']['beautifyFa']}\n"
                                f"Days Left Until Expire: {post['expireTime']['daysLeftUntil']}"
                            )
                await context.bot.send_message(chat_id=query.message.chat_id, text=message)
        else:
            await query.answer(text=f"No job posts found for {subcategory}", show_alert=True)



nest_asyncio.apply()

if __name__ == '__main__':
  print('Starting Bot...')
  app = Application.builder().token(TOKEN).build()

  #Commands
  app.add_handler(CommandHandler("start",start))
  #app.add_handler(CommandHandler("shutdown", shutdown))

  # Schedule the job to run every 1 minute
  #app.job_queue.run_repeating(send_custom_message, interval=60)
  # Callback query handler for button clicks
  app.add_handler(CallbackQueryHandler(button_callback))
  print('Polling...')


  # Use asyncio to run the application
  loop = asyncio.get_event_loop()
  loop.run_until_complete(app.initialize())
  app.run_polling(poll_interval = 3)


