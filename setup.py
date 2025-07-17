#!/usr/bin/env python3
"""
Script de setup automático para o Bot de Similaridade de Tokens
"""

import os
import subprocess
import sys

def install_requirements():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependências instaladas com sucesso!")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências. Instale manualmente:")
        print("pip install -r requirements.txt")
        return False
    return True

def create_env_file():
    """Cria arquivo .env se não existir"""
    if not os.path.exists('.env'):
        print("📝 Criando arquivo .env...")
        with open('.env', 'w') as f:
            f.write("# Token do bot do Telegram (obtenha com @BotFather)\n")
            f.write("BOT_TOKEN=seu_token_do_bot_aqui\n\n")
            f.write("# ID do grupo que servirá como banco de dados\n")
            f.write("DATABASE_GROUP_ID=-1001234567890\n\n")
            f.write("# ID do grupo onde chegam as mensagens para comparação\n")
            f.write("COMPARISON_GROUP_ID=-1001234567891\n\n")
            f.write("# ID do grupo onde são enviadas as notificações de similaridade\n")
            f.write("NOTIFICATION_GROUP_ID=-1001234567892\n")
        print("✅ Arquivo .env criado! Edite com suas configurações.")
    else:
        print("ℹ️ Arquivo .env já existe.")

def print_next_steps():
    """Mostra próximos passos"""
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Configure o arquivo .env com:")
    print("   - Token do bot (obtenha com @BotFather)")
    print("   - IDs dos grupos do Telegram")
    print("\n2. Para obter IDs dos grupos:")
    print("   python get_group_ids.py")
    print("\n3. Para executar o bot:")
    print("   python run.py")
    print("\n📖 Consulte o README.md para mais detalhes!")

def main():
    """Função principal de setup"""
    print("🤖 Setup do Bot de Similaridade de Tokens")
    print("="*50)
    
    success = install_requirements()
    if not success:
        return
    
    create_env_file()
    print_next_steps()

if __name__ == '__main__':
    main() 