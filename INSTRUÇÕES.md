# 🚀 Instruções Rápidas - Bot de Similaridade

## 🛠️ 1. Instalação Automática

```bash
python setup.py
```

Este comando irá:
- ✅ Instalar todas as dependências
- ✅ Criar arquivo `.env` 
- ✅ Mostrar próximos passos

## ⚙️ 2. Configuração

### 2.1 Criar Bot no Telegram
1. Abra o Telegram e converse com **@BotFather**
2. Digite `/newbot`
3. Escolha um nome para seu bot (ex: "Meu Bot Similaridade") 
4. Escolha um username (ex: "meu_bot_similaridade_bot")
5. **COPIE O TOKEN** fornecido

### 2.2 Configurar Token
Edite o arquivo `.env`:
```
BOT_TOKEN=1234567890:ABCdefghijklmnopqrstuvwxyz123456789
DATABASE_GROUP_ID=-1001234567890
COMPARISON_GROUP_ID=-1001234567891
```

### 2.3 Obter IDs dos Grupos
```bash
python get_group_ids.py
```

1. Crie dois grupos no Telegram
2. Adicione o bot aos grupos
3. Execute o comando acima
4. Envie uma mensagem em cada grupo
5. Copie os IDs mostrados para o arquivo `.env`

## 🚀 3. Execução

```bash
python run.py
```

## 📋 4. Como Usar

### 4.1 Grupo de Banco de Dados
- Envie mensagens com informações de tokens
- O bot salvará automaticamente no banco
- Use o formato mostrado no exemplo do README

### 4.2 Grupo de Comparação  
- Envie mensagens no mesmo formato
- O bot comparará com o banco de dados
- Receberá relatório de similaridade

### 4.3 Exemplo de Resposta
```
🔍 Análise de Similaridade

🎯 Token analisado: everything is grok

📊 2 token(s) similar(es) encontrado(s):

1. Token Similar
├ 📈 Similaridade: 85.2%
├ 👨‍💻 Mesmo criador: ✅
├ 🏭 Mesma plataforma: ✅
└ 📍 Endereço: oRRMQqkrk...t7pump
```

## 🧪 5. Testes

### Testar Parser:
```bash
python test_parser.py
```

### Verificar Configuração:
```bash
python -c "from config import Config; print('✅ Configuração OK!' if Config.BOT_TOKEN else '❌ Configure BOT_TOKEN')"
```

## 🔧 6. Solução de Problemas

### Bot não responde:
- ✅ Verifique se o token está correto
- ✅ Confirme se o bot está nos grupos
- ✅ Verifique IDs dos grupos no `.env`

### Erro de dependências:
```bash
pip install python-telegram-bot python-dotenv fuzzywuzzy python-Levenshtein
```

### Banco de dados corrompido:
```bash
rm token_database.db
# Reinicie o bot para recriar
```

## 📊 7. Personalização

### Alterar limite de similaridade:
Edite `config.py`:
```python
MIN_SIMILARITY_THRESHOLD = 80  # Padrão: 70
```

### Ajustar pesos dos critérios:
Edite `similarity_calculator.py`:
```python
self.weights = {
    'creator_address': 50,  # Padrão: 40

    # ... outros pesos
}
```

## 🔍 8. Monitoramento

### Ver logs em tempo real:
```bash
python run.py | tee bot.log
```

### Ver dados salvos:
```bash
python -c "from database import TokenDatabase; db = TokenDatabase(); tokens = db.get_all_tokens(); print(f'Tokens salvos: {len(tokens)}')"
```

---

## 🆘 Precisa de Ajuda?

1. **Logs**: Verifique as mensagens de erro no terminal
2. **Teste Individual**: Use `python test_parser.py` para verificar se o parsing funciona
3. **IDs dos Grupos**: Use `python get_group_ids.py` para obter IDs corretos
4. **README Completo**: Consulte `README.md` para documentação detalhada

## ✅ Lista de Verificação

- [ ] ✅ Dependências instaladas (`python setup.py`)
- [ ] ✅ Token do bot configurado no `.env`
- [ ] ✅ Bot adicionado aos grupos
- [ ] ✅ IDs dos grupos configurados no `.env`
- [ ] ✅ Bot executando (`python run.py`)
- [ ] ✅ Teste realizado (`python test_parser.py`)

**🎉 Pronto! Seu bot está funcionando!** 