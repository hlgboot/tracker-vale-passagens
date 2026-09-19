import logging
from dotenv import load_dotenv
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

load_dotenv()

from monitor import createTracking, getTrackingsByUser, loadTrackings, removeUser, deleteTracking
from locais import getLocationById, loadLocations
from vale import check, genPayload

TOKEN = os.getenv("TOKEN")
INTERVALO = 5 * 60

ORIGEM, DESTINO, DATA = range(3)

locais = loadLocations()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# --- ROTINA DE MONITORAMENTO ---
async def monitor_job(context: ContextTypes.DEFAULT_TYPE):
    monitoramentos = loadTrackings()
    if not monitoramentos:
        return

    logging.info(f"Executando verificação para {len(monitoramentos)} rota(s)...")

    for monitor in monitoramentos:
        payload = genPayload(monitor)
        passagens = check(payload)

        if passagens:
            for p in passagens:
                msg = (
                    f"🚨 **PASSAGEM ENCONTRADA!**\n\n"
                    f"**Trem:** {p.get('descricaoOrigem')} → {p.get('descricaoDestino')}\n"
                    f"**Data:** {monitor['data']}\n"
                    f"**Hora de Partida:** {p.get('horaPartidaProgramada')}\n"
                    f"**Valor:** R$ {p.get('valorTotal')}\n"
                    f"Acesse o site da Vale para comprar!"
                )

                callback_data = (
                f"reativar:"
                f"{monitor['origem']}:"
                f"{monitor['destino']}:"
                f"{monitor['data']}"
                )

                keyboard = [[
                    InlineKeyboardButton(
                        "🔄 Reativar busca",
                        callback_data=callback_data
                    )
                ]]

                for user_id in monitor.get("users", []):
                    try:
                        await context.bot.send_message(
                            chat_id=user_id, text=msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                    except Exception as e:
                        logging.error(f"Falha ao enviar mensagem para {user_id}: {e}")

            deleteTracking(monitor["id"])

# --- COMANDOS DO BOT ---

## /start
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Bot Vale Passagens*\n\n"
        "/monitorar - Cadastre uma nova viagem\n"
        "/alertas - Liste e gerencie seus alertas ativos\n"
        "/cancelar - Cancele o formulário atual",
        parse_mode="Markdown",
    )


## /monitorar
async def monitorar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = "*Informe o código da estação de Origem (ex: 7185):*\n\n"

    for local in locais :
        texto += (f"`{local['id']}` → {local['nome']}\n")

    await update.message.reply_text(texto, parse_mode="Markdown",)
    return ORIGEM


async def receber_origem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["origem"] = update.message.text.strip()

    texto = "*Informe o código da estação de Destino (ex: 7165):*\n\n"
    
    for local in locais :
        texto += (f"`{local['id']}` → {local['nome']}\n")

    await update.message.reply_text(texto, parse_mode="Markdown",)
    return DESTINO


async def receber_destino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["destino"] = update.message.text.strip()
    await update.message.reply_text("Informe a data no formato *DD/MM/AAAA:*", parse_mode="Markdown")
    return DATA


async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data_str = update.message.text.strip()
    user_id = update.effective_chat.id

    try:
        origem = int(context.user_data["origem"])
        destino = int(context.user_data["destino"])
    except ValueError:
        await update.message.reply_text("Códigos de estação inválidos. Tente /monitorar novamente.")
        return ConversationHandler.END

    monitor = createTracking(origem, destino, data_str, user_id)

    await update.message.reply_text(
        f"✅ *Monitoramento ativo!*\n\n"
        f"• Origem: `{getLocationById(origem)['nome']}`\n"
        f"• Destino: `{getLocationById(destino)['nome']}`\n"
        f"• Data: `{data_str}`\n\n"
        f"Você receberá um alerta assim que vagas forem liberadas.",
        parse_mode="Markdown",
    )

    return ConversationHandler.END


## /alertas
async def cmd_alertas(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_chat.id

    alertas = getTrackingsByUser(user_id)

    if not alertas:

        await update.message.reply_text(
            "📭 Você não possui alertas ativos."
        )

        return

    await update.message.reply_text("📋 *Seus alertas ativos:*\n\n", parse_mode="Markdown",)

    for monitor in alertas:

        origem = getLocationById(monitor["origem"])["nome"]

        destino = getLocationById(monitor["destino"])["nome"]

        texto = (
            f"• *ID:* `{monitor['id']}`\n\n"
            f"• {origem} → {destino}\n"
            f"• Data: {monitor['data']}\n\n"
        )

        keyboard = [[
            InlineKeyboardButton(
                "Remover",
                callback_data=f"delete:{monitor['id']}"
            )
        ]]

        await update.message.reply_text(
            texto,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


## /excluir:id
async def cmd_excluir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_chat.id

    query = update.callback_query

    await query.answer()

    _, monitor_id = query.data.split(":", 1)

    if removeUser(monitor_id, user_id):
        await query.edit_message_text(f"Monitoramento `{monitor_id}` cancelado.", parse_mode="Markdown")

    else:
        await query.edit_message_text("ID não encontrado entre os seus alertas.")


## /reativar:origem:destino:data
async def cmd_reativar(update, context):

    query = update.callback_query
    await query.answer()

    _, origem, destino, data = query.data.split(":")

    user_id = update.effective_user.id

    monitor = createTracking(
        int(origem),
        int(destino),
        data,
        user_id
    )

    await query.edit_message_reply_markup(
        reply_markup=None
    )

    await query.message.reply_text(
        "Busca reativada!"
    )


## /cancelar
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operação cancelada.")
    return ConversationHandler.END



# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("monitorar", monitorar)],
        states={
            ORIGEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_origem)],
            DESTINO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_destino)],
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv_handler)

    app.add_handler(CallbackQueryHandler(cmd_excluir, pattern="^delete"))
    app.add_handler(CallbackQueryHandler(cmd_reativar, pattern="^reativar"))

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("alertas", cmd_alertas))


    # Inicia a tarefa de polling no background a cada 5 minutos
    app.job_queue.run_repeating(monitor_job, interval=INTERVALO, first=10)

    app.run_polling()


if __name__ == "__main__":
    main()