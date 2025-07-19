import logging
import os
import io
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from config import Config
from database import TokenDatabase
from message_parser import MessageParser
from similarity_calculator import SimilarityCalculator

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimilarityBot:
    def __init__(self):
        self.database = TokenDatabase()
        self.parser = MessageParser()
        self.similarity_calculator = SimilarityCalculator()
    
    def _validate_html_message(self, message: str) -> str:
        """Valida e corrige HTML na mensagem antes de enviar"""
        if not message:
            return ""
        
        # Remove linhas vazias excessivas
        import re
        message = re.sub(r'\n\s*\n\s*\n', '\n\n', message)
        
        return message
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula mensagens recebidas nos grupos"""
        
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        
        logger.info(f"Mensagem recebida no chat {chat_id}")
        
        # Verifica se a mensagem contém informações de token
        if not self._is_token_message(message_text):
            return
        
        try:
            # Parse da mensagem
            token_data = self.parser.parse_token_message(message_text)
            
            # Captura entidades de link da mensagem (para hiperlinks invisíveis)
            message_entities = update.message.entities if update.message.entities else []
            token_data['message_entities'] = message_entities
            
            # DEBUG: Log detalhado das entidades para debug
            if message_entities:
                logger.info(f"🔍 DEBUG: {len(message_entities)} entidades encontradas na mensagem")
                for i, entity in enumerate(message_entities):
                    text_slice = message_text[entity.offset:entity.offset + entity.length] if entity.offset < len(message_text) else "ERRO"
                    entity_url = getattr(entity, 'url', 'N/A')
                    logger.info(f"  📋 Entidade {i+1}: tipo='{entity.type}', offset={entity.offset}, length={entity.length}, texto='{text_slice}', url='{entity_url}'")
            else:
                logger.info("🔍 DEBUG: Nenhuma entidade encontrada na mensagem")
            
            if str(chat_id) == Config.DATABASE_GROUP_ID:
                # Grupo de banco de dados - salva a informação
                await self._handle_database_message(token_data, message_id, chat_id, update, context)
                
            elif str(chat_id) == Config.COMPARISON_GROUP_ID:
                # Grupo de comparação - compara com banco de dados e envia notificação
                await self._handle_comparison_message(token_data, update, context)
                
            elif str(chat_id) == Config.NOTIFICATION_GROUP_ID:
                # Grupo de notificação - apenas processa mensagens se necessário
                await self._handle_notification_message(token_data, update, context)
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            await update.message.reply_text("❌ Erro ao processar a mensagem.")
    
    def _is_token_message(self, message_text: str) -> bool:
        """Verifica se a mensagem contém informações de token"""
        # Procura por padrões característicos das mensagens de token
        indicators = [
            '📊 Market Overview',
            'Market Cap:',
            '📊 Wallet Insights',
            '📈 Risk Metrics',
            '📊 Top 10 Holders',
            
            # Mantém compatibilidade com formato antigo
            '👥 Wallet Statistics',
            '📊 Top 20 Holders'
        ]
        
        return any(indicator in message_text for indicator in indicators)
    
    async def _handle_database_message(self, token_data, message_id, chat_id, update, context):
        """Manipula mensagens do grupo de banco de dados"""
        try:
            token_name = token_data.get('token_name', 'Token desconhecido')
            contract_address = token_data.get('contract_address')
            
            # Verifica se o contrato já existe no banco de dados
            if contract_address:
                existing_token = self.database.is_contract_already_in_database(contract_address)
                
                if existing_token:
                    # Token já existe - envia aviso
                    existing_id, existing_name, existing_timestamp = existing_token
                    logger.info(f"Token duplicado detectado: {token_name} (CA: {contract_address})")
                    
                    warning_message = (
                        f"⚠️ **TOKEN DUPLICADO DETECTADO**\n\n"
                        f"📋 **Token atual:** {token_name}\n"
                        f"🔍 **Endereço:** `{contract_address}`\n\n"
                        f"💾 **Já existe no banco de dados:**\n"
                        f"• **Nome:** {existing_name}\n"
                        f"• **ID:** {existing_id}\n"
                        f"• **Salvo em:** {existing_timestamp}\n\n"
                        f"❌ **Token NÃO foi salvo** para evitar duplicatas.\n"
                        f"🗑️ Use `/del {contract_address}` para remover o token existente se necessário."
                    )
                    
                    await update.message.reply_text(warning_message, parse_mode='Markdown')
                    return
            
            # Salva no banco de dados
            self.database.save_token_info(token_data, message_id, chat_id)
            
            logger.info(f"Token salvo no banco de dados: {token_name}")
            
            # Confirma o salvamento
            if contract_address:
                await update.message.reply_text(f"✅ **{token_name}** salvo no banco de dados!\n📍 **CA:** `{contract_address}`", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"✅ **{token_name}** salvo no banco de dados!", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco de dados: {e}")
            await update.message.reply_text("❌ Erro ao salvar token no banco de dados.")
    
    async def _handle_comparison_message(self, token_data, update, context):
        """Manipula mensagens do grupo de comparação"""
        try:
            # Busca todos os tokens do banco de dados
            database_tokens = self.database.get_all_tokens()
            
            if not database_tokens:
                await update.message.reply_text("📭 Banco de dados vazio. Adicione tokens no grupo de banco de dados primeiro.")
                return
            
            # Encontra o token mais similar
            most_similar_token, similarity, section_similarities = self.similarity_calculator.find_most_similar_token(
                token_data, database_tokens
            )
            
            # Verifica se já foi exibido anteriormente (usando endereço de contrato)
            contract_address = token_data.get('contract_address')
            
            if contract_address and self.database.is_contract_already_displayed(contract_address):
                # Não exibe nada se já foi mostrado antes
                return
            
            # Verifica se a similaridade atende ao threshold mínimo
            min_threshold = self.database.get_min_similarity_threshold()
            
            if similarity < min_threshold:
                # Não exibe nada se estiver abaixo do threshold
                return
            
            # Marca contrato como exibido para evitar repetições futuras
            token_name = token_data.get('token_name', 'Token desconhecido')
            if contract_address:
                self.database.mark_contract_as_displayed(contract_address, token_name, similarity)
            
            # Cria relatório completo com formatação mono-espaçada
            enhanced_message = self.similarity_calculator.create_enhanced_message(
                token_name, most_similar_token, similarity, section_similarities, 
                token_data.get('raw_message', ''), contract_address
            )
            
            # Adiciona comparação lado a lado dentro do mesmo bloco de código
            if most_similar_token:
                side_by_side_comparison = self.similarity_calculator.create_side_by_side_comparison(
                    token_data, most_similar_token, section_similarities
                )
                
                # Remove apenas o fechamento ``` do final e adiciona a comparação
                if enhanced_message.endswith("```"):
                    enhanced_message = enhanced_message[:-3]  # Remove apenas os últimos 3 caracteres
                enhanced_message += side_by_side_comparison
                
                # Adiciona social links no rodapé se estiverem disponíveis
                social_links_section = self.similarity_calculator.get_social_links_section(
                    token_data.get('raw_message', ''), 
                    token_data.get('message_entities', [])
                )
                if social_links_section:
                    enhanced_message += "\n" + social_links_section + "\n"
                
                enhanced_message += "```"
            
            # Envia notificação APENAS para o grupo de notificação
            await self._send_notification_to_group(context, enhanced_message, token_name, similarity)
            
        except Exception as e:
            logger.error(f"Erro ao comparar tokens: {e}")
            # Não envia mensagem de erro no grupo de comparação, apenas no log
    
    async def _handle_notification_message(self, token_data, update, context):
        """Manipula mensagens do grupo de notificação"""
        # O grupo de notificação é apenas para receber notificações
        # Não processa mensagens enviadas aqui
        logger.info(f"Mensagem recebida no grupo de notificação - ignorada")
        return
    
    async def _send_notification_to_group(self, context, enhanced_message, token_name, similarity):
        """Envia notificação de similaridade para o grupo de notificação"""
        if not Config.NOTIFICATION_GROUP_ID:
            logger.warning("NOTIFICATION_GROUP_ID não configurado - notificação não enviada")
            return
            
        try:
            # Verifica tamanho da mensagem (limite do Telegram: 4096 caracteres)
            if len(enhanced_message) > 4000:
                # Se a mensagem for muito longa, envia versão resumida
                short_message = f"🔍 ANÁLISE DE SIMILARIDADE\n"
                short_message += f"📌 Token: {token_name}\n"
                short_message += f"✅ Similaridade: {similarity:.1f}%\n"
                short_message += f"⚠️ Relatório completo muito longo - verifique logs"
                enhanced_message = short_message  # Remove as crases aqui também
            
            # Remove formatação de código e aplica monospace linha por linha
            clean_message = enhanced_message.replace('```', '')
            
            # Lista de títulos de seções que devem aparecer em formatação normal
            section_titles = [
                'Market Overview:',
                'Wallet Insights:',
                'Risk Metrics:',
                'Top 10 Holders:',
                'Source Wallets:',
                'Market Overview (24h):',
                'Wallet Insights:',
                'Risk Metrics:',
                'Source Wallets:',
                'Similaridades por seção:',
                'Social Links:'
            ]
            
            # Lista de elementos adicionais que devem aparecer em formatação normal
            normal_format_elements = [
                'ANÁLISE DE SIMILARIDADE',
                'Token Analisado:',
                'CA:',
                'Token Mais Similar:',
                'Similaridade Geral:',
                'Lado esquerdo ATUAL direito BANCO DE DADOS',
                '🎯Similaridade:'
            ]
            
            # Aplica <code> em cada linha para fonte mono sem fundo preto, exceto títulos e elementos especiais
            lines = clean_message.split('\n')
            formatted_lines = []
            for line in lines:
                if line.strip():  # Se linha não está vazia
                    
                    # Verifica se é um título de seção que deve ficar em formatação normal
                    # Títulos de seção não começam com ├ ou └ e terminam com :
                    line_trimmed = line.strip()
                    is_section_title = (
                        any(title in line for title in section_titles) and 
                        not line_trimmed.startswith('├') and 
                        not line_trimmed.startswith('└') and
                        line_trimmed.endswith(':')
                    )
                    
                    # Verifica se é uma linha de similaridade (contém ========================>)
                    is_similarity_line = '========================>' in line
                    
                    # Verifica se é um cabeçalho específico que precisa formatação mista
                    is_mixed_format_line = any(element in line for element in [
                        'Token Analisado:', 'CA:', 'Token Mais Similar:', 'Similaridade Geral:'
                    ])
                    
                    # Verifica se é um elemento que deve ficar completamente em formatação normal
                    is_normal_element = any(element in line for element in [
                        'ANÁLISE DE SIMILARIDADE',
                        'Lado esquerdo ATUAL direito BANCO DE DADOS'
                    ])
                    
                    # Verifica se é uma linha de social links
                    is_social_link_line = ('🌐 Social Links' in line or
                                         ('├' in line and ('http://' in line or 'https://' in line)) or
                                         ('└' in line and ('http://' in line or 'https://' in line)))
                    
                    # Escapa caracteres HTML perigosos (exceto para linhas de similaridade e social links)
                    if is_similarity_line or is_social_link_line:
                        escaped_line = line  # Não escapa caracteres nas linhas de similaridade e social links
                    else:
                        escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    
                    if is_section_title or is_normal_element:
                        # Formatação normal completa
                        formatted_lines.append(escaped_line)
                    elif is_mixed_format_line:
                        # Formatação mista: rótulo normal + valor monospace
                        if 'Token Analisado:' in line:
                            parts = line.split('Token Analisado:', 1)
                            if len(parts) == 2:
                                label = 'Token Analisado:'
                                value = parts[1].strip()
                                formatted_lines.append(f'{label} <code>{value}</code>')
                            else:
                                formatted_lines.append(escaped_line)
                        elif 'CA:' in line:
                            parts = line.split('CA:', 1)
                            if len(parts) == 2:
                                label = 'CA:'
                                value = parts[1].strip()
                                formatted_lines.append(f'{label}  <code>{value}</code>')
                            else:
                                formatted_lines.append(escaped_line)
                        elif 'Token Mais Similar:' in line:
                            parts = line.split('Token Mais Similar:', 1)
                            if len(parts) == 2:
                                label = 'Token Mais Similar:'
                                value = parts[1].strip()
                                formatted_lines.append(f'{label}  <code>{value}</code>')
                            else:
                                formatted_lines.append(escaped_line)
                        elif 'Similaridade Geral:' in line:
                            parts = line.split('Similaridade Geral:', 1)
                            if len(parts) == 2:
                                label = 'Similaridade Geral:'
                                value = parts[1].strip()
                                formatted_lines.append(f'{label}  <code>{value}</code>')
                            else:
                                formatted_lines.append(escaped_line)
                        else:
                            formatted_lines.append(escaped_line)
                    elif is_similarity_line:
                        # Linha de similaridade: toda a linha em formatação normal
                        formatted_lines.append(escaped_line)
                    elif is_social_link_line:
                        # Linha de social links com hiperlinks: preserva formatação HTML
                        formatted_lines.append(escaped_line)
                    else:
                        # Outras linhas com formatação monospace
                        # Tratamento especial para linhas com ├ e └ - mantém caracteres em formatação normal
                        # EXCETO para social links que devem preservar HTML
                        if line_trimmed.startswith('├') and not is_social_link_line:
                            # Remove ├ do início e aplica formatação monospace apenas ao resto
                            content_without_prefix = escaped_line.lstrip().lstrip('├').strip()
                            formatted_lines.append(f'├ <code>{content_without_prefix}</code>')
                        elif line_trimmed.startswith('└') and not is_social_link_line:
                            # Remove └ do início e aplica formatação monospace apenas ao resto
                            content_without_prefix = escaped_line.lstrip().lstrip('└').strip()
                            formatted_lines.append(f'└ <code>{content_without_prefix}</code>')
                        elif is_social_link_line:
                            # Social links preservam HTML sem formatação monospace
                            formatted_lines.append(escaped_line)
                        else:
                            formatted_lines.append(f'<code>{escaped_line}</code>')
                else:
                    formatted_lines.append('')  # Mantém linha vazia
            
            formatted_message = '\n'.join(formatted_lines)
            
            # Valida e sanitiza HTML antes de enviar
            validated_message = self._validate_html_message(formatted_message)
            
            # Envia usando HTML parse mode
            await context.bot.send_message(
                chat_id=Config.NOTIFICATION_GROUP_ID,
                text=validated_message,
                parse_mode='HTML'
            )
            
            logger.info(f"Notificação enviada para grupo de notificação: {token_name} (similaridade: {similarity:.1f}%)")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação para grupo de notificação: {e}")
    
    async def database_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gera e envia arquivo TXT com dados do banco de dados"""
        if not update.message:
            return
            
        try:
            # Busca todos os tokens do banco
            database_tokens = self.database.get_all_tokens()
            
            if not database_tokens:
                await update.message.reply_text("📭 Banco de dados vazio. Nenhum token encontrado.")
                return
            
            # Gera conteúdo do arquivo
            txt_content = self._generate_database_txt(database_tokens)
            
            # Cria arquivo em memória
            file_buffer = io.BytesIO()
            file_buffer.write(txt_content.encode('utf-8'))
            file_buffer.seek(0)
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_tokens_{timestamp}.txt"
            
            # Envia arquivo
            await update.message.reply_document(
                document=file_buffer,
                filename=filename,
                caption=f"📊 **Banco de Dados - {len(database_tokens)} tokens**\n🕒 Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            logger.info(f"Arquivo de database enviado: {filename} ({len(database_tokens)} tokens)")
            
        except Exception as e:
            logger.error(f"Erro ao gerar arquivo de database: {e}")
            await update.message.reply_text("❌ Erro ao gerar arquivo do banco de dados.")
    
    def _generate_database_txt(self, tokens):
        """Gera conteúdo TXT com dados dos tokens"""
        content = []
        content.append("=" * 80)
        content.append("🗄️  BANCO DE DADOS DE TOKENS - RELATÓRIO COMPLETO")
        content.append("=" * 80)
        content.append(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        content.append(f"📊 Total de tokens: {len(tokens)}")
        content.append("=" * 80)
        content.append("")
        
        for i, token in enumerate(tokens, 1):
            content.append(f"🪙 TOKEN #{i}: {token.get('token_name', 'Token Desconhecido')}")
            content.append("-" * 60)
            content.append(f"🆔 ID: {token.get('id', 'N/A')}")
            content.append(f"📅 Data: {token.get('timestamp', 'N/A')}")
            content.append(f"💬 Message ID: {token.get('message_id', 'N/A')}")
            content.append(f"👥 Group ID: {token.get('group_id', 'N/A')}")
            content.append("")
            
            # Market Overview
            content.append("📊 MARKET OVERVIEW:")
            content.append(f"   💰 Market Cap: ${token.get('market_cap', 'N/A'):,.2f}" if token.get('market_cap') else "   💰 Market Cap: N/A")
            content.append(f"   📈 Price Change: {token.get('price_change', 'N/A')}%" if token.get('price_change') is not None else "   📈 Price Change: N/A")
            content.append(f"   👤 Traders: {token.get('traders', 'N/A'):,}" if token.get('traders') else "   👤 Traders: N/A")
            content.append(f"   💵 Buy Volume: ${token.get('buy_volume', 'N/A'):,.2f}" if token.get('buy_volume') else "   💵 Buy Volume: N/A")
            content.append(f"   💸 Sell Volume: ${token.get('sell_volume', 'N/A'):,.2f}" if token.get('sell_volume') else "   💸 Sell Volume: N/A")
            content.append(f"   🟢 Buyers: {token.get('buyers', 'N/A'):,}" if token.get('buyers') else "   🟢 Buyers: N/A")
            content.append(f"   🔴 Sellers: {token.get('sellers', 'N/A'):,}" if token.get('sellers') else "   🔴 Sellers: N/A")
            content.append("")
            

            
            # Wallet Statistics
            content.append("👥 WALLET STATISTICS:")
            content.append(f"   🆕 Fresh: {token.get('fresh_percentage', 'N/A')}%" if token.get('fresh_percentage') is not None else "   🆕 Fresh: N/A")
            content.append(f"   🔝 Top: {token.get('top_percentage', 'N/A')}%" if token.get('top_percentage') is not None else "   🔝 Top: N/A")
            content.append(f"   📦 Bundler: {token.get('bundler_percentage', 'N/A')}%" if token.get('bundler_percentage') is not None else "   📦 Bundler: N/A")
            content.append(f"   🔢 Total Wallets: {token.get('total_wallets', 'N/A'):,}" if token.get('total_wallets') else "   🔢 Total Wallets: N/A")
            content.append("")
            
            # Top Holders Analysis
            content.append("📊 TOP HOLDERS ANALYSIS:")
            content.append(f"   💎 Top 20: {token.get('top_holders_percentage', 'N/A')}%" if token.get('top_holders_percentage') is not None else "   💎 Top 20: N/A")
            content.append(f"   👑 Top 1: {token.get('top1_holder_percentage', 'N/A')}%" if token.get('top1_holder_percentage') is not None else "   👑 Top 1: N/A")
            content.append(f"   🏆 Top 5: {token.get('top5_holders_percentage', 'N/A')}%" if token.get('top5_holders_percentage') is not None else "   🏆 Top 5: N/A")
            content.append(f"   📊 Concentration: {token.get('holders_concentration_ratio', 'N/A')}%" if token.get('holders_concentration_ratio') is not None else "   📊 Concentration: N/A")
            content.append(f"   📈 Distribution Score: {token.get('holders_distribution_score', 'N/A'):.1f}" if token.get('holders_distribution_score') is not None else "   📈 Distribution Score: N/A")
            content.append("")
            
            # Source Wallets Analysis
            content.append("🔍 SOURCE WALLETS ANALYSIS:")
            content.append(f"   💧 Percentage: {token.get('source_wallets_percentage', 'N/A')}%" if token.get('source_wallets_percentage') is not None else "   💧 Percentage: N/A")
            content.append(f"   🔢 Count: {token.get('source_wallets_count', 'N/A')}" if token.get('source_wallets_count') is not None else "   🔢 Count: N/A")
            content.append(f"   🔗 Avg Hops: {token.get('source_wallets_avg_hops', 'N/A'):.1f}" if token.get('source_wallets_avg_hops') is not None else "   🔗 Avg Hops: N/A")
            content.append("")
            
            content.append("=" * 80)
            content.append("")
        
        return "\n".join(content)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para limpar todos os dados do banco de dados"""
        if not update.message:
            return
        
        try:
            # Verifica quantos tokens existem
            token_count = self.database.get_tokens_count()
            
            if token_count == 0:
                await update.message.reply_text("📭 Banco de dados já está vazio.")
                return
            
            # Verifica se foi enviado argumento de confirmação
            args = context.args if context.args else []
            
            if not args or args[0].lower() != 'confirmar':
                # Primeira execução - pede confirmação
                confirmation_text = (
                    f"⚠️ **ATENÇÃO - OPERAÇÃO PERIGOSA** ⚠️\n\n"
                    f"🗄️ Banco de dados atual: **{token_count} tokens**\n\n"
                    f"❌ Esta ação irá **DELETAR TODOS** os dados salvos!\n"
                    f"🚨 Esta operação **NÃO PODE SER DESFEITA**!\n\n"
                    f"📝 Para confirmar, digite:\n"
                    f"`/clear confirmar`\n\n"
                    f"🔒 Para cancelar, ignore esta mensagem."
                )
                await update.message.reply_text(confirmation_text, parse_mode='Markdown')
                return
            
            # Confirmação recebida - executa limpeza
            user_id = update.effective_user.id if update.effective_user else "desconhecido"
            logger.info(f"Limpeza do banco de dados solicitada por usuário {user_id}")
            deleted_count = self.database.clear_all_tokens()
            
            success_text = (
                f"✅ **BANCO DE DADOS LIMPO COM SUCESSO!**\n\n"
                f"🗑️ Tokens deletados: **{deleted_count}**\n"
                f"📊 Status atual: **Banco vazio**\n\n"
                f"💡 Você pode adicionar novos tokens no grupo database."
            )
            
            await update.message.reply_text(success_text, parse_mode='Markdown')
            logger.info(f"Banco de dados limpo: {deleted_count} tokens deletados")
            
        except Exception as e:
            logger.error(f"Erro ao limpar banco de dados: {e}")
            await update.message.reply_text("❌ Erro ao limpar o banco de dados.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para mostrar estatísticas do banco de dados"""
        if not update.message:
            return
        
        try:
            token_count = self.database.get_tokens_count()
            
            if token_count == 0:
                stats_text = (
                    f"📊 **ESTATÍSTICAS DO BANCO**\n\n"
                    f"📭 Status: **Vazio**\n"
                    f"🔢 Total de tokens: **0**\n\n"
                    f"💡 Adicione tokens no grupo database para começar."
                )
            else:
                # Busca último token adicionado
                tokens = self.database.get_all_tokens()
                latest_token = max(tokens, key=lambda x: x.get('id', 0))
                
                stats_text = (
                    f"📊 **ESTATÍSTICAS DO BANCO**\n\n"
                    f"✅ Status: **Ativo**\n"
                    f"🔢 Total de tokens: **{token_count}**\n"
                    f"🆕 Último adicionado: **{latest_token.get('token_name', 'N/A')}**\n"
                    f"📅 Data do último: **{latest_token.get('timestamp', 'N/A')}**\n\n"
                    f"📝 Use `/database` para baixar relatório completo.\n"
                    f"🗑️ Use `/clear confirmar` para limpar todos os dados."
                )
            
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            await update.message.reply_text("❌ Erro ao obter estatísticas do banco.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando de ajuda mostrando todos os comandos disponíveis"""
        if not update.message:
            return
        
        help_text = (
            f"🤖 **BOT DE SIMILARIDADE DE TOKENS**\n\n"
            f"📋 **COMANDOS DISPONÍVEIS:**\n\n"
            f"📊 `/database` - Gera arquivo TXT com todos os dados salvos\n"
            f"📈 `/stats` - Mostra estatísticas do banco de dados\n"
            f"🗑️ `/clear confirmar` - Deleta TODOS os dados (irreversível)\n"
            f"🗑️ `/delete` - Exclusão seletiva de tokens (por ID, nome, etc.)\n"
            f"🗑️ `/del <endereço>` - Deleta token por endereço de contrato\n"
            f"🎯 `/threshold <valor>` - Define threshold mínimo de similaridade\n"
            f"🔄 `/reset confirmar` - Limpa lista de contratos já exibidos\n"
            f"📋 `/cas` - Lista todos os contratos salvos\n"
            f"💾 `/backup` - Cria backup do banco de dados\n"
            f"🔄 `/restore` - Restaura banco de dados a partir de backup\n"
            f"🤖 `/ailinks` - Gerencia análise de IA dos social links\n"
            f"🆔 `/getid` - Mostra ID e informações do grupo atual\n"
            f"❓ `/help` - Mostra esta mensagem de ajuda\n\n"
            f"⚙️ **FUNCIONAMENTO:**\n\n"
            f"📤 **Grupo Database** ({Config.DATABASE_GROUP_ID}):\n"
            f"   • Envie mensagens de tokens para salvar no banco\n\n"
            f"🔍 **Grupo Comparison** ({Config.COMPARISON_GROUP_ID}):\n"
            f"   • Envie mensagens de tokens para comparar com o banco\n"
            f"   • Processa silenciosamente (sem respostas no grupo)\n"
            f"   • Envia notificações automaticamente para o grupo de notificação\n\n"
            f"🔔 **Grupo Notification** ({Config.NOTIFICATION_GROUP_ID}):\n"
            f"   • Recebe apenas notificações de similaridade\n"
            f"   • Não processa mensagens enviadas aqui\n"
            f"   • Local exclusivo para visualizar análises\n\n"
            f"💾 **Banco de Dados:**\n"
            f"   • Todos os dados são salvos permanentemente\n"
            f"   • Análise sofisticada de similaridade por seções\n"
            f"   • Formatação limpa sem emojis desnecessários\n"
            f"   • Sistema anti-duplicatas por endereço de contrato\n"
            f"   • Sistema de backup e restore completo\n\n"
            f"🔧 **Versão:** 3.14 - Formatação Mista Inteligente Implementada"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def get_group_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra o ID do grupo atual e informações relevantes"""
        if not update.message or not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = update.effective_chat.title or "N/A"
        
        # Determina o tipo de grupo baseado no ID configurado
        group_function = "🔍 Grupo não configurado"
        if str(chat_id) == Config.DATABASE_GROUP_ID:
            group_function = "📊 Grupo de Database (salva tokens)"
        elif str(chat_id) == Config.COMPARISON_GROUP_ID:
            group_function = "🔍 Grupo de Comparison (compara tokens)"
        elif str(chat_id) == Config.NOTIFICATION_GROUP_ID:
            group_function = "🔔 Grupo de Notification (recebe notificações)"
        
        message = f"""🆔 **INFORMAÇÕES DO CHAT**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **ID do Chat:** `{chat_id}`
📝 **Tipo:** {chat_type}
🏷️ **Título:** {chat_title}
⚙️ **Função:** {group_function}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 **Para configurar no .env:**
```
DATABASE_GROUP_ID={chat_id}
COMPARISON_GROUP_ID={chat_id}
NOTIFICATION_GROUP_ID={chat_id}
```
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para exclusão seletiva de tokens"""
        if not update.message:
            return
        
        # Verifica se foram fornecidos argumentos
        if not context.args:
            help_text = """🗑️ **EXCLUSÃO SELETIVA DE TOKENS**

📋 **Comandos disponíveis:**

`/delete id <número>` - Apaga token por ID específico
`/delete token <nome>` - Apaga token por nome
`/delete last` - Apaga o último token adicionado
`/delete list` - Lista tokens para seleção
`/delete range <id1> <id2>` - Apaga faixa de IDs

**Exemplos:**
• `/delete id 5` - Apaga o token com ID 5
• `/delete token MemeToken` - Apaga o token chamado MemeToken
• `/delete last` - Apaga o último token
• `/delete range 10 15` - Apaga tokens de ID 10 a 15
"""
            await update.message.reply_text(help_text, parse_mode='Markdown')
            return
        
        option = context.args[0].lower()
        
        if option == "id":
            await self._delete_by_id(update, context)
        elif option == "token":
            await self._delete_by_name(update, context)
        elif option == "last":
            await self._delete_last(update, context)
        elif option == "list":
            await self._show_tokens_list(update, context)
        elif option == "range":
            await self._delete_by_range(update, context)
        else:
            await update.message.reply_text(
                "❌ Opção inválida! Use `/delete` sem argumentos para ver as opções.",
                parse_mode='Markdown'
            )
    
    async def _delete_by_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apaga token por ID específico"""
        if not update.message or not context.args or len(context.args) < 2:
            if update.message:
                await update.message.reply_text("❌ Use: `/delete id <número>`", parse_mode='Markdown')
            return
        
        try:
            token_id = int(context.args[1])
            token_name = self.database.delete_token_by_id(token_id)
            
            if token_name:
                await update.message.reply_text(
                    f"✅ **Token deletado com sucesso!**\n"
                    f"🆔 ID: {token_id}\n"
                    f"📝 Nome: {token_name}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ Token com ID {token_id} não encontrado.",
                    parse_mode='Markdown'
                )
        except ValueError:
            await update.message.reply_text("❌ ID deve ser um número válido.", parse_mode='Markdown')
    
    async def _delete_by_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apaga token por nome"""
        if not update.message or not context.args or len(context.args) < 2:
            if update.message:
                await update.message.reply_text("❌ Use: `/delete token <nome>`", parse_mode='Markdown')
            return
        
        token_name = " ".join(context.args[1:])
        deleted_count = self.database.delete_token_by_name(token_name)
        
        if deleted_count > 0:
            await update.message.reply_text(
                f"✅ **Token(s) deletado(s) com sucesso!**\n"
                f"📝 Nome: {token_name}\n"
                f"🔢 Quantidade: {deleted_count}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Token com nome '{token_name}' não encontrado.",
                parse_mode='Markdown'
            )
    
    async def _delete_last(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apaga o último token adicionado"""
        if not update.message:
            return
            
        token_name = self.database.delete_last_token()
        
        if token_name:
            await update.message.reply_text(
                f"✅ **Último token deletado com sucesso!**\n"
                f"📝 Nome: {token_name}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Nenhum token encontrado no banco de dados.",
                parse_mode='Markdown'
            )
    
    async def _delete_by_range(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Apaga tokens em uma faixa de IDs"""
        if not update.message or not context.args or len(context.args) < 3:
            if update.message:
                await update.message.reply_text("❌ Use: `/delete range <id1> <id2>`", parse_mode='Markdown')
            return
        
        try:
            start_id = int(context.args[1])
            end_id = int(context.args[2])
            
            if start_id > end_id:
                await update.message.reply_text("❌ ID inicial deve ser menor que o final.", parse_mode='Markdown')
                return
            
            deleted_count, token_names = self.database.delete_tokens_by_range(start_id, end_id)
            
            if deleted_count > 0:
                tokens_text = ", ".join(token_names[:5])
                if len(token_names) > 5:
                    tokens_text += f" e mais {len(token_names) - 5}..."
                
                await update.message.reply_text(
                    f"✅ **{deleted_count} token(s) deletado(s) com sucesso!**\n"
                    f"📊 Faixa: ID {start_id} a {end_id}\n"
                    f"📝 Tokens: {tokens_text}",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ Nenhum token encontrado na faixa de ID {start_id} a {end_id}.",
                    parse_mode='Markdown'
                )
        except ValueError:
            await update.message.reply_text("❌ IDs devem ser números válidos.", parse_mode='Markdown')
    
    async def _show_tokens_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mostra lista de tokens para seleção"""
        if not update.message:
            return
            
        tokens = self.database.get_tokens_list(20)
        
        if not tokens:
            await update.message.reply_text(
                "❌ Nenhum token encontrado no banco de dados.",
                parse_mode='Markdown'
            )
            return
        
        message = "📋 **LISTA DE TOKENS DISPONÍVEIS**\n\n"
        for token in tokens:
            token_id, token_name, created_at = token
            message += f"• **ID {token_id}** - {token_name} ({created_at})\n"
        
        message += f"\n💡 **Para deletar:**\n"
        message += f"• `/delete id <número>` - Apagar por ID\n"
        message += f"• `/delete token <nome>` - Apagar por nome"
        
        await update.message.reply_text(message, parse_mode='Markdown')

    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para limpar contratos já exibidos"""
        if not update.message:
            return
        
        # Se não foram fornecidos argumentos, mostra informações
        if not context.args:
            count = self.database.get_displayed_contracts_count()
            await update.message.reply_text(
                f"🔄 **CONTRATOS JÁ EXIBIDOS**\n\n"
                f"📊 **Total atual:** {count} contratos\n\n"
                f"💡 **Para limpar:** `/reset confirmar`\n\n"
                f"ℹ️ **Nota:** Isso permitirá que tokens já exibidos apareçam novamente no grupo de comparação.",
                parse_mode='Markdown'
            )
            return
        
        # Verifica se foi confirmado
        if context.args[0].lower() == 'confirmar':
            count = self.database.clear_displayed_contracts()
            await update.message.reply_text(
                f"✅ **Reset realizado com sucesso!**\n\n"
                f"🗑️ **Contratos removidos:** {count}\n\n"
                f"ℹ️ **Agora todos os tokens poderão ser exibidos novamente** (se atenderem ao threshold).",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ **Comando incompleto!**\n\n"
                "✅ **Para confirmar:** `/reset confirmar`",
                parse_mode='Markdown'
            )

    async def threshold_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para definir o threshold mínimo de similaridade"""
        if not update.message:
            return
        
        # Se não foram fornecidos argumentos, mostra o valor atual
        if not context.args:
            current_threshold = self.database.get_min_similarity_threshold()
            await update.message.reply_text(
                f"🎯 **THRESHOLD DE SIMILARIDADE**\n\n"
                f"📊 **Valor atual:** {current_threshold:.1f}%\n\n"
                f"💡 **Para alterar:** `/threshold <valor>`\n"
                f"**Exemplo:** `/threshold 80.5`\n\n"
                f"ℹ️ **Nota:** Apenas tokens com similaridade igual ou superior a este valor serão exibidos no grupo de comparação.",
                parse_mode='Markdown'
            )
            return
        
        # Tenta converter o argumento para float
        try:
            new_threshold = float(context.args[0])
            
            # Valida o range (0 a 100)
            if new_threshold < 0 or new_threshold > 100:
                await update.message.reply_text(
                    "❌ **Valor inválido!**\n\n"
                    "📊 O threshold deve estar entre **0** e **100**.",
                    parse_mode='Markdown'
                )
                return
            
            # Salva o novo threshold
            old_threshold = self.database.get_min_similarity_threshold()
            self.database.set_min_similarity_threshold(new_threshold)
            
            await update.message.reply_text(
                f"✅ **Threshold atualizado com sucesso!**\n\n"
                f"📊 **Valor anterior:** {old_threshold:.1f}%\n"
                f"🎯 **Novo valor:** {new_threshold:.1f}%\n\n"
                f"ℹ️ **Agora apenas tokens com similaridade ≥ {new_threshold:.1f}% serão exibidos no grupo de comparação.**",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ **Formato inválido!**\n\n"
                "📊 Use apenas números decimais.\n"
                "**Exemplos válidos:** `70`, `85.5`, `90.2`",
                parse_mode='Markdown'
            )

    async def del_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para deletar token por endereço de contrato"""
        if not update.message:
            return
        
        # Verifica se foi fornecido endereço de contrato
        if not context.args:
            await update.message.reply_text(
                "❌ Use: `/del <endereço_contrato>`\n\n"
                "**Exemplo:**\n"
                "`/del U6Po1nXztih5YD3zRmn9zoTpx97tYrFKxEm137eX9C4`",
                parse_mode='Markdown'
            )
            return
        
        contract_address = context.args[0]
        
        # Valida formato básico do endereço
        if len(contract_address) < 40 or len(contract_address) > 50:
            await update.message.reply_text(
                "❌ Formato de endereço inválido. Deve ter entre 40-50 caracteres.",
                parse_mode='Markdown'
            )
            return
        
        # Verifica se o token existe antes de deletar
        token_info = self.database.get_token_by_contract_address(contract_address)
        
        if not token_info:
            await update.message.reply_text(
                f"❌ **Token não encontrado!**\n\n"
                f"📄 **Endereço:** `{contract_address}`\n\n"
                f"💡 Use `/delete list` para ver tokens disponíveis.",
                parse_mode='Markdown'
            )
            return
        
        # Deleta o token
        deleted_count, token_names = self.database.delete_token_by_contract_address(contract_address)
        
        if deleted_count > 0:
            token_names_text = ", ".join(token_names)
            await update.message.reply_text(
                f"✅ **{deleted_count} token(s) deletado(s) com sucesso!**\n\n"
                f"📄 **Endereço:** `{contract_address}`\n"
                f"📝 **Token(s):** {token_names_text}\n"
                f"🆔 **ID:** {token_info[0]}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Erro ao deletar token com endereço {contract_address}.",
                parse_mode='Markdown'
            )

    async def cas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para exibir todos os contratos salvos"""
        if not update.message:
            return
        
        try:
            # Busca todos os contratos salvos
            contracts = self.database.get_all_contracts()
            
            if not contracts:
                await update.message.reply_text(
                    "📭 **NENHUM CONTRATO ENCONTRADO**\n\n"
                    "Não há contratos salvos no banco de dados.",
                    parse_mode='Markdown'
                )
                return
            
            # Monta a mensagem com os contratos
            message_lines = []
            message_lines.append(f"📋 **CONTRATOS SALVOS ({len(contracts)})**")
            message_lines.append("=" * 40)
            message_lines.append("")
            
            for token_name, contract_address in contracts:
                message_lines.append(f"{token_name}")
                message_lines.append(f"└ `{contract_address}`")
                message_lines.append("")
            
            message_lines.append("=" * 40)
            message_lines.append(f"📊 **Total:** {len(contracts)} contratos")
            
            message_text = "\n".join(message_lines)
            
            # Verifica se a mensagem não é muito longa
            if len(message_text) > 4000:
                # Divide a mensagem em partes
                chunk_size = 3500
                chunks = []
                current_chunk = []
                current_length = 0
                
                header = f"📋 **CONTRATOS SALVOS ({len(contracts)})**\n" + "=" * 40 + "\n\n"
                
                for i, (token_name, contract_address) in enumerate(contracts):
                    line = f"{token_name}\n└ `{contract_address}`\n\n"
                    
                    if current_length + len(line) > chunk_size:
                        # Finaliza chunk atual
                        chunk_text = header + "".join(current_chunk) + f"--- Parte {len(chunks) + 1} ---"
                        chunks.append(chunk_text)
                        current_chunk = []
                        current_length = len(header)
                    
                    current_chunk.append(line)
                    current_length += len(line)
                
                # Adiciona último chunk
                if current_chunk:
                    chunk_text = header + "".join(current_chunk) + f"📊 **Total:** {len(contracts)} contratos"
                    chunks.append(chunk_text)
                
                # Envia as partes
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(chunk, parse_mode='Markdown')
                    
            else:
                await update.message.reply_text(message_text, parse_mode='Markdown')
            
            logger.info(f"Comando /cas executado: {len(contracts)} contratos listados")
            
        except Exception as e:
            logger.error(f"Erro ao executar comando /cas: {e}")
            await update.message.reply_text("❌ Erro ao buscar contratos do banco de dados.")

    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para criar backup do banco de dados"""
        if not update.message:
            return
        
        try:
            # Obtém informações do banco atual
            db_info = self.database.get_database_info()
            
            if not db_info.get('exists', False):
                await update.message.reply_text(
                    "❌ **Banco de dados não encontrado!**\n\n"
                    "💡 Não há dados para fazer backup.",
                    parse_mode='Markdown'
                )
                return
            
            # Cria o backup
            success, message = self.database.create_backup()
            
            if success:
                # Extrai o nome do arquivo da mensagem
                backup_filename = message.split(": ")[1].split(" (")[0]
                
                # Lê o arquivo de backup e envia como documento
                try:
                    with open(backup_filename, 'rb') as backup_file:
                        await update.message.reply_document(
                            document=backup_file,
                            filename=backup_filename,
                            caption=(
                                f"💾 **BACKUP DO BANCO DE DADOS**\n\n"
                                f"📊 **Tokens:** {db_info['tokens_count']}\n"
                                f"📁 **Tamanho:** {db_info['size']} bytes\n"
                                f"🕒 **Criado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                                f"✅ **Backup criado com sucesso!**\n"
                                f"💡 Use `/restore` para restaurar este backup."
                            ),
                            parse_mode='Markdown'
                        )
                    
                    # Remove o arquivo temporário após envio
                    import os
                    os.remove(backup_filename)
                    
                    logger.info(f"Backup criado e enviado: {backup_filename}")
                    
                except Exception as e:
                    await update.message.reply_text(
                        f"✅ Backup criado, mas erro ao enviar arquivo:\n{message}\n\n"
                        f"❌ Erro: {str(e)}",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    f"❌ **Erro ao criar backup:**\n\n{message}",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Erro no comando backup: {e}")
            await update.message.reply_text("❌ Erro interno ao criar backup do banco de dados.")

    async def restore_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para restaurar banco de dados a partir de backup"""
        if not update.message:
            return
        
        try:
            # Verifica se foi enviado um arquivo
            if not update.message.document:
                help_text = (
                    "💾 **RESTAURAR BANCO DE DADOS**\n\n"
                    "📋 **Como usar:**\n"
                    "1. Envie o comando `/restore` junto com um arquivo de backup\n"
                    "2. O arquivo deve ser um backup válido (.db)\n"
                    "3. O banco atual será substituído pelo backup\n\n"
                    "⚠️ **ATENÇÃO:**\n"
                    "• Esta operação substitui TODOS os dados atuais\n"
                    "• Um backup automático do banco atual será criado\n"
                    "• Esta operação NÃO PODE ser desfeita\n\n"
                    "📎 **Envie este comando junto com o arquivo de backup anexado.**"
                )
                await update.message.reply_text(help_text, parse_mode='Markdown')
                return
            
            document = update.message.document
            
            # Verifica se é um arquivo .db
            if not document.file_name or not document.file_name.endswith('.db'):
                await update.message.reply_text(
                    "❌ **Arquivo inválido!**\n\n"
                    "📄 Apenas arquivos com extensão `.db` são aceitos.",
                    parse_mode='Markdown'
                )
                return
            
            # Verifica tamanho do arquivo (máximo 20MB)
            if document.file_size and document.file_size > 20 * 1024 * 1024:
                await update.message.reply_text(
                    "❌ **Arquivo muito grande!**\n\n"
                    "📏 Tamanho máximo: 20MB\n"
                    f"📊 Arquivo enviado: {document.file_size / (1024*1024):.1f}MB",
                    parse_mode='Markdown'
                )
                return
            
            # Baixa o arquivo
            file = await context.bot.get_file(document.file_id)
            backup_path = f"temp_restore_{document.file_name}"
            await file.download_to_drive(backup_path)
            
            try:
                # Mostra informações do banco atual antes da restauração
                current_db_info = self.database.get_database_info()
                
                # Executa a restauração
                success, message = self.database.restore_from_backup(backup_path, create_current_backup=True)
                
                if success:
                    # Obtém informações do banco restaurado
                    new_db_info = self.database.get_database_info()
                    
                    await update.message.reply_text(
                        f"✅ **BANCO RESTAURADO COM SUCESSO!**\n\n"
                        f"📊 **Dados anteriores:**\n"
                        f"   • Tokens: {current_db_info.get('tokens_count', 0)}\n"
                        f"   • Tamanho: {current_db_info.get('size', 0)} bytes\n\n"
                        f"📊 **Dados restaurados:**\n"
                        f"   • Tokens: {new_db_info.get('tokens_count', 0)}\n"
                        f"   • Tamanho: {new_db_info.get('size', 0)} bytes\n\n"
                        f"💾 **Backup automático do banco anterior foi criado**\n\n"
                        f"🔄 **O bot agora está usando os dados restaurados.**",
                        parse_mode='Markdown'
                    )
                    
                    logger.info(f"Banco restaurado com sucesso a partir de: {document.file_name}")
                else:
                    await update.message.reply_text(
                        f"❌ **Erro ao restaurar backup:**\n\n{message}",
                        parse_mode='Markdown'
                    )
                    
            finally:
                # Remove arquivo temporário
                import os
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    
        except Exception as e:
            logger.error(f"Erro no comando restore: {e}")
            await update.message.reply_text("❌ Erro interno ao restaurar backup do banco de dados.")

    async def ailinks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando para gerenciar análise de IA dos social links"""
        if not update.message:
            return
        
        try:
            # Obtém argumentos do comando
            args = context.args
            
            if not args:
                # Mostra status atual
                ai_enabled = self.similarity_calculator.is_ai_links_enabled()
                ai_configured = bool(self.similarity_calculator.ai_link_analyzer.openai_api_key)
                
                status_emoji = "✅" if ai_enabled else "❌"
                config_emoji = "✅" if ai_configured else "❌"
                
                status_text = (
                    f"🤖 **ANÁLISE DE IA DOS SOCIAL LINKS**\n\n"
                    f"📊 **Status atual:**\n"
                    f"   {status_emoji} Análise de IA: {'HABILITADA' if ai_enabled else 'DESABILITADA'}\n"
                    f"   {config_emoji} OpenAI configurada: {'SIM' if ai_configured else 'NÃO'}\n\n"
                    f"💡 **Como usar:**\n"
                    f"   • `/ailinks on` - Habilita análise de IA\n"
                    f"   • `/ailinks off` - Desabilita análise de IA\n\n"
                    f"⚙️ **Configuração:**\n"
                    f"   Para habilitar, adicione OPENAI_API_KEY no arquivo .env\n\n"
                    f"🎯 **O que faz:**\n"
                    f"   Analisa automaticamente links do Twitter/X e outros\n"
                    f"   social links, fornecendo descrições inteligentes"
                )
                
                await update.message.reply_text(status_text, parse_mode='Markdown')
                return
            
            # Processa comando
            comando = args[0].lower()
            
            # Aliases para habilitar
            habilitar_aliases = ['on', 'ativar', 'habilitar', 'enable', '1', 'true', 'sim']
            # Aliases para desabilitar  
            desabilitar_aliases = ['off', 'desativar', 'desabilitar', 'disable', '0', 'false', 'nao', 'não']
            
            if comando in habilitar_aliases:
                # Verifica se OpenAI está configurada
                if not self.similarity_calculator.ai_link_analyzer.openai_api_key:
                    await update.message.reply_text(
                        "❌ **OpenAI API não configurada!**\n\n"
                        "🔧 **Para habilitar a análise de IA:**\n"
                        "1. Adicione OPENAI_API_KEY=sua_chave no arquivo .env\n"
                        "2. Reinicie o bot\n"
                        "3. Execute `/ailinks on` novamente\n\n"
                        "💡 **Obtenha sua chave em:** https://platform.openai.com/api-keys",
                        parse_mode='Markdown'
                    )
                    return
                
                self.similarity_calculator.set_ai_links_enabled(True)
                await update.message.reply_text(
                    "✅ **Análise de IA HABILITADA!**\n\n"
                    "🤖 Os social links agora serão analisados automaticamente\n"
                    "📝 Descrições inteligentes serão geradas para cada link\n\n"
                    "🎯 **Teste:** Envie um token com social links para ver o resultado!",
                    parse_mode='Markdown'
                )
                
            elif comando in desabilitar_aliases:
                self.similarity_calculator.set_ai_links_enabled(False)
                await update.message.reply_text(
                    "❌ **Análise de IA DESABILITADA**\n\n"
                    "📋 Os social links voltarão ao formato padrão\n"
                    "🔄 Para reabilitar, use `/ailinks on`",
                    parse_mode='Markdown'
                )
                
            else:
                await update.message.reply_text(
                    "❓ **Comando inválido!**\n\n"
                    "💡 **Comandos válidos:**\n"
                    "   • `/ailinks` - Mostra status\n"
                    "   • `/ailinks on` - Habilita análise\n"
                    "   • `/ailinks off` - Desabilita análise\n\n"
                    "📋 **Aliases aceitos:**\n"
                    "   • **Habilitar:** on, ativar, habilitar, enable\n"
                    "   • **Desabilitar:** off, desativar, desabilitar, disable",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.error(f"Erro no comando ailinks: {e}")
            await update.message.reply_text("❌ Erro interno no comando de análise de IA.")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manipula erros do bot"""
        logger.error(f"Erro no update {update}: {context.error}")

def main():
    """Função principal do bot"""
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN não configurado!")
        return
    
    if not Config.DATABASE_GROUP_ID or not Config.COMPARISON_GROUP_ID or not Config.NOTIFICATION_GROUP_ID:
        logger.error("IDs dos grupos não configurados!")
        return
    
    # Cria a aplicação do bot
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Cria instância do bot
    bot = SimilarityBot()
    
    # Adiciona handlers
    application.add_handler(CommandHandler("database", bot.database_command))
    application.add_handler(CommandHandler("clear", bot.clear_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("getid", bot.get_group_id))
    application.add_handler(CommandHandler("delete", bot.delete_command))
    application.add_handler(CommandHandler("del", bot.del_command)) # Adicionado handler para /del
    application.add_handler(CommandHandler("threshold", bot.threshold_command)) # Adicionado handler para /threshold
    application.add_handler(CommandHandler("reset", bot.reset_command)) # Adicionado handler para /reset
    application.add_handler(CommandHandler("cas", bot.cas_command)) # Adicionado handler para /cas
    application.add_handler(CommandHandler("backup", bot.backup_command)) # Adicionado handler para /backup
    application.add_handler(CommandHandler("restore", bot.restore_command)) # Adicionado handler para /restore
    application.add_handler(CommandHandler("ailinks", bot.ailinks_command)) # Adicionado handler para /ailinks
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        bot.handle_message
    ))
    
    # Inicia o bot
    logger.info("🤖 Bot de Similaridade iniciado!")
    logger.info(f"📊 Grupo de banco de dados: {Config.DATABASE_GROUP_ID}")
    logger.info(f"🔍 Grupo de comparação: {Config.COMPARISON_GROUP_ID}")
    logger.info(f"🔔 Grupo de notificação: {Config.NOTIFICATION_GROUP_ID}")
    logger.info("📝 Formato: Monospace ativado")
    logger.info("🔧 Comandos disponíveis: /database, /stats, /clear, /delete, /del, /threshold, /reset, /cas, /backup, /restore, /getid, /help")
    
    application.run_polling()

if __name__ == '__main__':
    main() 