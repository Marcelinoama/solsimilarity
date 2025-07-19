import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Token do bot do Telegram
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # IDs dos grupos
    DATABASE_GROUP_ID = os.getenv('DATABASE_GROUP_ID')  # Grupo que serve como banco de dados
    COMPARISON_GROUP_ID = os.getenv('COMPARISON_GROUP_ID')  # Grupo onde chegam as mensagens para comparar
    NOTIFICATION_GROUP_ID = os.getenv('NOTIFICATION_GROUP_ID')  # Grupo onde são enviadas apenas as notificações de similaridade
    
    # Configurações de similaridade
    MIN_SIMILARITY_THRESHOLD = 70  # Porcentagem mínima para considerar similar
    
    # Configurações do banco de dados
    DATABASE_FILE = 'token_database.db' 
    
    # Configurações da IA para análise de links
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    AI_LINKS_ENABLED = True  # Estado padrão da análise de IA 