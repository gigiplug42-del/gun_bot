from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from urllib.parse import quote
from catalog import PISTOLS, RIFLES, SHOTGUNS
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env file


TOKEN = os.environ["TELEGRAM_TOKEN"]

CATALOG = {
    "Pistols": PISTOLS,
    "Rifles": RIFLES,
    "Shotguns": SHOTGUNS,
}


# --------------------------------------------------
# SMART EDIT (handles text vs media automatically)
# --------------------------------------------------
async def smart_edit(query, text, keyboard):
    message = query.message

    if message.text:
        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# --------------------------------------------------
# START
# --------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f"cat|{cat}")]
        for cat in CATALOG
    ]

    text = (
        "*Welcome to Slingard Gun cate!*\n\n"
        "Browse our premium selection of pistols, rifles, and shotguns.\n"
        "We provide professional, safe, and accurate product information.\n\n"
        "Use the buttons below to explore our catalog.\n\n"
        "📞 *Business WhatsApp:*\n"
        "+1 (470) 360-2782"
    )

    gif = "media/slingard.gif"

    if from_callback:
        await smart_edit(update.callback_query, text, keyboard)
    else:
        with open(gif, "rb") as f:
            await update.message.reply_animation(
                animation=f,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )


# --------------------------------------------------
# CATEGORY
# --------------------------------------------------
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, category = query.data.split("|")
    context.user_data["category"] = category

    keyboard = [
        [InlineKeyboardButton(sub, callback_data=f"sub|{sub}")]
        for sub in CATALOG[category]
    ]
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back_main")])

    await smart_edit(
        query,
        f"*{category}*\nChoose a type:",
        keyboard
    )


# --------------------------------------------------
# SUBCATEGORY
# --------------------------------------------------
async def subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, subcategory = query.data.split("|")
    category = context.user_data.get("category")

    context.user_data["subcategory"] = subcategory
    guns = CATALOG[category][subcategory]

    keyboard = [
        [InlineKeyboardButton(gun["name"], callback_data=f"gun|{gun['name']}")]
        for gun in guns
    ]
    keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back_category")])

    await smart_edit(
        query,
        f"*{category} → {subcategory}*\nSelect a firearm:",
        keyboard
    )


# --------------------------------------------------
# GUN DETAILS
# --------------------------------------------------
async def gun_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, gun_name = query.data.split("|")
    category = context.user_data.get("category")
    subcategory = context.user_data.get("subcategory")

    gun = next(g for g in CATALOG[category][subcategory] if g["name"] == gun_name)

    text = (
        f"🔫 *{gun['name']}*\n\n"
        f"• Caliber: {gun['caliber']}\n"
        f"• Manufacturer: {gun['manufacturer']}\n"
        f"• Price: {gun['price']}"
    )


    # ✅ SMART IMAGE LINK LOGIC
    image_url = gun.get("image")
    if not image_url:
        image_url = f"https://www.google.com/search?tbm=isch&q={gun['name'].replace(' ', '+')}"

    whatsapp_number = "14703602782"  # no + sign

    message = (
        "Hello, I would like to request a purchase.\n\n"
        f"Gun: {gun['name']}\n"
        f"Category: {category}\n"
        f"Type: {subcategory}\n"
        f"Price: {gun['price']}"
    )

    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={quote(message)}"

    keyboard = [
        [InlineKeyboardButton("🖼 View Image", url=image_url)],
        [InlineKeyboardButton("🛒 Request Purchase", url=whatsapp_link)],
        [InlineKeyboardButton("⬅ Back", callback_data="back_sub")]
    ]

    await smart_edit(query, text, keyboard)


# --------------------------------------------------
# BACK HANDLER
# --------------------------------------------------
async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "back_main":
        await start(update, context, from_callback=True)

    elif data == "back_category":
        category = context.user_data.get("category")

        keyboard = [
            [InlineKeyboardButton(sub, callback_data=f"sub|{sub}")]
            for sub in CATALOG[category]
        ]
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back_main")])

        await smart_edit(
            query,
            f"*{category}*\nChoose a type:",
            keyboard
        )

    elif data == "back_sub":
        category = context.user_data.get("category")
        subcategory = context.user_data.get("subcategory")

        guns = CATALOG[category][subcategory]

        keyboard = [
            [InlineKeyboardButton(gun["name"], callback_data=f"gun|{gun['name']}")]
            for gun in guns
        ]
        keyboard.append([InlineKeyboardButton("⬅ Back", callback_data="back_category")])

        await smart_edit(
            query,
            f"*{category} → {subcategory}*\nSelect a firearm:",
            keyboard
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(category_handler, pattern="^cat\\|"))
    app.add_handler(CallbackQueryHandler(subcategory_handler, pattern="^sub\\|"))
    app.add_handler(CallbackQueryHandler(gun_handler, pattern="^gun\\|"))
    app.add_handler(CallbackQueryHandler(back_handler, pattern="^back_"))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
