#!/usr/bin/env python3
"""
Teste para o parser de mensagens de tokens
"""

from message_parser import MessageParser
import json

def test_message():
    """Testa o parser com uma mensagem de exemplo"""
    
    sample_message = """everything is grok (EIG)
├ oRRMQqkrk8YQp6ehJBSQUg4PUZuud8oUUEgk6t7pump
└ Age: 10/07/2025 - 15h17min

👨‍💻 Creator:
└ EA4Yn7XxehkdGmBToMsefBNQJEH93YDJG9FqTz48cThG




📊 Market Overview (24h):
├ Market Cap:     $    3.88K
├ Buy Volume:     $  710.97K
├ Sell Volume:    $  710.07K
├ Price%:            -21.97%
├ Traders:              2417
├ Buy Count:            5427
├ Sell Count:           5507
├ Buyers:               2395
└ Sellers:              2369


🌐 Social Links:
├ Twitter (https://x.com/cb_doge/status/1943449214555689471)
└ AXI (http://axiom.trade/t/oRRMQqkrk8YQp6ehJBSQUg4PUZuud8oUUEgk6t7pump/@trancebh)

👥 Wallet Statistics:
├ Fresh:      53 ( 7.04%)
├ Creator:     1 ( 0.13%)
├ Renowned:    0 ( 0.00%)
├ Sniper:      5 ( 0.66%)
├ Top:       162 (21.51%)
├ Bundler:   532 (70.65%)
└ Total:     753

📊 Top 20 Holders:  7.89%
├  1. 12ZHKk...L5Ds -  4.35% -   0.45 SOL
├  2. AwVdWh...MP7L -  1.19% -  10.93 SOL
├  3. 8DnFuh...FatA -  0.78% -   0.02 SOL
├  4. HjtK2p...Dheu -  0.47% -   4.36 SOL
├  5. 3tWA3Q...cJT5 -  0.19% -   0.01 SOL

🔍 Source Wallets:  5.18%
├ 5tzFki...uAi9 -  2 hops
├ 5VCwKt...NmcD -  2 hops
└ ASTyfS...iaJZ -  2 hops"""

    print("🧪 Teste do Parser de Mensagens")
    print("="*50)
    
    parser = MessageParser()
    
    print("📝 Mensagem de teste:")
    print(sample_message[:200] + "..." if len(sample_message) > 200 else sample_message)
    print("\n" + "="*50)
    
    # Faz o parse da mensagem
    token_data = parser.parse_token_message(sample_message)
    
    print("📊 Dados extraídos:")
    print("-"*30)
    
    # Mostra dados principais
    print(f"🪙 Nome do Token: {token_data.get('token_name')}")
    print(f"📍 Endereço: {token_data.get('token_address')}")
    print(f"👨‍💻 Criador: {token_data.get('creator_address')}")

    print(f"💰 Market Cap: ${token_data.get('market_cap'):,.2f}" if token_data.get('market_cap') else "💰 Market Cap: N/A")
    print(f"📈 Mudança de Preço: {token_data.get('price_change')}%" if token_data.get('price_change') else "📈 Mudança de Preço: N/A")
    print(f"👥 Traders: {token_data.get('traders'):,}" if token_data.get('traders') else "👥 Traders: N/A")

    
    print(f"\n🌐 Links Sociais: {len(token_data.get('social_links', []))}")
    for link in token_data.get('social_links', []):
        print(f"   - {link['type']}: {link['url']}")
    
    print(f"\n📊 Top Holders: {len(token_data.get('top_holders', []))}")
    for holder in token_data.get('top_holders', [])[:3]:  # Mostra apenas os 3 primeiros
        print(f"   {holder['rank']}. {holder['address']} - {holder['percentage']}%")
    
    # Testa extração de características
    print("\n" + "="*50)
    print("🔍 Características para Comparação:")
    print("-"*30)
    
    # Mostra algumas características importantes do token
    print(f"   Token: {token_data.get('token_name', 'N/A')}")
    print(f"   Market Cap: {token_data.get('market_cap', 'N/A')}")
    print(f"   Traders: {token_data.get('traders', 'N/A')}")
    
    print("\n✅ Teste concluído com sucesso!")
    print("🔧 Se os dados estão corretos, o parser está funcionando.")

if __name__ == '__main__':
    test_message() 