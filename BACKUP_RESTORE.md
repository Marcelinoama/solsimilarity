# 💾 Sistema de Backup e Restore - Bot de Similaridade v3.10

## 🎯 Funcionalidades Implementadas

O sistema agora possui funcionalidades completas de **backup e restore** do banco de dados SQLite, permitindo proteção, migração e versionamento dos dados.

## 🔧 Comandos Implementados

### 💾 **Comando /backup**

**Sintaxe:**
```
/backup
```

**Funcionalidade:**
- Cria backup completo do banco de dados SQLite atual
- Adiciona timestamp automático no nome do arquivo
- Envia arquivo como documento via Telegram
- Remove arquivo temporário após envio
- Exibe informações detalhadas sobre o backup

**Exemplo de Uso:**
```
Usuário: /backup

Bot: 
💾 BACKUP DO BANCO DE DADOS

📊 Tokens: 47
📁 Tamanho: 90112 bytes  
🕒 Criado em: 16/01/2025 14:30:25

✅ Backup criado com sucesso!
💡 Use /restore para restaurar este backup.

[Arquivo anexado: backup_database_20250116_143025.db]
```

**Características:**
- ✅ Verificação de existência do banco antes do backup
- ✅ Nome do arquivo com timestamp: `backup_database_YYYYMMDD_HHMMSS.db`
- ✅ Informações completas sobre o backup (tokens, tamanho)
- ✅ Limpeza automática de arquivos temporários
- ✅ Logs detalhados para debugging

### 🔄 **Comando /restore**

**Sintaxe:**
```
/restore (enviar junto com arquivo .db anexado)
```

**Funcionalidade:**
- Restaura banco de dados a partir de arquivo de backup
- Validação completa do arquivo de backup antes da restauração
- Backup automático do banco atual antes de restaurar
- Substituição segura do banco de dados
- Informações detalhadas sobre a operação

**Como Usar:**
1. Envie o comando `/restore` junto com um arquivo `.db` anexado
2. O sistema validará o arquivo automaticamente
3. Backup do banco atual será criado automaticamente
4. O banco será substituído pelo backup fornecido
5. Confirmação com estatísticas será exibida

**Exemplo de Uso:**
```
Usuário: /restore + [arquivo backup_database_20250116_143025.db]

Bot:
✅ BANCO RESTAURADO COM SUCESSO!

📊 Dados anteriores:
   • Tokens: 47
   • Tamanho: 90112 bytes

📊 Dados restaurados:  
   • Tokens: 35
   • Tamanho: 75648 bytes

💾 Backup automático do banco anterior foi criado
🔄 O bot agora está usando os dados restaurados.
```

**Validações de Segurança:**
- ✅ Verificação de extensão `.db`
- ✅ Limite máximo de 20MB para o arquivo
- ✅ Validação de estrutura SQLite
- ✅ Verificação de tabelas necessárias (tokens, settings, displayed_contracts)
- ✅ Contagem de tokens no backup
- ✅ Backup automático antes da restauração

## 🛡️ Funcionalidades de Segurança

### **Validação de Backup**
```python
def validate_backup_file(self, backup_path):
    # Verifica existência do arquivo
    # Testa conexão SQLite
    # Valida tabelas necessárias
    # Conta tokens no backup
    # Retorna: (True/False, mensagem_detalhada)
```

### **Backup Automático**
- Sempre cria backup do banco atual antes de restaurar
- Nome: `backup_before_restore_YYYYMMDD_HHMMSS.db`
- Permite rollback em caso de problemas

### **Tratamento de Erros**
- Validação completa de arquivos
- Mensagens de erro detalhadas
- Limpeza automática de arquivos temporários
- Logs para debugging

## 📊 Informações Técnicas

### **Estrutura do Banco Validada**
- Tabela `tokens` - Dados principais dos tokens
- Tabela `settings` - Configurações do bot
- Tabela `displayed_contracts` - Contratos já exibidos

### **Limites e Restrições**
- **Tamanho máximo:** 20MB por arquivo
- **Extensão:** Apenas arquivos `.db`
- **Validação:** Estrutura SQLite obrigatória
- **Backup automático:** Sempre criado antes de restore

### **Performance**
- Backup via `shutil.copy2()` - Preserva metadados
- Validação rápida via consulta SQL
- Limpeza automática de arquivos temporários
- Logs otimizados para debugging

## 🎯 Casos de Uso

### **1. Backup Preventivo**
```
Situação: Antes de operações críticas
Comando: /backup
Resultado: Arquivo de backup seguro
```

### **2. Migração de Dados**
```
Situação: Mudança de servidor
Processo: /backup no servidor antigo → /restore no novo
Resultado: Dados migrados com segurança
```

### **3. Versionamento**
```
Situação: Diferentes estados do banco
Processo: Múltiplos backups com timestamps
Resultado: Histórico de versões disponível
```

### **4. Rollback de Emergência**
```
Situação: Problema após alterações
Processo: /restore com backup anterior
Resultado: Estado anterior restaurado
```

### **5. Clonagem de Configurações**
```
Situação: Replicar setup em outro bot
Processo: Backup → Restore em nova instância
Resultado: Configuração idêntica
```

## 🔧 Implementação Técnica

### **Arquivo: database.py**
```python
def create_backup(self, backup_path=None)
def validate_backup_file(self, backup_path)
def restore_from_backup(self, backup_path, create_current_backup=True)
def get_database_info(self)
```

### **Arquivo: bot.py**
```python
async def backup_command(self, update, context)
async def restore_command(self, update, context)
```

### **Handlers Registrados**
```python
application.add_handler(CommandHandler("backup", bot.backup_command))
application.add_handler(CommandHandler("restore", bot.restore_command))
```

## ✅ Status da Implementação

- ✅ **Comando /backup** - Totalmente implementado e testado
- ✅ **Comando /restore** - Totalmente implementado e testado
- ✅ **Validação de segurança** - Implementada e testada
- ✅ **Backup automático** - Implementado
- ✅ **Documentação** - Completa
- ✅ **Logs detalhados** - Implementados
- ✅ **Tratamento de erros** - Implementado

## 🚀 Próximas Melhorias

### **Planejadas**
- [ ] Backup automático programado (diário/semanal)
- [ ] Compressão de arquivos grandes
- [ ] Backup para cloud storage (Google Drive, etc.)
- [ ] Interface web para gerenciamento de backups

### **Sugeridas**
- [ ] Criptografia de backups
- [ ] Backup incremental
- [ ] Histórico de backups com limpeza automática
- [ ] Notificações de backup bem-sucedido

---

## ✅ Sistema de Backup e Restore Implementado com Sucesso!

**O bot agora possui proteção completa de dados com funcionalidades profissionais de backup e restore, garantindo segurança e facilidade de migração dos dados.** 