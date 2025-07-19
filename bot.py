from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import os

EXAMS_PATH = 'exams'
TOKEN = os.environ["BOT_TOKEN"]

# Main menu keyboard
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("📘 WIUT Math Entrance Exam Samples")]],
    resize_keyboard=True
)

# Get list of years from folder structure
def get_available_years():
    return sorted([
        folder for folder in os.listdir(EXAMS_PATH)
        if os.path.isdir(os.path.join(EXAMS_PATH, folder))
    ])

# Get list of files for a selected year
def get_files_for_year(year):
    year_path = os.path.join(EXAMS_PATH, year)
    if not os.path.isdir(year_path):
        return []
    return sorted([
        f for f in os.listdir(year_path)
        if os.path.isfile(os.path.join(year_path, f))
    ])

# Start or menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! Tap below to see available exam years:",
        reply_markup=main_menu_keyboard
    )

# Show years
async def show_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    years = get_available_years()
    keyboard = [[KeyboardButton(year)] for year in years]
    keyboard.append([KeyboardButton("⬅️ Main Menu")])
    await update.message.reply_text(
        "Select a year to view available exam files:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Show files inside the year folder
async def show_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year = update.message.text.strip()
    if year not in get_available_years():
        await update.message.reply_text("Invalid year. Please select from the list.")
        return

    context.user_data["selected_year"] = year
    files = get_files_for_year(year)
    if not files:
        await update.message.reply_text(f"No files found for {year}.")
        return

    keyboard = [[KeyboardButton(file)] for file in files]
    keyboard.append([KeyboardButton("⬅️ Back to Years")])
    await update.message.reply_text(
        f"Available files for {year}:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Send the selected file
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filename = update.message.text.strip()
    year = context.user_data.get("selected_year")

    if not year:
        await update.message.reply_text("Please select a year first.")
        return

    file_path = os.path.join(EXAMS_PATH, year, filename)
    if os.path.exists(file_path):
        await update.message.reply_document(document=open(file_path, 'rb'))
    else:
        await update.message.reply_text("File not found. Try again.")

# Navigation commands
async def go_back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def go_back_to_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_years(update, context)

# Main
def main():
    TOKEN = "BOT_TOKEN"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📘 WIUT Math Entrance Exam Samples$"), show_years))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^⬅️ Main Menu$"), go_back_to_main))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^⬅️ Back to Years$"), go_back_to_years))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("r^\d{4}$"), show_files))
    app.add_handler(MessageHandler(filters.TEXT, send_file))  # fallback for filename match

    print("Bot running...")
    app.run_polling()

if __name__ == '__main__':
    main()
