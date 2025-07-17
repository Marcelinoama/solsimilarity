import re
from typing import Dict, List, Any

class MessageParser:
    def __init__(self):
        pass
    
    def parse_token_message(self, message_text: str) -> Dict[str, Any]:
        """
        Extrai apenas os valores numéricos principais para comparação
        """
        token_data = {
            'raw_message': message_text,
            'token_name': None,
            'contract_address': None,
            
            # 📊 Market Overview - valores numéricos principais
            'market_cap': None,
            'price_change': None,
            'traders': None,
            'buy_volume': None,
            'sell_volume': None,
            'buy_count': None,
            'sell_count': None,
            'buyers': None,
            'sellers': None,
            

            

            
            # 📊 Wallet Insights - campos atualizados
            'holders_totais': None,
            'smart_wallets': None,
            'fresh_wallets': None,
            'renowned_wallets': None,
            'creator_wallets': None,
            'sniper_wallets': None,
            'rat_traders': None,
            'whale_wallets': None,
            'top_wallets': None,
            'following_wallets': None,
            'bluechip_holders': None,
            'bundler_wallets': None,
            
            # 📈 Risk Metrics - seção nova
            'bluechip_holders_percentage': None,
            'rat_trader_supply_percentage': None,
            'bundler_supply_percentage': None,
            'entrapment_supply_percentage': None,
            'degen_calls': None,
            'sinais_tecnicos': None,
            
            # 📊 Top 10 Holders - análise sofisticada (mudou de 20 para 10)
            'top_holders_percentage': None,  # Total dos 10
            'top1_holder_percentage': None,   # Concentração do #1
            'top5_holders_percentage': None,  # Oligopólio top 5
            'top10_holders_percentage': None, # Concentração top 10
            'holders_concentration_ratio': None, # Razão top1/total
            'holders_distribution_score': None,   # Score de distribuição
            
            # 🔍 Source Wallets - análise real
            'source_wallets_percentage': None,  # Porcentagem total
            'source_wallets_count': None,       # Quantidade de wallets
            'source_wallets_avg_hops': None     # Média de hops
        }
        
        # Extrai nome do token - procura no início da mensagem, antes de qualquer seção com emojis
        lines = message_text.strip().split('\n')
        token_name = None
        
        # Procura o nome do token na primeira linha que não contenha emojis de seção
        for line in lines:
            line = line.strip()
            if line and not any(emoji in line for emoji in ['📊', '📈', '🔍', '👨‍💻', '🏭', '🌐']):
                # Procura por padrão "Nome (Símbolo)" na primeira linha válida
                token_match = re.search(r'^(.+?)\s*\(([^)]+)\)(?:\s*$|\s*├)', line)
                if token_match:
                    token_name = token_match.group(1).strip()
                    break
                else:
                    # Se não encontrar parênteses, usa a linha inteira (até o primeiro ├ se houver)
                    if '├' in line:
                        token_name = line.split('├')[0].strip()
                    else:
                        token_name = line.strip()
                    break
        
        # Fallback: se não encontrou nas primeiras linhas, procura por padrão mais flexível
        if not token_name:
            # Procura por qualquer texto seguido de parênteses que não seja uma seção
            token_match = re.search(r'^([^📊📈🔍👨‍💻🏭🌐]+?)\s*\(([^)]+)\)', message_text.strip())
            if token_match:
                token_name = token_match.group(1).strip()
        
        # Limpa o nome do token de caracteres desnecessários
        if token_name:
            # Remove emojis comuns que podem aparecer
            token_name = re.sub(r'[🟣👀🟢🔴🟡🐋♦️]', '', token_name).strip()
            # Remove múltiplos espaços
            token_name = re.sub(r'\s+', ' ', token_name)
            
        token_data['token_name'] = token_name
        
        # 📊 Contract Address - extrai endereço de contrato
        # Busca padrões mais flexíveis para capturar o endereço
        contract_patterns = [
            r'├\s*([A-Za-z0-9]{32,50})\s*(?:\n|$)',  # Linha com ├ seguida de endereço
            r'└\s*([A-Za-z0-9]{32,50})\s*(?:\n|$)',  # Linha com └ seguida de endereço
            r'^([A-Za-z0-9]{32,50})\s*$',            # Linha só com endereço
            r'CA:\s*([A-Za-z0-9]{32,50})',           # Formato "CA: endereço"
            r'Contract:\s*([A-Za-z0-9]{32,50})',     # Formato "Contract: endereço"
        ]
        
        for pattern in contract_patterns:
            contract_match = re.search(pattern, message_text, re.MULTILINE)
            if contract_match:
                potential_address = contract_match.group(1).strip()
                # Verifica se não é um valor numérico (como timestamp ou ID)
                if not re.match(r'^\d+$', potential_address):
                    token_data['contract_address'] = potential_address
                    break
        
        # 📊 Market Overview - extrai valores numéricos
        # Market Cap
        market_cap_match = re.search(r'├\s*Market Cap:\s*\$\s*([\d.,]+)([KMB]?)', message_text)
        if market_cap_match:
            value = float(market_cap_match.group(1).replace(',', ''))
            unit = market_cap_match.group(2)
            if unit == 'K':
                value *= 1000
            elif unit == 'M':
                value *= 1000000
            elif unit == 'B':
                value *= 1000000000
            token_data['market_cap'] = value
        
        # Price Change
        price_change_match = re.search(r'├\s*Price%:\s*([-+]?[\d.,]+)%', message_text)
        if price_change_match:
            token_data['price_change'] = float(price_change_match.group(1).replace(',', '.'))
        
        # Traders
        traders_match = re.search(r'├\s*Traders:\s*([\d,]+)', message_text)
        if traders_match:
            token_data['traders'] = int(traders_match.group(1).replace(',', ''))
        
        # Buy Volume
        buy_volume_match = re.search(r'├\s*Buy Volume:\s*\$\s*([\d.,]+)([KMB]?)', message_text)
        if buy_volume_match:
            value = float(buy_volume_match.group(1).replace(',', ''))
            unit = buy_volume_match.group(2)
            if unit == 'K':
                value *= 1000
            elif unit == 'M':
                value *= 1000000
            elif unit == 'B':
                value *= 1000000000
            token_data['buy_volume'] = value
        
        # Sell Volume
        sell_volume_match = re.search(r'├\s*Sell Volume:\s*\$\s*([\d.,]+)([KMB]?)', message_text)
        if sell_volume_match:
            value = float(sell_volume_match.group(1).replace(',', ''))
            unit = sell_volume_match.group(2)
            if unit == 'K':
                value *= 1000
            elif unit == 'M':
                value *= 1000000
            elif unit == 'B':
                value *= 1000000000
            token_data['sell_volume'] = value
        
        # Buy Count
        buy_count_match = re.search(r'├\s*Buy Count:\s*([\d,]+)', message_text)
        if buy_count_match:
            token_data['buy_count'] = int(buy_count_match.group(1).replace(',', ''))
        
        # Sell Count
        sell_count_match = re.search(r'├\s*Sell Count:\s*([\d,]+)', message_text)
        if sell_count_match:
            token_data['sell_count'] = int(sell_count_match.group(1).replace(',', ''))
        
        # Buyers
        buyers_match = re.search(r'├\s*Buyers:\s*([\d,]+)', message_text)
        if buyers_match:
            token_data['buyers'] = int(buyers_match.group(1).replace(',', ''))
        
        # Sellers
        sellers_match = re.search(r'└\s*Sellers:\s*([\d,]+)', message_text)
        if sellers_match:
            token_data['sellers'] = int(sellers_match.group(1).replace(',', ''))
        

        
        # 📊 Wallet Insights - extrai valores numéricos
        # Holders Totais
        holders_totais_match = re.search(r'├\s*Holders Totais:\s*([\d,]+)', message_text)
        if holders_totais_match:
            token_data['holders_totais'] = int(holders_totais_match.group(1).replace(',', ''))
        
        # Smart Wallets
        smart_wallets_match = re.search(r'├\s*Smart Wallets:\s*([\d,]+)', message_text)
        if smart_wallets_match:
            token_data['smart_wallets'] = int(smart_wallets_match.group(1).replace(',', ''))
        
        # Fresh Wallets
        fresh_wallets_match = re.search(r'├\s*Fresh Wallets:\s*([\d,]+)', message_text)
        if fresh_wallets_match:
            token_data['fresh_wallets'] = int(fresh_wallets_match.group(1).replace(',', ''))
        
        # Renowned Wallets
        renowned_wallets_match = re.search(r'├\s*Renowned Wallets:\s*([\d,]+)', message_text)
        if renowned_wallets_match:
            token_data['renowned_wallets'] = int(renowned_wallets_match.group(1).replace(',', ''))
        
        # Creator Wallets
        creator_wallets_match = re.search(r'├\s*Creator Wallets:\s*([\d,]+)', message_text)
        if creator_wallets_match:
            token_data['creator_wallets'] = int(creator_wallets_match.group(1).replace(',', ''))
        
        # Sniper Wallets
        sniper_wallets_match = re.search(r'├\s*Sniper Wallets:\s*([\d,]+)', message_text)
        if sniper_wallets_match:
            token_data['sniper_wallets'] = int(sniper_wallets_match.group(1).replace(',', ''))
        
        # Rat Traders
        rat_traders_match = re.search(r'├\s*Rat Traders:\s*([\d,]+)', message_text)
        if rat_traders_match:
            token_data['rat_traders'] = int(rat_traders_match.group(1).replace(',', ''))
        
        # Whale Wallets
        whale_wallets_match = re.search(r'├\s*Whale Wallets:\s*([\d,]+)', message_text)
        if whale_wallets_match:
            token_data['whale_wallets'] = int(whale_wallets_match.group(1).replace(',', ''))
        
        # Top Wallets
        top_wallets_match = re.search(r'├\s*Top Wallets:\s*([\d,]+)', message_text)
        if top_wallets_match:
            token_data['top_wallets'] = int(top_wallets_match.group(1).replace(',', ''))
        
        # Following Wallets
        following_wallets_match = re.search(r'├\s*Following Wallets:\s*([\d,]+)', message_text)
        if following_wallets_match:
            token_data['following_wallets'] = int(following_wallets_match.group(1).replace(',', ''))
        
        # Bluechip Holders
        bluechip_holders_match = re.search(r'├\s*Bluechip Holders:\s*([\d,]+)', message_text)
        if bluechip_holders_match:
            token_data['bluechip_holders'] = int(bluechip_holders_match.group(1).replace(',', ''))
        
        # Bundler Wallets
        bundler_wallets_match = re.search(r'└\s*Bundler Wallets:\s*([\d,]+)', message_text)
        if bundler_wallets_match:
            token_data['bundler_wallets'] = int(bundler_wallets_match.group(1).replace(',', ''))
        
        # 📈 Risk Metrics - extrai porcentagens
        # % Bluechip Holders
        bluechip_pct_match = re.search(r'├\s*%\s*Bluechip Holders:\s*([\d.,]+)%', message_text)
        if bluechip_pct_match:
            token_data['bluechip_holders_percentage'] = float(bluechip_pct_match.group(1).replace(',', '.'))
        
        # % Rat Trader Supply
        rat_trader_pct_match = re.search(r'├\s*%\s*Rat Trader Supply:\s*([\d.,]+)%', message_text)
        if rat_trader_pct_match:
            token_data['rat_trader_supply_percentage'] = float(rat_trader_pct_match.group(1).replace(',', '.'))
        
        # % Bundler Supply
        bundler_supply_pct_match = re.search(r'├\s*%\s*Bundler Supply:\s*([\d.,]+)%', message_text)
        if bundler_supply_pct_match:
            token_data['bundler_supply_percentage'] = float(bundler_supply_pct_match.group(1).replace(',', '.'))
        
        # % Entrapment Supply
        entrapment_pct_match = re.search(r'├\s*%\s*Entrapment Supply:\s*([\d.,]+)%', message_text)
        if entrapment_pct_match:
            token_data['entrapment_supply_percentage'] = float(entrapment_pct_match.group(1).replace(',', '.'))
        
        # Degen Calls
        degen_calls_match = re.search(r'├\s*Degen Calls:\s*([\d,]+)', message_text)
        if degen_calls_match:
            token_data['degen_calls'] = int(degen_calls_match.group(1).replace(',', ''))
        
        # Sinais Técnicos
        sinais_match = re.search(r'└\s*Sinais Técnicos:\s*([\d,]+)', message_text)
        if sinais_match:
            token_data['sinais_tecnicos'] = int(sinais_match.group(1).replace(',', ''))
        
        # 📊 Top 10 Holders - análise sofisticada
        self._extract_holders_analysis(message_text, token_data)
        
        # 🔍 Source Wallets - análise real
        self._extract_source_wallets_analysis(message_text, token_data)
        

        
        return token_data
    
    def _extract_holders_analysis(self, message_text: str, token_data: Dict[str, Any]):
        """Extrai análise detalhada dos Top 10 Holders"""
        
        # 1. Porcentagem total dos top 10
        holders_match = re.search(r'📊.*?Top 10 Holders:\s*([\d.,]+)%', message_text)
        if holders_match:
            token_data['top_holders_percentage'] = float(holders_match.group(1).replace(',', '.'))
        
        # 2. Extrai porcentagens individuais dos holders e valores de SOL
        holder_percentages = []
        holder_sol_amounts = []
        
        # Padrão para encontrar as linhas dos holders: ├  1. ABC...XYZ - 4.20% - 65.92 SOL
        holder_pattern = r'[├└]\s*\d+\.\s+\w+\.\.\.\w+\s*-\s*([\d.,]+)%\s*-\s*([\d.,]+)\s*SOL'
        holder_matches = re.findall(holder_pattern, message_text)
        
        for match in holder_matches:
            percentage = float(match[0].replace(',', '.'))
            sol_amount = float(match[1].replace(',', '.'))
            holder_percentages.append(percentage)
            holder_sol_amounts.append(sol_amount)
        
        if holder_percentages:
            # 3. Análise de concentração
            token_data['top1_holder_percentage'] = holder_percentages[0] if len(holder_percentages) >= 1 else None
            
            # Top 5 holders
            top5_sum = sum(holder_percentages[:5]) if len(holder_percentages) >= 5 else sum(holder_percentages)
            token_data['top5_holders_percentage'] = top5_sum
            
            # Top 10 holders 
            top10_sum = sum(holder_percentages[:10]) if len(holder_percentages) >= 10 else sum(holder_percentages)
            token_data['top10_holders_percentage'] = top10_sum
            
            # 4. Razão de concentração (top1 / total)
            total_holders_pct = token_data.get('top_holders_percentage', 0)
            if total_holders_pct and total_holders_pct > 0:
                concentration_ratio = (holder_percentages[0] / total_holders_pct) * 100
                token_data['holders_concentration_ratio'] = concentration_ratio
            
            # 5. Score de distribuição (baseado na distribuição dos top 10)
            if len(holder_percentages) >= 10:
                # Calcula desvio padrão dos top 10 como medida de distribuição
                import statistics
                top10_percentages = holder_percentages[:10]
                mean_pct = statistics.mean(top10_percentages)
                std_dev = statistics.stdev(top10_percentages) if len(top10_percentages) > 1 else 0
                
                # Score de distribuição: menor desvio = mais distribuído (score maior)
                # Normaliza para 0-100 scale
                distribution_score = max(0, 100 - (std_dev * 10))
                token_data['holders_distribution_score'] = distribution_score
        
        # 6. Análise de valores em SOL (nova funcionalidade)
        if holder_sol_amounts:
            # Total de SOL dos top holders
            token_data['top_holders_sol_total'] = sum(holder_sol_amounts[:10]) if len(holder_sol_amounts) >= 10 else sum(holder_sol_amounts)
            token_data['top5_holders_sol_total'] = sum(holder_sol_amounts[:5]) if len(holder_sol_amounts) >= 5 else sum(holder_sol_amounts)
            token_data['top1_holder_sol_amount'] = holder_sol_amounts[0] if len(holder_sol_amounts) >= 1 else None
            
            # Análise de distribuição de SOL
            if len(holder_sol_amounts) >= 10:
                import statistics
                top10_sol = holder_sol_amounts[:10]
                mean_sol = statistics.mean(top10_sol)
                std_dev_sol = statistics.stdev(top10_sol) if len(top10_sol) > 1 else 0
                
                # Score de distribuição de SOL (normalizado para 0-100)
                # Usa coeficiente de variação para normalizar por valor médio
                if mean_sol > 0:
                    coefficient_variation = (std_dev_sol / mean_sol) * 100
                    sol_distribution_score = max(0, 100 - coefficient_variation)
                else:
                    sol_distribution_score = 100
                
                token_data['holders_sol_distribution_score'] = sol_distribution_score
                
                # Concentração de SOL do top 1
                total_sol = sum(top10_sol)
                if total_sol > 0:
                    sol_concentration_ratio = (holder_sol_amounts[0] / total_sol) * 100
                    token_data['holders_sol_concentration_ratio'] = sol_concentration_ratio
    
    def _extract_source_wallets_analysis(self, message_text: str, token_data: Dict[str, Any]):
        """Extrai análise detalhada dos Source Wallets"""
        
        # 1. Porcentagem total dos source wallets: 🔍 Source Wallets: 14.73% (com possível link no meio)
        source_wallets_match = re.search(r'🔍.*?Source Wallets:\s*([\d.,]+)%', message_text)
        if source_wallets_match:
            token_data['source_wallets_percentage'] = float(source_wallets_match.group(1).replace(',', '.'))
        
        # 2. Extrai informações individuais dos source wallets
        hop_values = []
        wallet_count = 0
        
        # Padrão para encontrar linhas: ├ 5tzFki...uAi9 -  5 hops ou ├ Debridge - 10 hops
        source_pattern = r'[├└]\s+[\w🔹]+.*?\s*-\s*(\d+)\s+hops?'
        source_matches = re.findall(source_pattern, message_text)
        
        for match in source_matches:
            hops = int(match)
            hop_values.append(hops)
            wallet_count += 1
        
        if hop_values:
            # 3. Quantidade de source wallets
            token_data['source_wallets_count'] = wallet_count
            
            # 4. Média de hops
            avg_hops = sum(hop_values) / len(hop_values)
            token_data['source_wallets_avg_hops'] = avg_hops
    
 