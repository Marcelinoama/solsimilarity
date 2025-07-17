# 🤖 Bot de Similaridade de Tokens - v3.14

Bot avançado de Telegram que realiza análise sofisticada de similaridade entre tokens/criptomoedas. O sistema utiliza algoritmos ponderados e análise por seções para fornecer comparações precisas e detalhadas com formatação mista otimizada.

## 🚀 Funcionalidades Principais

- ✅ **Análise Sofisticada por Seções** - Cada seção tem algoritmo específico
- ✅ **Banco de Dados Persistente** - SQLite com dados preservados
- ✅ **Sistema de Backup e Restore** - Proteção e migração completa de dados
- ✅ **Formatação Totalmente Otimizada** - Cabeçalhos e títulos em texto normal, dados em monospace
- ✅ **Comandos de Gerenciamento** - Interface completa via comandos
- ✅ **Análise Avançada de Holders** - Concentração, oligopólio e distribuição
- ✅ **Source Wallets Inteligente** - Análise real de porcentagem, quantidade e hops
- ✅ **Wallet Insights Detalhado** - 12 tipos diferentes de carteiras
- ✅ **Risk Metrics Avançado** - Métricas de risco e análise de supply
- ✅ **Sistema de Pesos** - Algoritmos específicos para cada tipo de dado
- ✅ **Comparação Visual Completa** - Exibição lado a lado com identificação (ATUAL | BD)
- ✅ **Relatórios Detalhados** - Exportação em TXT com todos os dados

## 📋 Comandos Disponíveis

- `/database` - Gera e envia arquivo TXT com todos os dados salvos no banco
- `/stats` - Mostra estatísticas rápidas do banco de dados  
- `/clear confirmar` - Remove TODOS os dados do banco (irreversível)
- `/delete` - Exclusão seletiva de tokens por ID, nome ou faixa
- `/del <endereço>` - Deleta token por endereço de contrato
- `/threshold <valor>` - Define threshold mínimo de similaridade para exibição
- `/reset confirmar` - Limpa lista de contratos já exibidos (permite repetições)
- `/cas` - Lista todos os contratos salvos no banco de dados
- `/backup` - Cria backup do banco de dados e envia como arquivo
- `/restore` - Restaura banco de dados a partir de um arquivo de backup
- `/getid` - Mostra ID e informações do grupo atual
- `/help` - Mostra ajuda completa com todas as funcionalidades

### 🗑️ Exclusão Seletiva de Tokens

O comando `/delete` permite apagar tokens específicos do banco de dados:

```
/delete id <número>        - Apaga token por ID específico
/delete token <nome>       - Apaga token por nome
/delete last               - Apaga o último token adicionado
/delete list               - Lista tokens disponíveis para seleção
/delete range <id1> <id2>  - Apaga tokens em faixa de IDs
```

**Exemplos:**
- `/delete id 5` - Apaga o token com ID 5
- `/delete token MemeToken` - Apaga o token chamado "MemeToken"
- `/delete last` - Apaga o último token adicionado
- `/delete range 10 15` - Apaga tokens de ID 10 a 15
- `/delete list` - Mostra lista de tokens para escolher

### 🗑️ Exclusão por Endereço de Contrato

O comando `/del` permite apagar tokens pelo endereço de contrato:

```
/del <endereço_contrato>  - Apaga token por endereço de contrato
```

**Exemplo:**
- `/del U6Po1nXztih5YD3zRmn9zoTpx97tYrFKxEm137eX9C4`

**Características:**
- ✅ Valida formato do endereço (40-50 caracteres)
- ✅ Verifica se o token existe antes de deletar
- ✅ Mostra confirmação com nome do token e ID
- ✅ Suporta múltiplos tokens com mesmo endereço

### 🎯 Configuração de Threshold de Similaridade

O comando `/threshold` permite definir o valor mínimo de similaridade para exibição no grupo de comparação:

```
/threshold           - Mostra o valor atual do threshold
/threshold <valor>   - Define novo threshold (0-100)
```

**Exemplos:**
- `/threshold` - Mostra threshold atual
- `/threshold 75` - Define threshold para 75%
- `/threshold 85.5` - Define threshold para 85.5%

**Funcionamento:**
- ✅ Apenas tokens com similaridade ≥ threshold são exibidos
- ✅ Tokens abaixo do threshold mostram aviso de "similaridade baixa"
- ✅ Valor padrão: 70.0%
- ✅ Range válido: 0.0% a 100.0%
- ✅ Configuração persistente no banco de dados

### 🔄 Sistema Anti-Repetição

O bot evita mostrar o mesmo token múltiplas vezes usando o endereço de contrato como identificador único:

```
/reset           - Mostra quantos contratos já foram exibidos
/reset confirmar - Limpa lista e permite repetições novamente
```

**Funcionamento:**
- ✅ Cada endereço de contrato é exibido apenas **uma vez**
- ✅ Mesmo se o token aparecer novamente, **não será mostrado**
- ✅ Lista persistente no banco de dados (não se perde ao reiniciar)
- ✅ Comando `/reset` permite limpar e começar do zero

**Exemplo:**
```
1ª vez: Token ABC (endereço: XYZ123...) → ✅ EXIBE
2ª vez: Token ABC (endereço: XYZ123...) → 🔇 NÃO EXIBE (já mostrado)
3ª vez: Token ABC (endereço: XYZ123...) → 🔇 NÃO EXIBE (já mostrado)

Após /reset confirmar:
4ª vez: Token ABC (endereço: XYZ123...) → ✅ EXIBE (lista limpa)
```

### 💾 Sistema de Backup e Restore

O bot possui sistema completo de backup e restauração do banco de dados para proteger e migrar seus dados:

#### 🔄 **Comando /backup**
```
/backup  - Cria backup completo do banco de dados
```

**Funcionamento:**
- ✅ Cria cópia completa do banco SQLite atual
- ✅ Adiciona timestamp no nome do arquivo (backup_database_YYYYMMDD_HHMMSS.db)
- ✅ Envia arquivo como documento via Telegram
- ✅ Remove arquivo temporário após envio
- ✅ Mostra informações do backup (quantidade de tokens, tamanho)

**Exemplo de uso:**
```
Comando: /backup
Resposta: 
💾 BACKUP DO BANCO DE DADOS

📊 Tokens: 47
📁 Tamanho: 2048 bytes  
🕒 Criado em: 16/01/2025 14:30:25

✅ Backup criado com sucesso!
💡 Use /restore para restaurar este backup.

[Arquivo: backup_database_20250116_143025.db]
```

#### 🔄 **Comando /restore**
```
/restore  - Restaura banco a partir de arquivo de backup
```

**Como usar:**
1. Envie o comando `/restore` **junto com o arquivo de backup** anexado
2. O arquivo deve ter extensão `.db` e ser um backup válido
3. O sistema validará o arquivo antes de restaurar
4. Backup automático do banco atual será criado antes da restauração

**Segurança:**
- ✅ **Validação completa** do arquivo de backup
- ✅ **Backup automático** do banco atual antes de restaurar
- ✅ **Verificação de integridade** das tabelas necessárias
- ✅ **Limite de tamanho** de 20MB para segurança
- ✅ **Rollback disponível** através do backup automático

**Exemplo de uso:**
```
1. Enviar /restore + arquivo backup_database_20250116_143025.db
2. Sistema valida o arquivo
3. Cria backup automático do banco atual
4. Substitui banco atual pelo backup
5. Confirma restauração com estatísticas

Resposta:
✅ BANCO RESTAURADO COM SUCESSO!

📊 Dados anteriores:
   • Tokens: 47
   • Tamanho: 2048 bytes

📊 Dados restaurados:  
   • Tokens: 35
   • Tamanho: 1856 bytes

💾 Backup automático do banco anterior foi criado
🔄 O bot agora está usando os dados restaurados.
```

**Casos de uso:**
- 🔄 **Migração de dados** entre servidores
- 💾 **Backup preventivo** antes de operações críticas  
- 🔙 **Restauração** após problemas no banco
- 📋 **Clonagem** de configurações entre bots
- 🔄 **Versioning** de diferentes estados do banco

## 🧮 Sistema Avançado de Análise

### 📊 **Market Overview (Peso: 20%)**
- Market Cap, Price Change, Traders
- Buy/Sell Volume e Count
- Buyers vs Sellers



### 📊 **Wallet Insights (Peso: 20%)**
- **12 tipos de carteiras:** Holders Totais, Smart Wallets, Fresh Wallets
- **Análise completa:** Renowned, Creator, Sniper, Rat Traders
- **Métricas avançadas:** Whale, Top, Following, Bluechip, Bundler

### 📈 **Risk Metrics (Peso: 15%)**
- **Supply Analysis:** % Bluechip Holders, % Rat Trader Supply
- **Risk Indicators:** % Bundler Supply, % Entrapment Supply
- **Technical Signals:** Degen Calls, Sinais Técnicos

### 💎 **Top 10 Holders (Peso: 25%) - Algoritmo Sofisticado**
- **Porcentagem Total** dos top 10 (peso: 20%)
- **Concentração Top 1** holder (peso: 30%)
- **Oligopólio Top 5** holders (peso: 25%)
- **Score de Distribuição** estatística (peso: 25%)

### 🔍 **Source Wallets (Peso: 15%) - Análise Real**
- **Porcentagem Total** (peso: 50%)
- **Quantidade de Wallets** (peso: 25%)
- **Média de Hops** (peso: 25%)

## 🛠️ Instalação e Configuração

### 1. **Preparação do Ambiente**
```bash
git clone <url-do-repositorio>
cd solsimilarity
pip install -r requirements.txt
```

### 2. **Configuração do Bot**

#### 2.1 Criar Bot no BotFather
1. Converse com `@BotFather` no Telegram
2. Digite `/newbot`
3. Escolha nome e username
4. Copie o token fornecido

#### 2.2 Configurar Menu de Comandos (Recomendado)
No BotFather, digite `/setcommands` e cole:
```
database - 📊 Gera arquivo TXT com todos os dados salvos
stats - 📈 Mostra estatísticas do banco de dados  
clear - 🗑️ Deleta TODOS os dados (use: /clear confirmar)
help - ❓ Mostra ajuda completa e instruções
```

### 3. **Configurar Variáveis de Ambiente**
Crie arquivo `.env`:
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
DATABASE_GROUP_ID=-1002327861186
COMPARISON_GROUP_ID=-1002864538300
```

### 4. **Execução**
```bash
python3 run.py
```

## 📖 Como Usar

### 🗄️ **Grupo Database** 
Envie mensagens de tokens para armazenar no banco:

```
TokenName (SYMBOL)
├ ContractAddress...
└ Age: 11/07/2025 - 1min15s

👨‍💻 Creator:
└ CreatorAddress...

📊 Market Overview (5m):
├ Market Cap:     $   86.06K
├ Buy Volume:     $   15.85K
├ Price%:            +449.62%
├ Traders:                82



👥 Wallet Statistics:
├ Fresh:       9 (12.33%)
├ Bundler:    13 (17.81%)
└ Total:      73

📊 Top 20 Holders: 24.50%
├  1. 9G6SBN...CZvv - 19.46% -   0.00 SOL
├  2. EruFck...mNeu -  1.01% -   2.89 SOL
...

🔍 Source Wallets:  0.94%
├ FWznbc...ouN5 -  3 hops
└ 5tzFki...uAi9 -  2 hops
```

### 🔍 **Grupo Comparison**
Envie tokens no mesmo formato e receba análise completa:

```
🔍 ANÁLISE DE SIMILARIDADE 🔍
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Token Analisado: NewToken
📍 CA: `ABC123456789DEF...`
🎯 Token Mais Similar: SimilarToken
💯 Similaridade Geral: 78.5%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 SIMILARIDADES POR SEÇÃO:
• 📊 Market Overview: 82.1%
• 📊 Migration Statistics: 100.0%
• 👥 Wallet Statistics: 67.3%
• 📊 Top 20 Holders: 71.2%
• 🔍 Source Wallets: 65.8%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 DADOS DO TOKEN MAIS SIMILAR:
[Dados completos com linhas de similaridade inseridas]
```

## 📁 Estrutura do Projeto

```
solsimilarity/
├── run.py                    # Script de execução
├── bot.py                    # Bot principal com comandos
├── config.py                 # Configurações do sistema
├── database.py              # Gerenciamento SQLite persistente
├── message_parser.py        # Parser avançado por seções
├── similarity_calculator.py # Algoritmos de similaridade
├── requirements.txt         # Dependências Python
├── token_database.db       # Banco SQLite (auto-criado)
├── .env                    # Variáveis de ambiente
└── README.md               # Esta documentação
```

## 🔧 Algoritmos Implementados

### 🧮 **Top 20 Holders - Análise Sofisticada**
```python
# Extração de dados individuais dos holders
holder_percentages = [19.46, 1.01, 0.39, ...]  # Todos os 20

# Métricas calculadas:
- top1_holder_percentage: 19.46%
- top5_holders_percentage: 21.52% (soma dos 5 primeiros)  
- holders_concentration_ratio: 79.43% (top1/total*100)
- holders_distribution_score: 74.3 (desvio padrão normalizado)

# Algoritmo ponderado:
similaridade = (20% × total) + (30% × concentração) + 
               (25% × oligopólio) + (25% × distribuição)
```

### 🔍 **Source Wallets - Análise Real**
```python
# Extração real dos dados:
source_wallets_percentage: 0.94%
source_wallets_count: 2
source_wallets_avg_hops: 2.5

# Algoritmo ponderado:
similaridade = (50% × porcentagem) + (25% × quantidade) + 
               (25% × média_hops)
```

## 🛡️ Segurança e Confiabilidade

- ✅ **Banco Persistente** - Dados não são perdidos no restart
- ✅ **Confirmação para Clear** - Proteção contra deleção acidental
- ✅ **Logs Detalhados** - Rastreamento completo de operações
- ✅ **Tratamento de Erros** - Sistema robusto e estável
- ✅ **Validação de Entrada** - Parsing seguro de mensagens
- ✅ **Formatação Limpa** - Remove emojis desnecessários automaticamente

## 🔧 Troubleshooting

### **Bot não responde aos comandos:**
- Verifique se o bot foi adicionado aos grupos
- Confirme o token no arquivo `.env`
- Verifique logs para erros de conexão

### **Comandos não aparecem no menu:**
- Configure via BotFather usando `/setcommands`
- Reinicie o chat para atualizar o menu

### **Banco de dados vazio após restart:**
- ✅ **Corrigido na v3.0** - Banco agora é persistente
- Arquivo `token_database.db` preserva todos os dados

### **Similaridade incorreta:**
- Verifique formato das mensagens
- Use `/stats` para verificar dados no banco
- Consulte logs para erros de parsing

## 📈 Recursos Técnicos

### **Performance:**
- Algoritmos otimizados por seção
- Banco SQLite com índices eficientes
- Sistema de cache para consultas frequentes

### **Escalabilidade:**
- Suporte a milhares de tokens
- Arquivos TXT compactados automaticamente
- Limpeza controlada via comando seguro

### **Manutenibilidade:**
- Código modular e bem documentado
- Logs estruturados para debugging
- Configurações centralizadas

## 📊 Exemplos de Uso

### **Comando /stats:**
```
📊 ESTATÍSTICAS DO BANCO

✅ Status: Ativo
🔢 Total de tokens: 47
🆕 Último adicionado: MemeToken
📅 Data do último: 2025-07-11 18:22:30

📝 Use /database para baixar relatório completo.
🗑️ Use /clear confirmar para limpar todos os dados.
```

### **Arquivo /database gerado:**
```
================================================================================
🗄️  BANCO DE DADOS DE TOKENS - RELATÓRIO COMPLETO
================================================================================
📅 Data: 11/07/2025 18:22:45
📊 Total de tokens: 47
================================================================================

🪙 TOKEN #1: TokenExample
------------------------------------------------------------
🆔 ID: 1
📅 Data: 2025-07-11 15:30:22
💬 Message ID: 12345
👥 Group ID: -1002327861186

📊 MARKET OVERVIEW:
   💰 Market Cap: $86,060.00
   📈 Price Change: 449.62%
   👤 Traders: 82
   💵 Buy Volume: $15,850.00
   💸 Sell Volume: $677.82
   🟢 Buyers: 82
   🔴 Sellers: 14

📊 TOP HOLDERS ANALYSIS:
   💎 Top 20: 24.50%
   👑 Top 1: 19.46%
   🏆 Top 5: 21.52%
   📊 Concentration: 79.43%
   📈 Distribution Score: 74.3

🔍 SOURCE WALLETS ANALYSIS:
   💧 Percentage: 0.94%
   🔢 Count: 2
   🔗 Avg Hops: 2.5
```

## 🎯 Versão 3.14 - Novidades

- 🆕 **Formatação Mista Inteligente Implementada**
  - 📝 **Rótulos em texto normal**: Token Analisado, CA, Token Mais Similar, Similaridade Geral
  - 💻 **Valores em monospace**: Nomes de tokens, endereços de contrato, percentuais
  - 🎯 **Linhas de similaridade otimizadas**: `========================> 🎯Similaridade:` em normal, porcentagem em monospace
  - ✅ **Máxima legibilidade**: Rótulos destacados + valores precisos em fonte monospace
  - 🎨 **Interface híbrida perfeita**: Combina o melhor da formatação normal e monospace

### Versões Anteriores:
- 🆕 **Espaçamento Perfeito Implementado (v3.13)**
  - 📝 Linha vazia adicionada após cada linha de similaridade (`========================> 🎯Similaridade: XX%`)
  - 🎯 Espaçamento consistente entre todas as seções
  - 📊 Formatação uniforme em todo o relatório de análise
  - ✅ Correção do espaçamento que estava faltando em algumas seções

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

---

**🚀 Bot de Similaridade v3.14 - Formatação Mista Inteligente Implementada** 

## 🔧 Versão Atual

**v3.14 - Formatação Mista Inteligente**

### ✨ Novidades da Versão 3.14:
- ✅ **Formatação Mista** - Rótulos normais + valores monospace
- ✅ **Rótulos Destacados** - Token Analisado, CA, Token Mais Similar, etc.
- ✅ **Valores Precisos** - Nomes, endereços e percentuais em monospace
- ✅ **Interface Híbrida** - Máxima legibilidade + precisão visual
- ✅ **Similaridade Otimizada** - Porcentagens destacadas em monospace
- ✅ **Experiência Perfeita** - Combina o melhor dos dois mundos # solsimilarity
