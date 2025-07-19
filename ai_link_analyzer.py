import re
import requests
import logging
from typing import Dict, List, Optional
from config import Config
import asyncio
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class AILinkAnalyzer:
    """Classe para análise de links usando IA (OpenAI)"""
    
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        self.enabled = bool(self.openai_api_key)
        
        if not self.enabled:
            logger.warning("⚠️ OpenAI API key não configurada - análise de links desabilitada")
            logger.info("💡 Adicione OPENAI_API_KEY=sua_chave_aqui no arquivo .env para habilitar")
    
    def extract_social_links(self, social_links_text: str) -> List[Dict[str, str]]:
        """Extrai todos os links da seção Social Links"""
        links = []
        
        # Padrão para encontrar links HTML: <a href="url">texto</a>
        html_links = re.findall(r'<a href="([^"]+)">[^<]*</a>', social_links_text)
        
        # Padrão para encontrar URLs em parênteses: (url)
        parentheses_links = re.findall(r'\((https?://[^)]+)\)', social_links_text)
        
        # Padrão para encontrar URLs soltas
        loose_links = re.findall(r'(https?://[^\s<>()]+)', social_links_text)
        
        # Combina todos os links únicos
        all_links = list(set(html_links + parentheses_links + loose_links))
        
        for url in all_links:
            # Identifica o tipo de link baseado na URL
            link_type = self._identify_link_type(url)
            links.append({
                'url': url,
                'type': link_type,
                'description': ''
            })
        
        return links
    
    def _identify_link_type(self, url: str) -> str:
        """Identifica o tipo de link baseado na URL"""
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()
        
        if 'twitter.com' in domain or 'x.com' in domain:
            if '/communities/' in url_lower:
                return 'Twitter Community'
            elif '/status/' in url_lower:
                return 'Twitter Post'
            else:
                return 'Twitter Profile'
        elif 't.me' in domain:
            return 'Telegram'
        elif 't.co' in domain:
            return 'Shortened Link'
        elif 'axiom.trade' in domain:
            return 'Axiom Trading'
        elif any(word in domain for word in ['website', 'site', 'www']):
            return 'Website'
        elif any(ext in domain for ext in ['.com', '.org', '.net', '.io', '.co', '.info', '.news']):
            # Identifica websites comuns por extensão de domínio
            return 'Website'
        else:
            return 'Link'
    
    async def analyze_links_with_ai(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Analisa os links usando OpenAI e retorna descrições, excluindo links do Axiom"""
        if not self.enabled:
            logger.info("🤖 Análise de IA desabilitada - retornando tipos básicos")
            return links
        
        try:
            analyzed_links = []
            
            for link_info in links:
                url = link_info['url']
                link_type = link_info['type']
                
                # Verifica se é link do Axiom - se for, mantém formato padrão
                if 'axiom.trade' in url.lower() or link_type == 'Axiom Trading':
                    logger.info(f"🚫 Link do Axiom excluído da análise de IA: {url}")
                    analyzed_links.append({
                        'url': url,
                        'type': link_type,
                        'description': f"Link do tipo {link_type}"  # Formato padrão
                    })
                    continue
                
                try:
                    # Faz análise com OpenAI apenas para links não-Axiom
                    description = await self._analyze_single_link(url, link_type)
                    
                    analyzed_links.append({
                        'url': url,
                        'type': link_type,
                        'description': description
                    })
                    
                    # Pequena pausa para evitar rate limiting
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ Erro analisando link {url}: {e}")
                    # Fallback para tipo básico
                    analyzed_links.append({
                        'url': url,
                        'type': link_type,
                        'description': f"Link do tipo {link_type}"
                    })
            
            return analyzed_links
            
        except ImportError:
            logger.error("❌ Biblioteca openai não instalada. Execute: pip install openai")
            return links
        except Exception as e:
            logger.error(f"❌ Erro na análise de IA: {e}")
            return links
    
    async def _analyze_single_link(self, url: str, link_type: str) -> str:
        """Analisa um único link usando OpenAI"""
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.openai_api_key)
            
            # Prompt otimizado para análise de links de tokens/cripto
            prompt = f"""
Analise este link relacionado a um token de criptomoeda e forneça uma descrição concisa em português:

URL: {url}
Tipo identificado: {link_type}

Instruções:
- Responda em português brasileiro
- Máximo 50 palavras
- Foque no propósito/conteúdo do link
- Se for rede social, mencione o tipo de conteúdo
- Se for ferramenta/plataforma, explique sua função
- Use linguagem simples e direta

Descrição:"""

            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de links de projetos de criptomoedas. Forneça descrições concisas e úteis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            description = content.strip() if content else f"Link do tipo {link_type}"
            return description
            
        except Exception as e:
            logger.error(f"❌ Erro na análise OpenAI para {url}: {e}")
            return f"Link do tipo {link_type}"
    
    def _sanitize_html_content(self, text: str) -> str:
        """Sanitiza texto para uso seguro em HTML"""
        if not text:
            return ""
        
        # Remove caracteres problemáticos e limpa o texto
        text = text.strip()
        # Escapa caracteres HTML básicos mas preserva funcionalidade
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
    
    def _validate_url(self, url: str) -> str:
        """Valida e limpa URL para uso em href"""
        if not url:
            return "#"
        
        url = url.strip()
        
        # Garante que URL tem protocolo
        if not url.startswith(('http://', 'https://', 'ftp://')):
            if 't.me' in url or 'telegram' in url.lower():
                url = f"https://{url}"
            elif url.startswith('www.'):
                url = f"https://{url}"
            elif '.' in url:
                url = f"https://{url}"
        
        # Remove caracteres problemáticos
        url = url.replace('"', '%22')
        url = url.replace("'", '%27')
        url = url.replace(' ', '%20')
        
        return url
    
    def format_analyzed_links(self, links: List[Dict[str, str]]) -> str:
        """Formata os links analisados para exibição com sanitização HTML"""
        if not links:
            return ""
        
        # Verifica se há links analisados pela IA (não-Axiom)
        has_ai_analyzed = any(
            link_info.get('description', '') != f"Link do tipo {link_info.get('type', '')}" and 
            'axiom.trade' not in link_info.get('url', '').lower() and
            link_info.get('type', '') != 'Axiom Trading'
            for link_info in links
        )
        
        # Define o cabeçalho baseado se tem análise de IA ou não
        if has_ai_analyzed:
            formatted_lines = ["🌐 Social Links (Análise IA):"]
        else:
            formatted_lines = ["🌐 Social Links:"]
        
        for i, link_info in enumerate(links):
            url = self._validate_url(link_info.get('url', ''))
            link_type = self._sanitize_html_content(link_info.get('type', 'Link'))
            description = self._sanitize_html_content(link_info.get('description', ''))
            
            # Caractere de árvore
            tree_char = "└" if i == len(links) - 1 else "├"
            
            # Valida se temos dados válidos
            if not url or url == "#" or not link_type:
                continue
                
            # Formata a linha com link clicável e descrição
            # Usa URL direta que o Telegram detecta automaticamente como link
            line = f"{tree_char} {link_type} ({url})"
            
            # Adiciona descrição apenas se for análise de IA (não para Axiom)
            is_axiom_link = 'axiom.trade' in url.lower() or link_type == 'Axiom Trading'
            has_real_description = description and description != f"Link do tipo {link_type}" and len(description) > 3
            
            if has_real_description and not is_axiom_link:
                line += f" - {description}"
            
            formatted_lines.append(line)
        
        return "\n".join(formatted_lines)
    
    async def analyze_social_links_section(self, social_links_text: str) -> str:
        """Método principal para analisar uma seção completa de Social Links"""
        if not social_links_text:
            return ""
        
        try:
            # 1. Extrai os links da seção
            links = self.extract_social_links(social_links_text)
            
            if not links:
                logger.info("📋 Nenhum link encontrado na seção Social Links")
                return social_links_text
            
            logger.info(f"🔍 Encontrados {len(links)} links para análise")
            
            # 2. Analisa com IA (se habilitado)
            analyzed_links = await self.analyze_links_with_ai(links)
            
            # 3. Formata para exibição
            formatted_result = self.format_analyzed_links(analyzed_links)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"❌ Erro na análise completa de Social Links: {e}")
            return social_links_text  # Retorna texto original em caso de erro 