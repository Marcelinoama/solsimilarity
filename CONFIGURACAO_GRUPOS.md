# 📋 Configuração dos Grupos - Bot de Similaridade v3.7

## 🔧 Configuração do Terceiro Grupo

O bot agora suporta **três grupos** para melhor organização:

### 1. 📊 Grupo de Banco de Dados (DATABASE_GROUP_ID)
- **Função**: Armazena mensagens de tokens para comparação
- **Comportamento**: 
  - Salva tokens no banco de dados
  - Confirma salvamento com mensagem
  - Não realiza comparações

### 2. 🔍 Grupo de Comparação (COMPARISON_GROUP_ID)
- **Função**: Processa mensagens para comparação
- **Comportamento**:
  - Compara tokens com o banco de dados
  - Processa silenciosamente (sem respostas no grupo)
  - Envia notificações automaticamente para o grupo de notificação

### 3. 🔔 Grupo de Notificação (NOTIFICATION_GROUP_ID)
- **Função**: Recebe apenas notificações de similaridade
- **Comportamento**:
  - Recebe notificações automaticamente
  - Não processa mensagens enviadas aqui
  - Foco apenas em notificações

## ⚙️ Como Configurar

### 1. Edite o arquivo `.env`:

```env
# Token do bot do Telegram (obtenha com @BotFather)
BOT_TOKEN=seu_token_do_bot_aqui

# ID do grupo que servirá como banco de dados  
DATABASE_GROUP_ID=-1001234567890

# ID do grupo onde chegam as mensagens para comparação
COMPARISON_GROUP_ID=-1001234567891

# ID do grupo onde são enviadas as notificações de similaridade
NOTIFICATION_GROUP_ID=-1001234567892
```

### 2. Para obter IDs dos grupos:

```bash
python get_group_ids.py
```

1. Crie três grupos no Telegram
2. Adicione o bot aos três grupos
3. Execute o comando acima
4. Envie uma mensagem em cada grupo
5. Copie os IDs mostrados para o arquivo `.env`

### 3. Comandos úteis:

- `/getid` - Mostra ID do grupo atual
- `/help` - Mostra informações completas dos grupos

## 🔄 Fluxo de Funcionamento

```
1. Token enviado no GRUPO DE BANCO DE DADOS
   ↓
   💾 Salvo no banco de dados
   
2. Token enviado no GRUPO DE COMPARAÇÃO
   ↓
   🔍 Comparado com banco de dados (processamento silencioso)
   ↓
   🔔 Notificação enviada APENAS para GRUPO DE NOTIFICAÇÃO
```

## 📝 Observações Importantes

- **Todos os três grupos** devem estar configurados
- O bot deve estar **adicionado nos três grupos**
- As **notificações são enviadas automaticamente**
- O grupo de notificação é **apenas para receber** (não processa mensagens)

## 🚀 Benefícios

- **Organização**: Separação clara entre dados, comparação e notificações
- **Foco**: Grupo de notificação fica limpo, apenas com resultados
- **Flexibilidade**: Pode usar o mesmo grupo para múltiplas funções se necessário
- **Monitoramento**: Fácil acompanhamento de similaridades em grupo dedicado
- **Comparação Visual**: Dados lado a lado para análise rápida e eficiente

## 🔄 Nova Funcionalidade - Comparação Lado a Lado

### 📊 Formato Visual Aprimorado

A partir da versão 3.8, o bot exibe uma comparação visual completa lado a lado entre o token atual e o token similar encontrado no banco de dados, com identificação clara:

```
📊 MARKET OVERVIEW:
                         ATUAL |        BD
├ Market Cap        :  $204.66K |  $204.66K  
├ Buy Volume        :  $212.46K |  $212.46K  
├ Sell Volume       :  $185.64K |  $185.64K  
├ Price%            : +3917.57% | +3917.57%  
├ Traders           :  1,013    |  1,013  
├ Buy Count         :  1,945    |  1,945  
├ Sell Count        :  1,562    |  1,562  
├ Buyers            :  1,012    |  1,012  
└ Sellers           :    803    |    803  
============================>🎯Similaridade: 85%
```

### 🎯 Seções Comparadas

1. **📊 Market Overview**: Market Cap, Volumes, Traders, Contadores
2. **📊 Migration Statistics**: Tokens criados, migrados e taxa de sucesso
3. **📊 Wallet Insights**: Tipos de carteiras e quantidades
4. **📈 Risk Metrics**: Indicadores de risco e métricas avançadas
5. **📊 Top 10 Holders**: Concentração de holders principais
6. **🔍 Source Wallets**: Análise de carteiras de origem

### 📋 Formatação Inteligente

- **Moeda**: Formato K (milhares) e M (milhões)
- **Porcentagem**: Sinal + para positivo, - para negativo
- **Números**: Separadores de milhares (1,234)
- **Decimais**: Uma casa decimal para precisão
- **Alinhamento**: Formatação visual consistente
- **Identificação**: ATUAL (token analisado) | BD (token do banco de dados) 