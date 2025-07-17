#!/usr/bin/env python3
"""
Utilitário para obter IDs dos grupos do Telegram
"""

import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import Config

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GroupIDBot:
    def __init__(self):
        self.found_groups = set()
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Captura IDs dos grupos"""
        if update.message and update.message.chat:
            chat = update.message.chat
            chat_id = chat.id
            chat_title = chat.title or "Chat Privado"
            chat_type = chat.type
            
            if chat_type in ['group', 'supergroup']:
                if chat_id not in self.found_groups:
                    self.found_groups.add(chat_id)
                    print(f"\n📊 GRUPO ENCONTRADO:")
                    print(f"   Nome: {chat_title}")
                    print(f"   ID: {chat_id}")
                    print(f"   Tipo: {chat_type}")
                    print(f"   Use este ID no arquivo .env")
                    
                    # Responde no grupo
                    await update.message.reply_text(
                        f"✅ ID deste grupo: `{chat_id}`\n"
                        f"Nome: {chat_title}\n"
                        f"Copie o ID para seu arquivo .env",
                        parse_mode='Markdown'
                    )

def main():
    """Função principal"""
    print("🆔 Utilitário para Obter IDs dos Grupos")
    print("="*40)
    
    if not Config.BOT_TOKEN:
        print("❌ BOT_TOKEN não configurado!")
        print("Configure o token no arquivo .env primeiro.")
        return
    
    print("📋 INSTRUÇÕES:")
    print("1. Adicione o bot aos grupos desejados")
    print("2. Envie uma mensagem em cada grupo")
    print("3. O bot mostrará o ID do grupo")
    print("4. Copie os IDs para o arquivo .env")
    print("5. Pressione Ctrl+C para parar\n")
    
    # Cria a aplicação do bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Cria instância do bot
    bot = GroupIDBot()
    
    # Adiciona handler para todas as mensagens
    application.add_handler(MessageHandler(
        filters.ALL, 
        bot.handle_message
    ))
    
    print("🤖 Bot iniciado! Envie mensagens nos grupos...")
    print("Pressione Ctrl+C para parar.\n")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        print("\n\n✅ Bot parado!")
        if bot.found_groups:
            print(f"📊 Total de grupos encontrados: {len(bot.found_groups)}")
            print("\nIDs encontrados:")
            for group_id in bot.found_groups:
                print(f"  {group_id}")
        else:
            print("ℹ️ Nenhum grupo foi encontrado.")
        print("\nAtualize seu arquivo .env com os IDs corretos.")

if __name__ == '__main__':
    main() 