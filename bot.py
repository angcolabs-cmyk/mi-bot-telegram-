import logging
import os
import sqlite3
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DB_PATH = "points.db"
AD_REWARD = 10
AD_COOLDOWN = 30  # segundos entre anuncios (evita spam de puntos)


# ---------- Base de datos (persistente) ----------
def db_init():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, last_ad REAL DEFAULT 0)"
        )


def get_user(user_id: int):
    with sqlite3.connect(DB_PATH) as db:
        db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        return db.execute(
            "SELECT points, last_ad FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()


def add_points(user_id: int, amount: int):
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            "UPDATE users SET points = points + ?, last_ad = ? WHERE user_id = ?",
            (amount, time.time(), user_id),
        )


# ---------- Teclados ----------
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📺 Ver Anuncio (+{AD_REWARD} Pts)", callback_data="watch_ad")],
        [InlineKeyboardButton("💰 Ver mi Saldo", callback_data="check_balance")],
    ])


async def safe_edit(query, text, markup):
    """Evita el error 'Message is not modified' al pulsar el mismo botón."""
    try:
        await query.edit_message_text(text=text, reply_markup=markup)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_user(update.effective_user.id)
    await update.message.reply_text(
        f"¡Hola {update.effective_user.first_name}! Bienvenid@ a la plataforma de recompensas.\n\n"
        "Gana puntos viendo anuncios y completando misiones.",
        reply_markup=main_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    points, last_ad = get_user(user_id)

    if query.data == "watch_ad":
        wait = AD_COOLDOWN - (time.time() - last_ad)
        if wait > 0:
            await query.answer(f"⏳ Espera {int(wait) + 1}s para el siguiente anuncio.", show_alert=True)
            return
        await query.answer()
        add_points(user_id, AD_REWARD)
        points += AD_REWARD
        await safe_edit(
            query,
            f"✅ ¡Has visto el anuncio! Ganaste {AD_REWARD} puntos.\nSaldo actual: {points} pts.",
            main_keyboard(),
        )

    elif query.data == "check_balance":
        await query.answer()
        await safe_edit(query, f"📊 Tu saldo actual es de: {points} puntos.", main_keyboard())

    else:
        await query.answer()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error no controlado:", exc_info=context.error)


if __name__ == "__main__":
    # Pega aquí tu token nuevo de BotFather
    token = "9201469857:AAHfG8mHxv1r0pFhEK8wzEpL7RPVK1XSm18"

    db_init()
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    print("Bot en ejecución...")
    app.run_polling()
