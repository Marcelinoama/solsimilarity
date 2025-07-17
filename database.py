import sqlite3
import json
from datetime import datetime
from config import Config
import os

class TokenDatabase:
    def __init__(self):
        self.db_file = Config.DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Cria tabela apenas se não existir (preserva dados existentes)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_name TEXT,
                    contract_address TEXT,
                    
                    -- Market Overview values
                    market_cap REAL,
                    price_change REAL,
                    traders INTEGER,
                    buy_volume REAL,
                    sell_volume REAL,
                    buy_count INTEGER,
                    sell_count INTEGER,
                    buyers INTEGER,
                    sellers INTEGER,
                    

                    
                    -- Wallet Insights (novo formato)
                    holders_totais INTEGER,
                    smart_wallets INTEGER,
                    fresh_wallets INTEGER,
                    renowned_wallets INTEGER,
                    creator_wallets INTEGER,
                    sniper_wallets INTEGER,
                    rat_traders INTEGER,
                    whale_wallets INTEGER,
                    top_wallets INTEGER,
                    following_wallets INTEGER,
                    bluechip_holders INTEGER,
                    bundler_wallets INTEGER,
                    
                    -- Risk Metrics (novo)
                    bluechip_holders_percentage REAL,
                    rat_trader_supply_percentage REAL,
                    bundler_supply_percentage REAL,
                    entrapment_supply_percentage REAL,
                    degen_calls INTEGER,
                    sinais_tecnicos INTEGER,
                    
                    -- Top Holders analysis (sofisticada)
                    top_holders_percentage REAL,
                    top1_holder_percentage REAL,
                    top5_holders_percentage REAL,
                    top10_holders_percentage REAL,
                    holders_concentration_ratio REAL,
                    holders_distribution_score REAL,
                    
                    -- Source Wallets analysis (real)
                    source_wallets_percentage REAL,
                    source_wallets_count INTEGER,
                    source_wallets_avg_hops REAL,
                    
                    raw_message TEXT,
                    message_id INTEGER,
                    group_id INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Cria tabela de configurações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE,
                    setting_value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insere configuração padrão de threshold se não existir
            cursor.execute('''
                INSERT OR IGNORE INTO settings (setting_key, setting_value) 
                VALUES ('min_similarity_threshold', '70.0')
            ''')
            
            # Cria tabela para contratos já exibidos (evitar repetições)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS displayed_contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_address TEXT UNIQUE,
                    token_name TEXT,
                    similarity_percentage REAL,
                    displayed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migração: Adiciona coluna contract_address se não existir
            try:
                cursor.execute('ALTER TABLE tokens ADD COLUMN contract_address TEXT')
            except sqlite3.OperationalError:
                # Coluna já existe, não faz nada
                pass
            
            # Migração: Adiciona novas colunas do Wallet Insights
            new_columns = [
                'holders_totais INTEGER',
                'smart_wallets INTEGER', 
                'fresh_wallets INTEGER',
                'renowned_wallets INTEGER',
                'creator_wallets INTEGER',
                'sniper_wallets INTEGER',
                'rat_traders INTEGER',
                'whale_wallets INTEGER',
                'top_wallets INTEGER',
                'following_wallets INTEGER',
                'bluechip_holders INTEGER',
                'bundler_wallets INTEGER',
                'bluechip_holders_percentage REAL',
                'rat_trader_supply_percentage REAL',
                'bundler_supply_percentage REAL',
                'entrapment_supply_percentage REAL',
                'degen_calls INTEGER',
                'sinais_tecnicos INTEGER'
            ]
            
            for column_def in new_columns:
                try:
                    cursor.execute(f'ALTER TABLE tokens ADD COLUMN {column_def}')
                except sqlite3.OperationalError:
                    # Coluna já existe, continua
                    pass
            
            conn.commit()
    
    def save_token_info(self, token_data, message_id, group_id):
        """Salva informações do token no banco de dados"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tokens (
                    token_name, contract_address, market_cap, price_change, traders,
                    buy_volume, sell_volume, buy_count, sell_count,
                    buyers, sellers, holders_totais, smart_wallets, fresh_wallets,
                    renowned_wallets, creator_wallets, sniper_wallets, rat_traders,
                    whale_wallets, top_wallets, following_wallets, bluechip_holders,
                    bundler_wallets, bluechip_holders_percentage, rat_trader_supply_percentage,
                    bundler_supply_percentage, entrapment_supply_percentage, degen_calls,
                    sinais_tecnicos, top_holders_percentage, top1_holder_percentage,
                    top5_holders_percentage, top10_holders_percentage, holders_concentration_ratio,
                    holders_distribution_score, source_wallets_percentage, source_wallets_count,
                    source_wallets_avg_hops,
                    top_holders_sol_total, top5_holders_sol_total, top1_holder_sol_amount,
                    holders_sol_distribution_score, holders_sol_concentration_ratio,
                    raw_message, message_id, group_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                token_data.get('token_name'),
                token_data.get('contract_address'),
                token_data.get('market_cap'),
                token_data.get('price_change'),
                token_data.get('traders'),
                token_data.get('buy_volume'),
                token_data.get('sell_volume'),
                token_data.get('buy_count'),
                token_data.get('sell_count'),
                token_data.get('buyers'),
                token_data.get('sellers'),
                token_data.get('holders_totais'),
                token_data.get('smart_wallets'),
                token_data.get('fresh_wallets'),
                token_data.get('renowned_wallets'),
                token_data.get('creator_wallets'),
                token_data.get('sniper_wallets'),
                token_data.get('rat_traders'),
                token_data.get('whale_wallets'),
                token_data.get('top_wallets'),
                token_data.get('following_wallets'),
                token_data.get('bluechip_holders'),
                token_data.get('bundler_wallets'),
                token_data.get('bluechip_holders_percentage'),
                token_data.get('rat_trader_supply_percentage'),
                token_data.get('bundler_supply_percentage'),
                token_data.get('entrapment_supply_percentage'),
                token_data.get('degen_calls'),
                token_data.get('sinais_tecnicos'),
                token_data.get('top_holders_percentage'),
                token_data.get('top1_holder_percentage'),
                token_data.get('top5_holders_percentage'),
                token_data.get('top10_holders_percentage'),
                token_data.get('holders_concentration_ratio'),
                token_data.get('holders_distribution_score'),
                token_data.get('source_wallets_percentage'),
                token_data.get('source_wallets_count'),
                token_data.get('source_wallets_avg_hops'),
                token_data.get('top_holders_sol_total'),
                token_data.get('top5_holders_sol_total'),
                token_data.get('top1_holder_sol_amount'),
                token_data.get('holders_sol_distribution_score'),
                token_data.get('holders_sol_concentration_ratio'),
                token_data.get('raw_message'),
                message_id,
                group_id
            ))
            conn.commit()
    
    def get_all_tokens(self):
        """Recupera todos os tokens do banco de dados"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tokens')
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            tokens = []
            for row in rows:
                token = dict(zip(columns, row))
                tokens.append(token)
            
            return tokens
    
    def clear_all_tokens(self):
        """Remove todos os tokens do banco de dados"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tokens')
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count
    
    def get_tokens_count(self):
        """Retorna a quantidade total de tokens no banco"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM tokens')
            count = cursor.fetchone()[0]
            return count 

    def delete_token_by_id(self, token_id):
        """Remove um token específico pelo ID"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT token_name FROM tokens WHERE id = ?', (token_id,))
            token = cursor.fetchone()
            
            if token:
                cursor.execute('DELETE FROM tokens WHERE id = ?', (token_id,))
                conn.commit()
                return token[0]  # Retorna o nome do token deletado
            return None

    def delete_token_by_name(self, token_name):
        """Remove um token específico pelo nome"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tokens WHERE token_name = ?', (token_name,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    def delete_last_token(self):
        """Remove o último token adicionado"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name FROM tokens 
                ORDER BY id DESC LIMIT 1
            ''')
            token = cursor.fetchone()
            
            if token:
                cursor.execute('DELETE FROM tokens WHERE id = ?', (token[0],))
                conn.commit()
                return token[1]  # Retorna o nome do token deletado
            return None

    def delete_tokens_by_range(self, start_id, end_id):
        """Remove tokens em uma faixa de IDs"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT token_name FROM tokens 
                WHERE id BETWEEN ? AND ?
            ''', (start_id, end_id))
            tokens = cursor.fetchall()
            
            if tokens:
                cursor.execute('DELETE FROM tokens WHERE id BETWEEN ? AND ?', (start_id, end_id))
                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count, [token[0] for token in tokens]
            return 0, []

    def get_tokens_list(self, limit=20):
        """Retorna lista resumida de tokens para seleção"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name, timestamp
                FROM tokens 
                ORDER BY id DESC 
                LIMIT ?
            ''', (limit,))
            tokens = cursor.fetchall()
            return tokens

    def get_token_info(self, token_id):
        """Retorna informações básicas de um token específico"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name, created_at, market_cap, price_change
                FROM tokens 
                WHERE id = ?
            ''', (token_id,))
            token = cursor.fetchone()
            return token

    def delete_token_by_contract_address(self, contract_address):
        """Remove um token específico pelo endereço de contrato"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name FROM tokens 
                WHERE contract_address = ?
            ''', (contract_address,))
            tokens = cursor.fetchall()
            
            if tokens:
                cursor.execute('DELETE FROM tokens WHERE contract_address = ?', (contract_address,))
                conn.commit()
                return len(tokens), [token[1] for token in tokens]  # Retorna quantidade e nomes dos tokens deletados
            return 0, []

    def get_token_by_contract_address(self, contract_address):
        """Retorna informações básicas de um token pelo endereço de contrato"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name, contract_address, timestamp, market_cap, price_change
                FROM tokens 
                WHERE contract_address = ?
            ''', (contract_address,))
            token = cursor.fetchone()
            return token 

    def is_contract_already_in_database(self, contract_address):
        """Verifica se um contrato já existe no banco de dados"""
        if not contract_address:
            return False
            
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, token_name, timestamp FROM tokens 
                WHERE contract_address = ?
            ''', (contract_address,))
            result = cursor.fetchone()
            return result  # Retorna (id, token_name, timestamp) se encontrar, None se não encontrar

    def get_setting(self, setting_key, default_value=None):
        """Retorna o valor de uma configuração"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT setting_value FROM settings 
                WHERE setting_key = ?
            ''', (setting_key,))
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return default_value

    def set_setting(self, setting_key, setting_value):
        """Define o valor de uma configuração"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (setting_key, setting_value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (setting_key, str(setting_value)))
            conn.commit()
            return True

    def get_min_similarity_threshold(self):
        """Retorna o threshold mínimo de similaridade"""
        threshold = self.get_setting('min_similarity_threshold', '70.0')
        return float(threshold) if threshold else 70.0

    def set_min_similarity_threshold(self, threshold):
        """Define o threshold mínimo de similaridade"""
        return self.set_setting('min_similarity_threshold', threshold) 

    def is_contract_already_displayed(self, contract_address):
        """Verifica se um contrato já foi exibido"""
        if not contract_address:
            return False
            
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM displayed_contracts 
                WHERE contract_address = ?
            ''', (contract_address,))
            result = cursor.fetchone()
            return result is not None

    def mark_contract_as_displayed(self, contract_address, token_name, similarity_percentage):
        """Marca um contrato como já exibido"""
        if not contract_address:
            return False
            
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO displayed_contracts 
                (contract_address, token_name, similarity_percentage) 
                VALUES (?, ?, ?)
            ''', (contract_address, token_name, similarity_percentage))
            conn.commit()
            return True

    def clear_displayed_contracts(self):
        """Limpa todos os contratos já exibidos"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM displayed_contracts')
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    def get_displayed_contracts_count(self):
        """Retorna a quantidade de contratos já exibidos"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM displayed_contracts')
            count = cursor.fetchone()[0]
            return count 

    def get_all_contracts(self):
        """Retorna todos os contratos salvos com seus nomes"""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT token_name, contract_address 
                FROM tokens 
                WHERE contract_address IS NOT NULL AND contract_address != ''
                ORDER BY token_name
            ''')
            contracts = cursor.fetchall()
            return contracts 

    def create_backup(self, backup_path=None):
        """Cria backup do banco de dados"""
        import shutil
        from datetime import datetime
        
        try:
            # Define nome do backup com timestamp se não foi fornecido
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_database_{timestamp}.db"
            
            # Verifica se o arquivo do banco existe
            if not os.path.exists(self.db_file):
                return False, "Arquivo do banco de dados não encontrado"
            
            # Cria cópia do arquivo
            shutil.copy2(self.db_file, backup_path)
            
            # Verifica se o backup foi criado com sucesso
            if os.path.exists(backup_path):
                file_size = os.path.getsize(backup_path)
                return True, f"Backup criado com sucesso: {backup_path} ({file_size} bytes)"
            else:
                return False, "Erro ao criar arquivo de backup"
                
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def validate_backup_file(self, backup_path):
        """Valida se um arquivo é um backup válido do banco de dados"""
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(backup_path):
                return False, "Arquivo de backup não encontrado"
            
            # Tenta conectar ao arquivo como banco SQLite
            with sqlite3.connect(backup_path) as conn:
                cursor = conn.cursor()
                
                # Verifica se as tabelas principais existem
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('tokens', 'settings', 'displayed_contracts')
                """)
                tables = cursor.fetchall()
                
                required_tables = {'tokens', 'settings', 'displayed_contracts'}
                found_tables = {table[0] for table in tables}
                
                if not required_tables.issubset(found_tables):
                    missing = required_tables - found_tables
                    return False, f"Tabelas necessárias não encontradas: {missing}"
                
                # Verifica estrutura básica da tabela tokens
                cursor.execute("PRAGMA table_info(tokens)")
                columns = cursor.fetchall()
                
                if not columns:
                    return False, "Tabela tokens está vazia ou corrompida"
                
                # Conta quantos tokens existem no backup
                cursor.execute("SELECT COUNT(*) FROM tokens")
                token_count = cursor.fetchone()[0]
                
                return True, f"Backup válido com {token_count} tokens"
                
        except sqlite3.Error as e:
            return False, f"Arquivo não é um banco SQLite válido: {str(e)}"
        except Exception as e:
            return False, f"Erro ao validar backup: {str(e)}"
    
    def restore_from_backup(self, backup_path, create_current_backup=True):
        """Restaura banco de dados a partir de um backup"""
        import shutil
        from datetime import datetime
        
        try:
            # Valida o arquivo de backup primeiro
            is_valid, validation_message = self.validate_backup_file(backup_path)
            if not is_valid:
                return False, f"Backup inválido: {validation_message}"
            
            # Cria backup do banco atual se solicitado
            current_backup_path = None
            if create_current_backup and os.path.exists(self.db_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                current_backup_path = f"backup_before_restore_{timestamp}.db"
                shutil.copy2(self.db_file, current_backup_path)
            
            # Substitui o banco atual pelo backup
            shutil.copy2(backup_path, self.db_file)
            
            # Verifica se a restauração foi bem-sucedida
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tokens")
                token_count = cursor.fetchone()[0]
            
            success_msg = f"Banco restaurado com sucesso! {token_count} tokens carregados."
            if current_backup_path:
                success_msg += f" Backup anterior salvo em: {current_backup_path}"
            
            return True, success_msg
            
        except Exception as e:
            return False, f"Erro ao restaurar backup: {str(e)}"
    
    def get_database_info(self):
        """Retorna informações básicas sobre o banco de dados"""
        try:
            if not os.path.exists(self.db_file):
                return {
                    'exists': False,
                    'size': 0,
                    'tokens_count': 0,
                    'last_modified': None
                }
            
            # Informações do arquivo
            file_size = os.path.getsize(self.db_file)
            last_modified = datetime.fromtimestamp(os.path.getmtime(self.db_file))
            
            # Informações do banco
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tokens")
                tokens_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM displayed_contracts")
                displayed_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT setting_value FROM settings 
                    WHERE setting_key = 'min_similarity_threshold'
                """)
                threshold_result = cursor.fetchone()
                threshold = float(threshold_result[0]) if threshold_result else 70.0
            
            return {
                'exists': True,
                'size': file_size,
                'tokens_count': tokens_count,
                'displayed_contracts_count': displayed_count,
                'threshold': threshold,
                'last_modified': last_modified,
                'file_path': self.db_file
            }
            
        except Exception as e:
            return {
                'exists': False,
                'error': str(e)
            } 