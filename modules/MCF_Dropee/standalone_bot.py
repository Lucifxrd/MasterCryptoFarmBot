#!/usr/bin/env python3
# Standalone Dropee Bot - Funciona independentemente do MasterCryptoFarm
# Desenvolvido a partir do código original do MasterkinG32

import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
import cloudscraper
import requests

# Configurações básicas
MODULE_DIR = Path(__file__).resolve().parent
ACCOUNTS_FILE = os.path.join(MODULE_DIR, "accounts.json")
TOKENS_FILE = os.path.join(MODULE_DIR, "tokens.json")
CONFIG_FILE = os.path.join(MODULE_DIR, "config.json")

# Configurações padrão
DEFAULT_CONFIG = {
    "check_interval": 3600,
    "auto_claim_daily_reward": True,
    "auto_farming": True,
    "auto_tasks": True,
    "delay_min": 5,
    "delay_max": 15
}

class Logger:
    """Logger simples para substituir o sistema de logging do MCF"""
    
    def __init__(self, name="DropeeBot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Configurar handler se não existir
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message):
        # Remove códigos de cor HTML para logs simples
        clean_msg = self._clean_message(message)
        self.logger.info(clean_msg)
    
    def error(self, message):
        clean_msg = self._clean_message(message)
        self.logger.error(clean_msg)
    
    def warning(self, message):
        clean_msg = self._clean_message(message)
        self.logger.warning(clean_msg)
    
    def success(self, message):
        clean_msg = self._clean_message(message)
        self.logger.info(f"✅ {clean_msg}")
    
    def _clean_message(self, message):
        """Remove tags HTML de cor das mensagens"""
        import re
        # Remove tags como <r>, </r>, <y>, </y>, etc.
        clean = re.sub(r'<[^>]*>', '', str(message))
        # Remove códigos de escape ANSI
        clean = re.sub(r'\033\[[0-9;]*m', '', clean)
        return clean

class UtilityFunctions:
    """Funções utilitárias para substituir utilities.utilities"""
    
    @staticmethod
    def getConfig(key, default=None):
        """Obter configuração do arquivo config.json"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                return config.get(key, default)
            return default
        except:
            return default
    
    @staticmethod
    def read_json_file(json_file, default=None):
        """Ler arquivo JSON com fallback"""
        if not os.path.exists(json_file):
            return default
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except:
            return default
    
    @staticmethod
    def save_json_file(json_file, data):
        """Salvar dados em arquivo JSON"""
        try:
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4)
            return True
        except:
            return False

class TokenManager:
    """Gerenciador de tokens de autenticação"""
    
    @staticmethod
    def save_auth_token(session_name, access_token=None, refresh_token=None):
        if session_name is None:
            return False
        try:
            data = UtilityFunctions.read_json_file(TOKENS_FILE, {})
            data[session_name] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            return UtilityFunctions.save_json_file(TOKENS_FILE, data)
        except:
            return False
    
    @staticmethod
    def get_auth_token(session_name):
        try:
            data = UtilityFunctions.read_json_file(TOKENS_FILE, {})
            return data.get(session_name, {})
        except:
            return {}
    
    @staticmethod
    def delete_auth_token(session_name):
        try:
            data = UtilityFunctions.read_json_file(TOKENS_FILE, {})
            if session_name in data:
                del data[session_name]
                return UtilityFunctions.save_json_file(TOKENS_FILE, data)
            return True
        except:
            return False
    
    @staticmethod
    def get_tz_offset():
        offset = datetime.now().astimezone().utcoffset()
        if offset is not None:
            offset_minutes = -offset.total_seconds() / 60
        else:
            offset_minutes = -200
        return int(offset_minutes)

class HttpRequest:
    """Cliente HTTP para requisições da API do Dropee"""
    
    def __init__(self, log, proxy=None, user_agent=None, tg_web_data=None, account_name=None):
        self.log = log
        self.proxy = proxy
        self.user_agent = user_agent or "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.3"
        self.game_url = {
            "gateway": "https://dropee.clicker-game-api.tropee.com",
            "game": "https://dropee.clicker-game-api.tropee.com",
            "wallet": "https://dropee.clicker-game-api.tropee.com",
            "subscription": "https://dropee.clicker-game-api.tropee.com",
            "tribe": "https://dropee.clicker-game-api.tropee.com",
            "user": "https://dropee.clicker-game-api.tropee.com",
            "earn": "https://dropee.clicker-game-api.tropee.com",
        }
        self.authToken = None
        self.RefreshToken = None
        self.tg_web_data = tg_web_data
        self.account_name = account_name
        self.token_refreshed = False
        
        self.scraper = cloudscraper.create_scraper()
        
        # Carregar tokens salvos
        tokens = TokenManager.get_auth_token(self.account_name)
        if tokens:
            self.authToken = tokens.get("access_token")
            self.RefreshToken = tokens.get("refresh_token")
    
    def _get_proxy(self):
        if self.proxy:
            return {"http": self.proxy, "https": self.proxy}
        return None
    
    def _get_default_headers(self):
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://webapp.game.dropee.xyz",
            "pragma": "no-cache",
            "referer": "https://webapp.game.dropee.xyz/",
            "sec-ch-ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": self.user_agent,
            "x-requested-with": "org.telegram.messenger",
        }
    
    def _fix_url(self, url, domain="game"):
        if url.startswith("http"):
            return url
        base_url = self.game_url.get(domain, self.game_url["game"])
        return f"{base_url}{url}"
    
    def get(self, url, domain="game", headers=None, auth_header=True, **kwargs):
        try:
            url = self._fix_url(url, domain)
            default_headers = self._get_default_headers()
            
            if headers:
                default_headers.update(headers)
            
            if auth_header and self.authToken:
                default_headers["authorization"] = f"Bearer {self.authToken}"
            
            response = self.scraper.get(
                url=url,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )
            
            if response.status_code == 401 and self.renew_access_token():
                self.log.info("🔄 Token renovado, tentando novamente...")
                TokenManager.save_auth_token(self.account_name, self.authToken, self.RefreshToken)
                return self.get(url, domain, headers, auth_header, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            self.log.error(f"Erro GET {url}: {e}")
            return None
    
    def post(self, url, domain="game", data=None, headers=None, auth_header=True, **kwargs):
        try:
            url = self._fix_url(url, domain)
            default_headers = self._get_default_headers()
            
            if headers:
                default_headers.update(headers)
            
            if auth_header and self.authToken:
                default_headers["authorization"] = f"Bearer {self.authToken}"
            
            response = self.scraper.post(
                url=url,
                json=data,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )
            
            if response.status_code == 401 and self.renew_access_token():
                self.log.info("🔄 Token renovado, tentando novamente...")
                TokenManager.save_auth_token(self.account_name, self.authToken, self.RefreshToken)
                return self.post(url, domain, data, headers, auth_header, **kwargs)
            
            if response.status_code in [200, 201]:
                return response.json()
            
            return None
            
        except Exception as e:
            self.log.error(f"Erro POST {url}: {e}")
            return None
    
    def auth_telegram(self):
        """Autenticação inicial usando dados do Telegram"""
        try:
            data = {
                "telegram_data": self.tg_web_data,
                "tz_offset": TokenManager.get_tz_offset()
            }
            
            response = self.post(
                url="/api/v1/auth/telegram",
                domain="game",
                data=data,
                auth_header=False
            )
            
            if response and "token" in response:
                self.authToken = response["token"]["access_token"]
                self.RefreshToken = response["token"]["refresh_token"]
                TokenManager.save_auth_token(self.account_name, self.authToken, self.RefreshToken)
                self.log.success(f"Autenticação bem-sucedida para {self.account_name}")
                return True
            
            return False
            
        except Exception as e:
            self.log.error(f"Erro na autenticação: {e}")
            return False
    
    def renew_access_token(self):
        """Renovar token de acesso"""
        if not self.RefreshToken:
            return False
        
        try:
            data = {"refresh_token": self.RefreshToken}
            
            response = self.post(
                url="/api/v1/auth/refresh",
                domain="game",
                data=data,
                auth_header=False
            )
            
            if response and "token" in response:
                self.authToken = response["token"]["access_token"]
                self.RefreshToken = response["token"]["refresh_token"]
                return True
            
            return False
            
        except Exception as e:
            self.log.error(f"Erro ao renovar token: {e}")
            return False

class DropeeGame:
    """Classe principal para interagir com o jogo Dropee"""
    
    def __init__(self, log, http_request, account_name):
        self.log = log
        self.http = http_request
        self.account_name = account_name
    
    def get_balance(self):
        """Obter saldo do jogador"""
        try:
            response = self.http.get("/api/v1/user/balance")
            if response:
                return response
            return None
        except Exception as e:
            self.log.error(f"Erro ao obter saldo: {e}")
            return None
    
    def get_daily_reward(self):
        """Verificar recompensa diária disponível"""
        try:
            response = self.http.get("/api/v2/daily-reward")
            return response
        except Exception as e:
            self.log.error(f"Erro ao verificar recompensa diária: {e}")
            return None
    
    def claim_daily_reward(self):
        """Reivindicar recompensa diária"""
        try:
            response = self.http.post("/api/v2/daily-reward")
            return response
        except Exception as e:
            self.log.error(f"Erro ao reivindicar recompensa diária: {e}")
            return None
    
    def get_farming_info(self):
        """Obter informações de farming"""
        try:
            response = self.http.get("/api/v1/farming/claim")
            return response
        except Exception as e:
            return None
    
    def start_farming(self):
        """Iniciar farming"""
        try:
            response = self.http.post("/api/v1/farming/start")
            return response
        except Exception as e:
            return None
    
    def claim_farming(self):
        """Reivindicar farming"""
        try:
            response = self.http.post("/api/v1/farming/claim")
            return response
        except Exception as e:
            return None

class DropeeBot:
    """Bot principal do Dropee"""
    
    def __init__(self, account_name, tg_web_data, proxy=None):
        self.account_name = account_name
        self.log = Logger(f"DropeeBot-{account_name}")
        self.http = HttpRequest(self.log, proxy, None, tg_web_data, account_name)
        self.game = DropeeGame(self.log, self.http, account_name)
        
        # Carregar configurações
        self.config = {}
        if os.path.exists(CONFIG_FILE):
            self.config = UtilityFunctions.read_json_file(CONFIG_FILE, DEFAULT_CONFIG)
        else:
            self.config = DEFAULT_CONFIG
            UtilityFunctions.save_json_file(CONFIG_FILE, self.config)
    
    def run_account(self):
        """Executar bot para uma conta específica"""
        self.log.info(f"🚀 Iniciando bot para {self.account_name}")
        
        # Tentar autenticação
        if not self.http.authToken and not self.http.auth_telegram():
            self.log.error(f"❌ Falha na autenticação para {self.account_name}")
            return False
        
        # Verificar saldo
        balance = self.game.get_balance()
        if balance:
            self.log.info(f"💰 Saldo: {balance.get('availableBalance', 0)}")
            self.log.info(f"🎫 Play Passes: {balance.get('playPasses', 0)}")
        
        # Recompensa diária
        if self.config.get("auto_claim_daily_reward", True):
            self.handle_daily_reward()
        
        # Farming
        if self.config.get("auto_farming", True):
            self.handle_farming()
        
        self.log.success(f"✅ Execução concluída para {self.account_name}")
        return True
    
    def handle_daily_reward(self):
        """Gerenciar recompensa diária"""
        try:
            daily_reward = self.game.get_daily_reward()
            if daily_reward and daily_reward.get("canClaim"):
                result = self.game.claim_daily_reward()
                if result:
                    self.log.success("🎁 Recompensa diária reivindicada!")
                else:
                    self.log.error("❌ Falha ao reivindicar recompensa diária")
            else:
                self.log.info("⏰ Recompensa diária não disponível ainda")
        except Exception as e:
            self.log.error(f"Erro na recompensa diária: {e}")
    
    def handle_farming(self):
        """Gerenciar farming"""
        try:
            farming_info = self.game.get_farming_info()
            if not farming_info:
                # Tentar iniciar farming
                start_result = self.game.start_farming()
                if start_result:
                    self.log.success("🌱 Farming iniciado!")
                else:
                    self.log.error("❌ Falha ao iniciar farming")
                return
            
            # Verificar se pode reivindicar
            if farming_info.get("canClaim"):
                claim_result = self.game.claim_farming()
                if claim_result:
                    self.log.success("🚜 Farming reivindicado!")
                    # Tentar iniciar novo ciclo
                    start_result = self.game.start_farming()
                    if start_result:
                        self.log.success("🌱 Novo ciclo de farming iniciado!")
                else:
                    self.log.error("❌ Falha ao reivindicar farming")
            else:
                self.log.info("⏰ Farming ainda em andamento")
                
        except Exception as e:
            self.log.error(f"Erro no farming: {e}")

def create_example_accounts():
    """Criar arquivo de exemplo para contas"""
    example_accounts = {
        "account1": {
            "telegram_data": "query_id=AAAA...&user=%7B%22id%22%3A...",
            "proxy": None
        },
        "account2": {
            "telegram_data": "query_id=BBBB...&user=%7B%22id%22%3A...",
            "proxy": "http://user:pass@proxy:port"
        }
    }
    
    example_file = os.path.join(MODULE_DIR, "accounts_example.json")
    UtilityFunctions.save_json_file(example_file, example_accounts)
    print(f"📝 Arquivo de exemplo criado: {example_file}")

async def run_bot():
    """Função principal para executar o bot"""
    # Verificar se existe arquivo de contas
    if not os.path.exists(ACCOUNTS_FILE):
        print("❌ Arquivo accounts.json não encontrado!")
        print("📝 Criando arquivo de exemplo...")
        create_example_accounts()
        print(f"✏️ Edite o arquivo {ACCOUNTS_FILE} com suas contas do Telegram")
        return
    
    # Carregar contas
    accounts = UtilityFunctions.read_json_file(ACCOUNTS_FILE, {})
    if not accounts:
        print("❌ Nenhuma conta encontrada no arquivo accounts.json")
        return
    
    print(f"🚀 Iniciando bot para {len(accounts)} contas...")
    
    # Executar bot para cada conta
    for account_name, account_data in accounts.items():
        try:
            tg_web_data = account_data.get("telegram_data")
            proxy = account_data.get("proxy")
            
            if not tg_web_data:
                print(f"❌ Dados do Telegram ausentes para {account_name}")
                continue
            
            bot = DropeeBot(account_name, tg_web_data, proxy)
            bot.run_account()
            
            # Delay entre contas
            delay = random.randint(5, 15)
            print(f"⏳ Aguardando {delay}s antes da próxima conta...")
            await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"❌ Erro executando bot para {account_name}: {e}")
    
    print("✅ Execução concluída para todas as contas!")

if __name__ == "__main__":
    try:
        # Configurar encoding UTF-8
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass
    
    print("🤖 Dropee Bot Standalone")
    print("=" * 50)
    
    # Executar bot
    asyncio.run(run_bot())