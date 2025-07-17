import json
import re
from typing import Dict, List, Any, Tuple, Optional

class SimilarityCalculator:
    def __init__(self):
        # Agrupamento de campos por seção
        self.section_fields = {
            'market_overview': ['market_cap', 'price_change', 'traders', 'buy_volume', 'sell_volume', 
                               'buy_count', 'sell_count', 'buyers', 'sellers'],


            'wallet_insights': ['holders_totais', 'smart_wallets', 'fresh_wallets', 'renowned_wallets',
                               'creator_wallets', 'sniper_wallets', 'rat_traders', 'whale_wallets',
                               'top_wallets', 'following_wallets', 'bluechip_holders', 'bundler_wallets'],
            'risk_metrics': ['bluechip_holders_percentage', 'rat_trader_supply_percentage', 
                            'bundler_supply_percentage', 'entrapment_supply_percentage', 
                            'degen_calls', 'sinais_tecnicos'],
            'top_holders': ['top_holders_percentage', 'top1_holder_percentage', 'top5_holders_percentage', 
                           'top10_holders_percentage', 'holders_concentration_ratio', 'holders_distribution_score',
                           'top_holders_sol_total', 'top5_holders_sol_total', 'top1_holder_sol_amount',
                           'holders_sol_distribution_score', 'holders_sol_concentration_ratio'],
            'source_wallets': ['source_wallets_percentage', 'source_wallets_count', 'source_wallets_avg_hops']
        }
        
        # Padrões para identificar seções na mensagem
        self.section_patterns = {
            'market_overview': r'📊 Market Overview',


            'wallet_insights': r'📊 Wallet Insights',
            'risk_metrics': r'📈 Risk Metrics',
            'top_holders': r'📊.*?Top 10 Holders',
            'source_wallets': r'🔍 Source Wallets'
        }
    
    def calculate_field_similarity(self, value1, value2) -> float:
        """Calcula similaridade entre dois valores (numéricos ou strings) (0-100%)"""
        if value1 is None and value2 is None:
            return 100.0
        
        if value1 is None or value2 is None:
            return 0.0
        
        # Para strings, compara igualdade exata
        if isinstance(value1, str) or isinstance(value2, str):
            if str(value1).lower() == str(value2).lower():
                return 100.0
            else:
                return 0.0
        
        # Para valores numéricos
        if value1 == 0 and value2 == 0:
            return 100.0
        
        if value1 == 0 or value2 == 0:
            return 0.0
        
        # Calcula similaridade baseada na proximidade dos valores
        max_val = max(abs(value1), abs(value2))
        min_val = min(abs(value1), abs(value2))
        
        similarity = (min_val / max_val) * 100
        return similarity
    
    def calculate_section_similarity(self, token1: Dict[str, Any], token2: Dict[str, Any], section_name: str) -> float:
        """Calcula similaridade média para uma seção específica"""
        if section_name not in self.section_fields:
            return 0.0
        
        fields = self.section_fields[section_name]
        similarities = []
        
        # Para Top Holders, usa algoritmo sofisticado com pesos
        if section_name == 'top_holders':
            return self._calculate_holders_similarity(token1, token2)
        
        # Para Source Wallets, usa algoritmo com pesos
        if section_name == 'source_wallets':
            return self._calculate_source_wallets_similarity(token1, token2)
        
        # Para outras seções, usa algoritmo padrão
        for field in fields:
            value1 = token1.get(field)
            value2 = token2.get(field)
            
            # Só inclui no cálculo se pelo menos um dos valores existir
            if value1 is not None or value2 is not None:
                field_sim = self.calculate_field_similarity(value1, value2)
                similarities.append(field_sim)
        
        # Retorna a média das similaridades da seção
        if similarities:
            return sum(similarities) / len(similarities)
        else:
            return 0.0
    
    def _calculate_holders_similarity(self, token1: Dict[str, Any], token2: Dict[str, Any]) -> float:
        """Algoritmo sofisticado para calcular similaridade dos Top 10 Holders (com análise de SOL)"""
        
        # Pesos para diferentes aspectos da análise (expandido com métricas de SOL)
        weights = {
            'total_pct_weight': 15,          # Porcentagem total dos top 10
            'concentration_pct_weight': 20,  # Concentração do top 1 (%)
            'oligopoly_pct_weight': 15,      # Top 5 holders (%)
            'distribution_pct_weight': 15,   # Score de distribuição (%)
            'sol_total_weight': 10,          # Total de SOL dos holders
            'sol_concentration_weight': 15,  # Concentração de SOL do top 1
            'sol_distribution_weight': 10    # Distribuição de SOL
        }
        
        similarities = []
        
        # === MÉTRICAS DE PORCENTAGEM (65% do peso total) ===
        
        # 1. Similaridade do total (peso 15%)
        total1 = token1.get('top_holders_percentage')
        total2 = token2.get('top_holders_percentage')
        if total1 is not None and total2 is not None:
            total_sim = self.calculate_field_similarity(total1, total2)
            similarities.append(total_sim * weights['total_pct_weight'] / 100)
        
        # 2. Similaridade da concentração do top 1 holder (peso 20%)
        top1_1 = token1.get('top1_holder_percentage')
        top1_2 = token2.get('top1_holder_percentage')
        if top1_1 is not None and top1_2 is not None:
            concentration_sim = self.calculate_field_similarity(top1_1, top1_2)
            similarities.append(concentration_sim * weights['concentration_pct_weight'] / 100)
        
        # 3. Similaridade do oligopólio (top 5) (peso 15%)
        top5_1 = token1.get('top5_holders_percentage')
        top5_2 = token2.get('top5_holders_percentage')
        if top5_1 is not None and top5_2 is not None:
            oligopoly_sim = self.calculate_field_similarity(top5_1, top5_2)
            similarities.append(oligopoly_sim * weights['oligopoly_pct_weight'] / 100)
        
        # 4. Similaridade da distribuição (peso 15%)
        dist1 = token1.get('holders_distribution_score')
        dist2 = token2.get('holders_distribution_score')
        if dist1 is not None and dist2 is not None:
            distribution_sim = self.calculate_field_similarity(dist1, dist2)
            similarities.append(distribution_sim * weights['distribution_pct_weight'] / 100)
        
        # === MÉTRICAS DE SOL (35% do peso total) ===
        
        # 5. Similaridade do total de SOL (peso 10%)
        sol_total1 = token1.get('top_holders_sol_total')
        sol_total2 = token2.get('top_holders_sol_total')
        if sol_total1 is not None and sol_total2 is not None:
            sol_total_sim = self.calculate_field_similarity(sol_total1, sol_total2)
            similarities.append(sol_total_sim * weights['sol_total_weight'] / 100)
        
        # 6. Similaridade da concentração de SOL do top 1 (peso 15%)
        sol_conc1 = token1.get('holders_sol_concentration_ratio')
        sol_conc2 = token2.get('holders_sol_concentration_ratio')
        if sol_conc1 is not None and sol_conc2 is not None:
            sol_conc_sim = self.calculate_field_similarity(sol_conc1, sol_conc2)
            similarities.append(sol_conc_sim * weights['sol_concentration_weight'] / 100)
        
        # 7. Similaridade da distribuição de SOL (peso 10%)
        sol_dist1 = token1.get('holders_sol_distribution_score')
        sol_dist2 = token2.get('holders_sol_distribution_score')
        if sol_dist1 is not None and sol_dist2 is not None:
            sol_dist_sim = self.calculate_field_similarity(sol_dist1, sol_dist2)
            similarities.append(sol_dist_sim * weights['sol_distribution_weight'] / 100)
        
        # Retorna a média ponderada
        if similarities:
            return sum(similarities)
        else:
            return 0.0
    
    def _calculate_source_wallets_similarity(self, token1: Dict[str, Any], token2: Dict[str, Any]) -> float:
        """Algoritmo para calcular similaridade dos Source Wallets"""
        
        # Pesos para diferentes aspectos da análise
        weights = {
            'percentage_weight': 50,  # Porcentagem total (mais importante)
            'count_weight': 25,       # Quantidade de wallets
            'hops_weight': 25         # Média de hops
        }
        
        similarities = []
        
        # 1. Similaridade da porcentagem total (peso 50%)
        pct1 = token1.get('source_wallets_percentage')
        pct2 = token2.get('source_wallets_percentage')
        if pct1 is not None and pct2 is not None:
            pct_sim = self.calculate_field_similarity(pct1, pct2)
            similarities.append(pct_sim * weights['percentage_weight'] / 100)
        
        # 2. Similaridade da quantidade de wallets (peso 25%)
        count1 = token1.get('source_wallets_count')
        count2 = token2.get('source_wallets_count')
        if count1 is not None and count2 is not None:
            count_sim = self.calculate_field_similarity(count1, count2)
            similarities.append(count_sim * weights['count_weight'] / 100)
        
        # 3. Similaridade da média de hops (peso 25%)
        hops1 = token1.get('source_wallets_avg_hops')
        hops2 = token2.get('source_wallets_avg_hops')
        if hops1 is not None and hops2 is not None:
            hops_sim = self.calculate_field_similarity(hops1, hops2)
            similarities.append(hops_sim * weights['hops_weight'] / 100)
        
        # Retorna a média ponderada
        if similarities:
            return sum(similarities)
        else:
            return 0.0
    
    def calculate_overall_similarity(self, token1: Dict[str, Any], token2: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calcula similaridade geral e por seção"""
        section_similarities = {}
        total_similarity = 0.0
        valid_sections = 0
        
        for section_name in self.section_fields.keys():
            section_sim = self.calculate_section_similarity(token1, token2, section_name)
            # Inclui todas as seções no dicionário, mesmo com 0.0%
            section_similarities[section_name] = section_sim
            if section_sim > 0:  # Só conta seções > 0 para a média geral
                total_similarity += section_sim
                valid_sections += 1
        
        # Calcula similaridade geral como média das seções
        overall_similarity = total_similarity / valid_sections if valid_sections > 0 else 0.0
        
        return overall_similarity, section_similarities
    
    def find_most_similar_token(self, target_token: Dict[str, Any], database_tokens: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float, Dict[str, float]]:
        """Encontra o token mais similar no banco de dados"""
        if not database_tokens:
            return None, 0.0, {}
        
        best_match = None
        best_similarity = 0.0
        best_section_similarities = {}
        
        for db_token in database_tokens:
            similarity, section_sims = self.calculate_overall_similarity(target_token, db_token)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = db_token
                best_section_similarities = section_sims
        
        return best_match, best_similarity, best_section_similarities
    
    def _clean_emojis_from_message(self, message: str) -> str:
        """Remove emojis específicos da mensagem"""
        # Remove os emojis 🟣👀🟢 
        emojis_to_remove = ['🟣', '👀🟢', '👀', '🟢']
        cleaned_message = message
        
        for emoji in emojis_to_remove:
            cleaned_message = cleaned_message.replace(emoji, '')
        
        # Remove apenas espaços extras no final das linhas, preservando quebras de linha
        lines = cleaned_message.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove espaços extras dentro da linha, mas preserva a estrutura
            cleaned_line = re.sub(r' +', ' ', line.strip())
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def insert_similarities_in_message(self, original_message: str, section_similarities: Dict[str, float]) -> str:
        """Insere linhas de similaridade na mensagem original após cada seção"""
        if not original_message:
            return "❌ Mensagem original não encontrada no banco de dados."
        
        # Limpa emojis indesejados da mensagem
        cleaned_message = self._clean_emojis_from_message(original_message)
        
        lines = cleaned_message.split('\n')
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            result_lines.append(line)
            
            # Verifica se esta linha marca o início de uma seção
            section_found = None
            similarity_pct = 0
            
            for section_name, pattern in self.section_patterns.items():
                if re.search(pattern, line):
                    section_found = section_name
                    similarity_pct = section_similarities.get(section_name, 30)  # Default 30% se não calculado
                    break
            
            if section_found:
                # Encontra o final desta seção
                section_end = i + 1
                while section_end < len(lines):
                    next_line = lines[section_end]
                    
                    # Para se encontrar linha vazia ou início de nova seção com emoji
                    if (next_line.strip() == '' or 
                        any(re.search(pattern, next_line) for pattern in self.section_patterns.values())):
                        break
                    
                    result_lines.append(next_line)
                    section_end += 1
                
                # Insere linha de similaridade após a seção
                result_lines.append(f"========================> 🎯Similaridade: {similarity_pct:.0f}%")
                
                # Adiciona linha vazia se a próxima linha não for vazia
                if section_end < len(lines) and lines[section_end].strip() != '':
                    result_lines.append("")
                
                i = section_end
            else:
                i += 1
        
        return '\n'.join(result_lines)
    
    def extract_formatted_data(self, token_data: Dict[str, Any], raw_message: Optional[str] = None) -> Dict[str, str]:
        """Extrai dados formatados para comparação lado a lado"""
        formatted_data = {}
        
        # Market Overview
        formatted_data['market_cap'] = self._format_currency(token_data.get('market_cap'))
        formatted_data['buy_volume'] = self._format_currency(token_data.get('buy_volume'))
        formatted_data['sell_volume'] = self._format_currency(token_data.get('sell_volume'))
        formatted_data['price_change'] = self._format_percentage(token_data.get('price_change'))
        formatted_data['traders'] = self._format_number(token_data.get('traders'))
        formatted_data['buy_count'] = self._format_number(token_data.get('buy_count'))
        formatted_data['sell_count'] = self._format_number(token_data.get('sell_count'))
        formatted_data['buyers'] = self._format_number(token_data.get('buyers'))
        formatted_data['sellers'] = self._format_number(token_data.get('sellers'))
        

        
        # Wallet Insights
        formatted_data['holders_totais'] = self._format_number(token_data.get('holders_totais'))
        formatted_data['smart_wallets'] = self._format_number(token_data.get('smart_wallets'))
        formatted_data['fresh_wallets'] = self._format_number(token_data.get('fresh_wallets'))
        formatted_data['renowned_wallets'] = self._format_number(token_data.get('renowned_wallets'))
        formatted_data['creator_wallets'] = self._format_number(token_data.get('creator_wallets'))
        formatted_data['sniper_wallets'] = self._format_number(token_data.get('sniper_wallets'))
        formatted_data['rat_traders'] = self._format_number(token_data.get('rat_traders'))
        formatted_data['whale_wallets'] = self._format_number(token_data.get('whale_wallets'))
        formatted_data['top_wallets'] = self._format_number(token_data.get('top_wallets'))
        formatted_data['following_wallets'] = self._format_number(token_data.get('following_wallets'))
        formatted_data['bluechip_holders'] = self._format_number(token_data.get('bluechip_holders'))
        formatted_data['bundler_wallets'] = self._format_number(token_data.get('bundler_wallets'))
        
        # Risk Metrics
        formatted_data['bluechip_holders_percentage'] = self._format_percentage(token_data.get('bluechip_holders_percentage'))
        formatted_data['rat_trader_supply_percentage'] = self._format_percentage(token_data.get('rat_trader_supply_percentage'))
        formatted_data['bundler_supply_percentage'] = self._format_percentage(token_data.get('bundler_supply_percentage'))
        formatted_data['degen_calls'] = self._format_number(token_data.get('degen_calls'))
        
        # Top Holders
        formatted_data['top_holders_percentage'] = self._format_percentage(token_data.get('top_holders_percentage'))
        formatted_data['top1_holder_percentage'] = self._format_percentage(token_data.get('top1_holder_percentage'))
        formatted_data['top5_holders_percentage'] = self._format_percentage(token_data.get('top5_holders_percentage'))
        
        # Source Wallets
        formatted_data['source_wallets_percentage'] = self._format_percentage(token_data.get('source_wallets_percentage'))
        formatted_data['source_wallets_count'] = self._format_number(token_data.get('source_wallets_count'))
        formatted_data['source_wallets_avg_hops'] = self._format_decimal(token_data.get('source_wallets_avg_hops'))
        
        return formatted_data
    
    def _format_currency(self, value) -> str:
        """Formata valores monetários"""
        if value is None:
            return "N/A"
        if value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        else:
            return f"${value:.2f}"
    
    def _format_percentage(self, value) -> str:
        """Formata porcentagens"""
        if value is None:
            return "N/A"
        if value >= 0:
            return f"+{value:.2f}%"
        else:
            return f"{value:.2f}%"
    
    def _format_number(self, value) -> str:
        """Formata números inteiros"""
        if value is None:
            return "N/A"
        return f"{value:,}"
    
    def _format_decimal(self, value) -> str:
        """Formata números decimais"""
        if value is None:
            return "N/A"
        return f"{value:.1f}"
    
    def create_side_by_side_comparison(self, current_token_data: Dict[str, Any], similar_token_data: Dict[str, Any], 
                                     section_similarities: Dict[str, float]) -> str:
        """Cria comparação lado a lado com formatação mono-espaçada (estilo terminal)"""
        
        # Extrai dados formatados
        current_formatted = self.extract_formatted_data(current_token_data)
        similar_formatted = self.extract_formatted_data(similar_token_data)
        
        # Nomes dos tokens para cabeçalho
        current_token_name = current_token_data.get('token_name', 'Token Atual')
        similar_token_name = similar_token_data.get('token_name', 'Token BD')
        
        comparison_lines = []
        
        # Filtra seções com similaridade > 30% para evitar mensagens muito longas
        MIN_SECTION_SIMILARITY = 30.0
        
        # Market Overview
        if section_similarities.get('market_overview', 0) > MIN_SECTION_SIMILARITY:
            comparison_lines.append("Market Overview:")
            comparison_lines.append(f"├ Market Cap:         {current_formatted['market_cap']:>8} | {similar_formatted['market_cap']:>8}")
            comparison_lines.append(f"├ Buy Volume:         {current_formatted['buy_volume']:>8} | {similar_formatted['buy_volume']:>8}")
            comparison_lines.append(f"├ Sell Volume:        {current_formatted['sell_volume']:>8} | {similar_formatted['sell_volume']:>8}")
            comparison_lines.append(f"├ Price%:             {current_formatted['price_change']:>8} | {similar_formatted['price_change']:>8}")
            comparison_lines.append(f"├ Traders:            {current_formatted['traders']:>8} | {similar_formatted['traders']:>8}")
            comparison_lines.append(f"├ Buy Count:          {current_formatted['buy_count']:>8} | {similar_formatted['buy_count']:>8}")
            comparison_lines.append(f"├ Sell Count:         {current_formatted['sell_count']:>8} | {similar_formatted['sell_count']:>8}")
            comparison_lines.append(f"├ Buyers:             {current_formatted['buyers']:>8} | {similar_formatted['buyers']:>8}")
            comparison_lines.append(f"└ Sellers:            {current_formatted['sellers']:>8} | {similar_formatted['sellers']:>8}")
            comparison_lines.append(f"========================> 🎯Similaridade: {section_similarities.get('market_overview', 0):.0f}%")
            comparison_lines.append("")
        

        
        # Wallet Insights
        if section_similarities.get('wallet_insights', 0) > MIN_SECTION_SIMILARITY:
            comparison_lines.append("Wallet Insights:")
            comparison_lines.append(f"├ Holders Totais:     {current_formatted['holders_totais']:>8} | {similar_formatted['holders_totais']:>8}")
            comparison_lines.append(f"├ Smart Wallets:      {current_formatted['smart_wallets']:>8} | {similar_formatted['smart_wallets']:>8}")
            comparison_lines.append(f"├ Fresh Wallets:      {current_formatted['fresh_wallets']:>8} | {similar_formatted['fresh_wallets']:>8}")
            comparison_lines.append(f"├ Renowned Wallets:   {current_formatted['renowned_wallets']:>8} | {similar_formatted['renowned_wallets']:>8}")
            comparison_lines.append(f"├ Creator Wallets:    {current_formatted['creator_wallets']:>8} | {similar_formatted['creator_wallets']:>8}")
            comparison_lines.append(f"├ Sniper Wallets:     {current_formatted['sniper_wallets']:>8} | {similar_formatted['sniper_wallets']:>8}")
            comparison_lines.append(f"├ Rat Traders:        {current_formatted['rat_traders']:>8} | {similar_formatted['rat_traders']:>8}")
            comparison_lines.append(f"├ Whale Wallets:      {current_formatted['whale_wallets']:>8} | {similar_formatted['whale_wallets']:>8}")
            comparison_lines.append(f"├ Top Wallets:        {current_formatted['top_wallets']:>8} | {similar_formatted['top_wallets']:>8}")
            comparison_lines.append(f"├ Following Wallets:  {current_formatted['following_wallets']:>8} | {similar_formatted['following_wallets']:>8}")
            comparison_lines.append(f"├ Bluechip Holders:   {current_formatted['bluechip_holders']:>8} | {similar_formatted['bluechip_holders']:>8}")
            comparison_lines.append(f"└ Bundler Wallets:    {current_formatted['bundler_wallets']:>8} | {similar_formatted['bundler_wallets']:>8}")
            comparison_lines.append(f"========================> 🎯Similaridade: {section_similarities.get('wallet_insights', 0):.0f}%")
            comparison_lines.append("")
        
        # Risk Metrics
        if section_similarities.get('risk_metrics', 0) > MIN_SECTION_SIMILARITY:
            comparison_lines.append("Risk Metrics:")
            comparison_lines.append(f"├ Bluechip Holders:   {current_formatted['bluechip_holders_percentage']:>8} | {similar_formatted['bluechip_holders_percentage']:>8}")
            comparison_lines.append(f"├ Rat Trader Supply:  {current_formatted['rat_trader_supply_percentage']:>8} | {similar_formatted['rat_trader_supply_percentage']:>8}")
            comparison_lines.append(f"└ Bundler Supply:     {current_formatted['bundler_supply_percentage']:>8} | {similar_formatted['bundler_supply_percentage']:>8}")
            comparison_lines.append(f"========================> 🎯Similaridade: {section_similarities.get('risk_metrics', 0):.0f}%")
            comparison_lines.append("")
        
        # Top Holders
        if section_similarities.get('top_holders', 0) > MIN_SECTION_SIMILARITY:
            comparison_lines.append("Top 10 Holders:")
            comparison_lines.append(f"├ Top 10 Total:       {current_formatted['top_holders_percentage']:>8} | {similar_formatted['top_holders_percentage']:>8}")
            comparison_lines.append(f"├ Top 1 Holder:       {current_formatted['top1_holder_percentage']:>8} | {similar_formatted['top1_holder_percentage']:>8}")
            comparison_lines.append(f"└ Top 5 Holders:      {current_formatted['top5_holders_percentage']:>8} | {similar_formatted['top5_holders_percentage']:>8}")
            comparison_lines.append(f"========================> 🎯Similaridade: {section_similarities.get('top_holders', 0):.0f}%")
            comparison_lines.append("")
        
        # Source Wallets
        if section_similarities.get('source_wallets', 0) > MIN_SECTION_SIMILARITY:
            comparison_lines.append("Source Wallets:")
            comparison_lines.append(f"├ Percentage:         {current_formatted['source_wallets_percentage']:>8} | {similar_formatted['source_wallets_percentage']:>8}")
            comparison_lines.append(f"├ Count:              {current_formatted['source_wallets_count']:>8} | {similar_formatted['source_wallets_count']:>8}")
            comparison_lines.append(f"└ Avg Hops:           {current_formatted['source_wallets_avg_hops']:>8} | {similar_formatted['source_wallets_avg_hops']:>8}")
            comparison_lines.append(f"========================> 🎯Similaridade: {section_similarities.get('source_wallets', 0):.0f}%")
            comparison_lines.append("")
        
        # Se não há seções com similaridade > 30%, exibe resumo básico
        if not comparison_lines:
            comparison_lines.append("RESUMO RÁPIDO:")
            comparison_lines.append(f"├ Similaridade Geral: {max(section_similarities.values(), default=0):.1f}%")
            comparison_lines.append(f"└ Nenhuma seção com similaridade > {MIN_SECTION_SIMILARITY}%")
            comparison_lines.append("")
        
        return '\n'.join(comparison_lines)
    
    def create_enhanced_message(self, target_token_name: str, most_similar_token: Optional[Dict[str, Any]], 
                               similarity: float, section_similarities: Dict[str, float], 
                               current_message: Optional[str] = None, contract_address: Optional[str] = None) -> str:
        """Cria a mensagem final com formatação mono-espaçada (estilo terminal)"""
        if not most_similar_token:
            ca_info = f"\nCA: `{contract_address}`" if contract_address else ""
            return f"Token: {target_token_name}{ca_info}\n\nNenhum token similar encontrado no banco de dados."
        
        # Usa a mensagem atual enviada pelo usuário
        if not current_message:
            ca_info = f"\nCA: `{contract_address}`" if contract_address else ""
            return f"Token: {target_token_name}{ca_info}\n\nMensagem atual não encontrada."
        
        # Nome do token mais similar
        similar_token_name = most_similar_token.get('token_name', 'Token desconhecido')
        
        # Criar relatório com formatação mono-espaçada (estilo terminal)
        report_lines = []
        report_lines.append("```")
        report_lines.append("ANÁLISE DE SIMILARIDADE")
        report_lines.append("──────────────────────────────────────")
        report_lines.append(f"Token Analisado:     {target_token_name}")
        
        # Adiciona CA do token analisado se disponível
        if contract_address:
            report_lines.append(f"CA:  {contract_address}")
        else:
            report_lines.append(f"CA:                  Não disponível")
        
        report_lines.append(f"Token Mais Similar:  {similar_token_name}")
        
        # Adiciona CA do token mais similar do banco de dados
        similar_contract_address = most_similar_token.get('contract_address')
        if similar_contract_address:
            report_lines.append(f"CA:  {similar_contract_address}")
        else:
            report_lines.append(f"CA:                  Não disponível")
            
        report_lines.append(f"Similaridade Geral:  {similarity:.1f}%")
        report_lines.append("")
        
        # Seções de similaridade com caracteres de árvore
        report_lines.append("Similaridades por seção:")
        section_names = {
            'market_overview': 'Market Overview',
            'wallet_insights': 'Wallet Insights',
            'risk_metrics': 'Risk Metrics',
            'top_holders': 'Top 10 Holders',
            'source_wallets': 'Source Wallets'
        }
        
        section_keys = list(section_names.keys())
        # Calcula o tamanho máximo dos nomes das seções para alinhamento
        max_section_name_length = max(len(name) for name in section_names.values())
        
        for i, (section_key, section_name) in enumerate(section_names.items()):
            similarity_value = section_similarities.get(section_key, 0.0)
            tree_char = "└" if i == len(section_keys) - 1 else "├"
            # Alinha o nome da seção à esquerda com espaçamento fixo
            padded_name = f"{section_name}:".ljust(max_section_name_length + 1)
            report_lines.append(f"{tree_char} {padded_name}      {similarity_value:.1f}%")
        
        report_lines.append("")
        report_lines.append("Lado esquerdo ATUAL direito BANCO DE DADOS")
        report_lines.append("──────────────────────────────────────")
        report_lines.append("```")
        
        return '\n'.join(report_lines) 