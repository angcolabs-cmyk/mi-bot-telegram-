import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Configuración del registro de actividad
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Diccionario provisional para guardar los puntos de los usuarios
user_points = {}

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_points:
        user_points[user_id] = 0

    keyboard = [
        [InlineKeyboardButton("📺 Ver Anuncio (+10 Pts)", callback_data='watch_ad')],
        [InlineKeyboardButton("💰 Ver mi Saldo", callback_data='check_balance')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"¡Hola {update.effective_user.first_name}! Bienvenid@ a la plataforma de recompensas.\n\n"
        "Gana puntos viendo anuncios y completando misiones.",
        reply_markup=reply_markup
    )

# Manejo de botones de la interfaz
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_points:
        user_points[user_id] = 0

    if query.data == 'watch_ad':
        user_points[user_id] += 10
        await query.edit_message_text(
            text=f"✅ ¡Has visto el anuncio! Ganaste 10 puntos.\nSaldo actual: {user_points[user_id]} pts.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Ver otro Anuncio", callback_data='watch_ad')],
                [InlineKeyboardButton("💰 Ver mi Saldo", callback_data='check_balance')]
            ])
        )
    elif query.data == 'check_balance':
        await query.edit_message_text(
            text=f"📊 Tu saldo actual es de: {user_points[user_id]} puntos.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📺 Ver Anuncio (+10 Pts)", callback_data='watch_ad')]
            ])
        )

if __name__ == '__main__':
    # Tu token oficial obtenido de BotFather[span_1](start_span)[span_1](end_span)
    TOKEN = '919826761:AAEtasCHPDu7RXkW67sT6gaUUSy-ycy-dGE'
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot en ejecución...")
    app.run_polling()
