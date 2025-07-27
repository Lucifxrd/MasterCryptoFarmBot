#!/usr/bin/env python3
# Advanced Standalone Dropee Bot - Versão avançada com mais funcionalidades
# Desenvolvido a partir do código original do MasterkinG32

import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import cloudscraper
import requests

# Configurações básicas
MODULE_DIR = Path(__file__).resolve().parent
ACCOUNTS_FILE = os.path.join(MODULE_DIR, "accounts.json")
TOKENS_FILE = os.path.join(MODULE_DIR, "tokens.json")
CONFIG_FILE = os.path.join(MODULE_DIR, "config.json")
STATS_FILE = os.path.join(MODULE_DIR, "stats.json")

# Configurações padrão expandidas
DEFAULT_CONFIG = {
    "check_interval": 3600,
    "auto_claim_daily_reward": True,
    "auto_farming": True,
    "auto_tasks": True,
    "auto_wheel": True,
    "auto_upgrade": False,
    "delay_min": 5,
    "delay_max": 15,
    "max_retries": 3,
    "use_random_delays": True,
    "log_level": "INFO"
}

class AdvancedLogger:
    """Logger avançado com diferentes níveis e cores"""
    
    def __init__(self, name="DropeeBot", level="INFO"):
        self.logger = logging.getLogger(name)
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR
        }
        self.logger.setLevel(level_map.get(level, logging.INFO))
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message):
        clean_msg = self._clean_message(message)
        self.logger.info(clean_msg)
    
    def error(self, message):
        clean_msg = self._clean_message(message)
        self.logger.error(clean_msg)
    
    def warning(self, message):
        clean_msg = self._clean_message(message)
        self.logger.warning(clean_msg)
    
    def debug(self, message):
        clean_msg = self._clean_message(message)
        self.logger.debug(clean_msg)
    
    def success(self, message):
        clean_msg = self._clean_message(message)
        self.logger.info(f"✅ {clean_msg}")
    
    def _clean_message(self, message):
        import re
        clean = re.sub(r'<[^>]*>', '', str(message))
        clean = re.sub(r'\033\[[0-9;]*m', '', clean)
        return clean

class StatsManager:
    """Gerenciador de estatísticas do bot"""
    
    @staticmethod
    def load_stats():
        """Carregar estatísticas salvas"""
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    @staticmethod
    def save_stats(stats):
        """Salvar estatísticas"""
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f, indent=4)
            return True
        except:
            return False
    
    @staticmethod
    def update_account_stats(account_name, action, amount=0):
        """Atualizar estatísticas de uma conta"""
        stats = StatsManager.load_stats()
        
        if account_name not in stats:
            stats[account_name] = {
                "daily_rewards": 0,
                "farming_claims": 0,
                "tasks_completed": 0,
                "total_earned": 0,
                "last_update": datetime.now().isoformat()
            }
        
        account_stats = stats[account_name]
        
        if action == "daily_reward":
            account_stats["daily_rewards"] += 1
            account_stats["total_earned"] += amount
        elif action == "farming":
            account_stats["farming_claims"] += 1
            account_stats["total_earned"] += amount
        elif action == "task":
            account_stats["tasks_completed"] += 1
            account_stats["total_earned"] += amount
        
        account_stats["last_update"] = datetime.now().isoformat()
        StatsManager.save_stats(stats)

class AdvancedHttpRequest:
    """Cliente HTTP avançado com retry e melhor tratamento de erros"""
    
    def __init__(self, log, proxy=None, user_agent=None, tg_web_data=None, account_name=None, max_retries=3):
        self.log = log
        self.proxy = proxy
        self.user_agent = user_agent or "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.3"
        self.max_retries = max_retries
        
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
            "accept-language": "pt-BR,pt;q=0.9,en;q=0.8",
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
    
    def _make_request(self, method, url, domain="game", data=None, headers=None, auth_header=True):
        """Método genérico para fazer requisições com retry"""
        for attempt in range(self.max_retries):
            try:
                url = self._fix_url(url, domain)
                default_headers = self._get_default_headers()
                
                if headers:
                    default_headers.update(headers)
                
                if auth_header and self.authToken:
                    default_headers["authorization"] = f"Bearer {self.authToken}"
                
                if method == "GET":
                    response = self.scraper.get(
                        url=url,
                        headers=default_headers,
                        proxies=self._get_proxy(),
                        timeout=30,
                    )
                elif method == "POST":
                    response = self.scraper.post(
                        url=url,
                        json=data,
                        headers=default_headers,
                        proxies=self._get_proxy(),
                        timeout=30,
                    )
                else:
                    return None
                
                # Renovar token se necessário
                if response.status_code == 401 and self.renew_access_token():
                    self.log.info("🔄 Token renovado, tentando novamente...")
                    TokenManager.save_auth_token(self.account_name, self.authToken, self.RefreshToken)
                    continue
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    self.log.warning(f"⏰ Rate limit, aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.log.debug(f"Erro HTTP {response.status_code}: {response.text}")
                    return None
                
            except requests.exceptions.Timeout:
                self.log.warning(f"⏰ Timeout na tentativa {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            except Exception as e:
                self.log.error(f"Erro na requisição {method} {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
        
        return None
    
    def get(self, url, domain="game", headers=None, auth_header=True, **kwargs):
        return self._make_request("GET", url, domain, None, headers, auth_header)
    
    def post(self, url, domain="game", data=None, headers=None, auth_header=True, **kwargs):
        return self._make_request("POST", url, domain, data, headers, auth_header)
    
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

class TokenManager:
    """Gerenciador de tokens com funcionalidades expandidas"""
    
    @staticmethod
    def save_auth_token(session_name, access_token=None, refresh_token=None):
        if session_name is None:
            return False
        try:
            data = UtilityFunctions.read_json_file(TOKENS_FILE, {})
            data[session_name] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "last_update": datetime.now().isoformat()
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
    
    @staticmethod
    def is_token_expired(session_name, hours=6):
        """Verificar se o token está expirado"""
        try:
            token_data = TokenManager.get_auth_token(session_name)
            if not token_data or "last_update" not in token_data:
                return True
            
            last_update = datetime.fromisoformat(token_data["last_update"])
            expiry_time = last_update + timedelta(hours=hours)
            
            return datetime.now() > expiry_time
        except:
            return True

class UtilityFunctions:
    """Funções utilitárias expandidas"""
    
    @staticmethod
    def getConfig(key, default=None):
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
        if not os.path.exists(json_file):
            return default
        try:
            with open(json_file, "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return default
    
    @staticmethod
    def save_json_file(json_file, data):
        try:
            with open(json_file, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def random_delay(min_sec=1, max_sec=5):
        """Delay aleatório para parecer mais humano"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay

class AdvancedDropeeGame:
    """Classe expandida para interagir com o jogo Dropee"""
    
    def __init__(self, log, http_request, account_name):
        self.log = log
        self.http = http_request
        self.account_name = account_name
    
    def get_balance(self):
        """Obter saldo detalhado do jogador"""
        try:
            response = self.http.get("/api/v1/user/balance")
            if response:
                self.log.debug(f"Saldo obtido: {response}")
                return response
            return None
        except Exception as e:
            self.log.error(f"Erro ao obter saldo: {e}")
            return None
    
    def get_user_info(self):
        """Obter informações do usuário"""
        try:
            response = self.http.get("/api/v1/user")
            if response:
                return response
            return None
        except Exception as e:
            self.log.error(f"Erro ao obter info do usuário: {e}")
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
            if response:
                reward_amount = response.get("amount", 0)
                StatsManager.update_account_stats(self.account_name, "daily_reward", reward_amount)
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
            if response:
                reward_amount = response.get("amount", 0)
                StatsManager.update_account_stats(self.account_name, "farming", reward_amount)
            return response
        except Exception as e:
            return None
    
    def get_tasks(self):
        """Obter lista de tarefas disponíveis"""
        try:
            response = self.http.get("/api/v1/tasks")
            return response
        except Exception as e:
            self.log.error(f"Erro ao obter tarefas: {e}")
            return None
    
    def complete_task(self, task_id):
        """Completar uma tarefa específica"""
        try:
            data = {"taskId": task_id}
            response = self.http.post("/api/v1/tasks/complete", data=data)
            if response:
                reward_amount = response.get("reward", 0)
                StatsManager.update_account_stats(self.account_name, "task", reward_amount)
            return response
        except Exception as e:
            self.log.error(f"Erro ao completar tarefa {task_id}: {e}")
            return None
    
    def get_wheel_info(self):
        """Obter informações da roda da fortuna"""
        try:
            response = self.http.get("/api/v1/wheel")
            return response
        except Exception as e:
            return None
    
    def spin_wheel(self):
        """Girar roda da fortuna"""
        try:
            response = self.http.post("/api/v1/wheel/spin")
            return response
        except Exception as e:
            return None

class AdvancedDropeeBot:
    """Bot avançado do Dropee com funcionalidades expandidas"""
    
    def __init__(self, account_name, tg_web_data, proxy=None, config=None):
        self.account_name = account_name
        self.config = config or DEFAULT_CONFIG
        
        log_level = self.config.get("log_level", "INFO")
        self.log = AdvancedLogger(f"DropeeBot-{account_name}", log_level)
        
        max_retries = self.config.get("max_retries", 3)
        self.http = AdvancedHttpRequest(self.log, proxy, None, tg_web_data, account_name, max_retries)
        self.game = AdvancedDropeeGame(self.log, self.http, account_name)
        
        self.session_stats = {
            "start_time": datetime.now(),
            "actions_performed": 0,
            "errors_encountered": 0
        }
    
    def run_account(self):
        """Executar bot para uma conta específica com funcionalidades avançadas"""
        self.log.info(f"🚀 Iniciando bot avançado para {self.account_name}")
        
        try:
            # Verificar se token está expirado
            if TokenManager.is_token_expired(self.account_name):
                self.log.info("🔄 Token expirado, renovando...")
                self.http.authToken = None
            
            # Tentar autenticação
            if not self.http.authToken and not self.http.auth_telegram():
                self.log.error(f"❌ Falha na autenticação para {self.account_name}")
                return False
            
            # Delay aleatório no início
            if self.config.get("use_random_delays", True):
                delay = UtilityFunctions.random_delay(1, 3)
                self.log.debug(f"⏳ Delay inicial: {delay:.1f}s")
            
            # Obter informações do usuário
            user_info = self.game.get_user_info()
            if user_info:
                self.log.info(f"👤 Usuário: {user_info.get('username', 'N/A')}")
            
            # Verificar saldo
            balance = self.game.get_balance()
            if balance:
                available_balance = balance.get('availableBalance', 0)
                play_passes = balance.get('playPasses', 0)
                self.log.info(f"💰 Saldo: {available_balance}")
                self.log.info(f"🎫 Play Passes: {play_passes}")
            
            # Executar ações configuradas
            success_count = 0
            
            if self.config.get("auto_claim_daily_reward", True):
                if self.handle_daily_reward():
                    success_count += 1
                self._random_delay()
            
            if self.config.get("auto_farming", True):
                if self.handle_farming():
                    success_count += 1
                self._random_delay()
            
            if self.config.get("auto_tasks", True):
                completed_tasks = self.handle_tasks()
                success_count += completed_tasks
                self._random_delay()
            
            if self.config.get("auto_wheel", True):
                if self.handle_wheel():
                    success_count += 1
                self._random_delay()
            
            # Verificar saldo final
            final_balance = self.game.get_balance()
            if final_balance and balance:
                initial = balance.get('availableBalance', 0)
                final = final_balance.get('availableBalance', 0)
                earned = final - initial
                if earned > 0:
                    self.log.success(f"💎 Ganhou {earned} nesta sessão!")
            
            self.session_stats["actions_performed"] = success_count
            self.log.success(f"✅ Execução concluída para {self.account_name} ({success_count} ações)")
            
            return True
            
        except Exception as e:
            self.log.error(f"❌ Erro na execução para {self.account_name}: {e}")
            self.session_stats["errors_encountered"] += 1
            return False
    
    def handle_daily_reward(self):
        """Gerenciar recompensa diária com mais detalhes"""
        try:
            daily_reward = self.game.get_daily_reward()
            if daily_reward and daily_reward.get("canClaim"):
                result = self.game.claim_daily_reward()
                if result:
                    amount = result.get("amount", 0)
                    self.log.success(f"🎁 Recompensa diária reivindicada! (+{amount})")
                    return True
                else:
                    self.log.error("❌ Falha ao reivindicar recompensa diária")
            else:
                next_claim = daily_reward.get("nextClaimTime") if daily_reward else None
                if next_claim:
                    self.log.info(f"⏰ Próxima recompensa diária: {next_claim}")
                else:
                    self.log.info("⏰ Recompensa diária não disponível ainda")
        except Exception as e:
            self.log.error(f"Erro na recompensa diária: {e}")
        return False
    
    def handle_farming(self):
        """Gerenciar farming com mais detalhes"""
        try:
            farming_info = self.game.get_farming_info()
            if not farming_info:
                # Tentar iniciar farming
                start_result = self.game.start_farming()
                if start_result:
                    end_time = start_result.get("endTime")
                    self.log.success(f"🌱 Farming iniciado! Termina em: {end_time}")
                    return True
                else:
                    self.log.error("❌ Falha ao iniciar farming")
                return False
            
            # Verificar se pode reivindicar
            if farming_info.get("canClaim"):
                claim_result = self.game.claim_farming()
                if claim_result:
                    amount = claim_result.get("amount", 0)
                    self.log.success(f"🚜 Farming reivindicado! (+{amount})")
                    
                    # Tentar iniciar novo ciclo
                    start_result = self.game.start_farming()
                    if start_result:
                        end_time = start_result.get("endTime")
                        self.log.success(f"🌱 Novo ciclo de farming iniciado! Termina em: {end_time}")
                    return True
                else:
                    self.log.error("❌ Falha ao reivindicar farming")
            else:
                end_time = farming_info.get("endTime")
                self.log.info(f"⏰ Farming em andamento, termina em: {end_time}")
                
        except Exception as e:
            self.log.error(f"Erro no farming: {e}")
        return False
    
    def handle_tasks(self):
        """Gerenciar tarefas automaticamente"""
        completed_count = 0
        try:
            tasks = self.game.get_tasks()
            if not tasks:
                self.log.info("📋 Nenhuma tarefa disponível")
                return 0
            
            available_tasks = tasks.get("tasks", [])
            self.log.info(f"📋 {len(available_tasks)} tarefas encontradas")
            
            for task in available_tasks:
                try:
                    task_id = task.get("id")
                    task_name = task.get("name", "Tarefa sem nome")
                    task_reward = task.get("reward", 0)
                    is_completed = task.get("isCompleted", False)
                    can_complete = task.get("canComplete", False)
                    
                    if is_completed:
                        self.log.debug(f"✅ Tarefa já completada: {task_name}")
                        continue
                    
                    if not can_complete:
                        self.log.debug(f"⏳ Tarefa não pode ser completada ainda: {task_name}")
                        continue
                    
                    self.log.info(f"🎯 Tentando completar: {task_name} (Recompensa: {task_reward})")
                    
                    result = self.game.complete_task(task_id)
                    if result:
                        actual_reward = result.get("reward", task_reward)
                        self.log.success(f"✅ Tarefa completada: {task_name} (+{actual_reward})")
                        completed_count += 1
                        
                        # Delay entre tarefas
                        self._random_delay(0.5, 2)
                    else:
                        self.log.warning(f"❌ Falha ao completar: {task_name}")
                    
                except Exception as e:
                    self.log.error(f"Erro ao processar tarefa: {e}")
                    continue
            
            if completed_count > 0:
                self.log.success(f"🎯 {completed_count} tarefas completadas!")
            else:
                self.log.info("📋 Nenhuma tarefa nova foi completada")
                
        except Exception as e:
            self.log.error(f"Erro ao gerenciar tarefas: {e}")
        
        return completed_count
    
    def handle_wheel(self):
        """Gerenciar roda da fortuna"""
        try:
            wheel_info = self.game.get_wheel_info()
            if not wheel_info:
                self.log.info("🎰 Roda da fortuna não disponível")
                return False
            
            can_spin = wheel_info.get("canSpin", False)
            spins_left = wheel_info.get("spinsLeft", 0)
            
            if not can_spin or spins_left <= 0:
                next_spin_time = wheel_info.get("nextSpinTime")
                self.log.info(f"🎰 Próximo giro da roda: {next_spin_time}")
                return False
            
            self.log.info(f"🎰 Girando roda da fortuna... ({spins_left} giros restantes)")
            
            spin_result = self.game.spin_wheel()
            if spin_result:
                prize = spin_result.get("prize", "Desconhecido")
                amount = spin_result.get("amount", 0)
                self.log.success(f"🎰 Roda girada! Prêmio: {prize} (+{amount})")
                return True
            else:
                self.log.error("❌ Falha ao girar roda da fortuna")
                
        except Exception as e:
            self.log.error(f"Erro na roda da fortuna: {e}")
        return False
    
    def _random_delay(self, min_sec=None, max_sec=None):
        """Aplicar delay aleatório se configurado"""
        if not self.config.get("use_random_delays", True):
            return
        
        min_delay = min_sec or self.config.get("delay_min", 1)
        max_delay = max_sec or self.config.get("delay_max", 3)
        
        delay = UtilityFunctions.random_delay(min_delay, max_delay)
        self.log.debug(f"⏳ Delay: {delay:.1f}s")

def create_advanced_example_accounts():
    """Criar arquivo de exemplo avançado para contas"""
    example_accounts = {
        "conta_principal": {
            "telegram_data": "query_id=AAAA...&user=%7B%22id%22%3A...",
            "proxy": None,
            "enabled": True,
            "notes": "Conta principal sem proxy"
        },
        "conta_secundaria": {
            "telegram_data": "query_id=BBBB...&user=%7B%22id%22%3A...",
            "proxy": "http://usuario:senha@proxy:porta",
            "enabled": True,
            "notes": "Conta com proxy"
        },
        "conta_desabilitada": {
            "telegram_data": "query_id=CCCC...&user=%7B%22id%22%3A...",
            "proxy": None,
            "enabled": False,
            "notes": "Conta temporariamente desabilitada"
        }
    }
    
    example_file = os.path.join(MODULE_DIR, "accounts_example.json")
    UtilityFunctions.save_json_file(example_file, example_accounts)
    print(f"📝 Arquivo de exemplo avançado criado: {example_file}")

def show_stats():
    """Mostrar estatísticas das contas"""
    stats = StatsManager.load_stats()
    if not stats:
        print("📊 Nenhuma estatística disponível ainda")
        return
    
    print("\n📊 ESTATÍSTICAS DAS CONTAS")
    print("=" * 50)
    
    for account_name, account_stats in stats.items():
        print(f"\n👤 {account_name}:")
        print(f"   🎁 Recompensas diárias: {account_stats.get('daily_rewards', 0)}")
        print(f"   🚜 Farmings coletados: {account_stats.get('farming_claims', 0)}")
        print(f"   🎯 Tarefas completadas: {account_stats.get('tasks_completed', 0)}")
        print(f"   💰 Total ganho: {account_stats.get('total_earned', 0)}")
        print(f"   🕐 Última atualização: {account_stats.get('last_update', 'N/A')}")

async def run_advanced_bot():
    """Função principal para executar o bot avançado"""
    print("🤖 Dropee Bot Standalone Avançado")
    print("=" * 50)
    
    # Verificar argumentos de linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats":
            show_stats()
            return
        elif sys.argv[1] == "--create-example":
            create_advanced_example_accounts()
            return
    
    # Verificar se existe arquivo de contas
    if not os.path.exists(ACCOUNTS_FILE):
        print("❌ Arquivo accounts.json não encontrado!")
        print("📝 Criando arquivo de exemplo avançado...")
        create_advanced_example_accounts()
        print(f"✏️ Edite o arquivo {ACCOUNTS_FILE} com suas contas do Telegram")
        return
    
    # Carregar configurações
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        loaded_config = UtilityFunctions.read_json_file(CONFIG_FILE, {})
        config.update(loaded_config)
    else:
        UtilityFunctions.save_json_file(CONFIG_FILE, config)
        print(f"⚙️ Arquivo de configuração criado: {CONFIG_FILE}")
    
    # Carregar contas
    accounts = UtilityFunctions.read_json_file(ACCOUNTS_FILE, {})
    if not accounts:
        print("❌ Nenhuma conta encontrada no arquivo accounts.json")
        return
    
    # Filtrar contas habilitadas
    enabled_accounts = {name: data for name, data in accounts.items() 
                       if data.get("enabled", True)}
    
    if not enabled_accounts:
        print("❌ Nenhuma conta habilitada encontrada")
        return
    
    print(f"🚀 Iniciando bot para {len(enabled_accounts)} contas habilitadas...")
    
    successful_runs = 0
    failed_runs = 0
    
    # Executar bot para cada conta habilitada
    for account_name, account_data in enabled_accounts.items():
        try:
            tg_web_data = account_data.get("telegram_data")
            proxy = account_data.get("proxy")
            
            if not tg_web_data:
                print(f"❌ Dados do Telegram ausentes para {account_name}")
                failed_runs += 1
                continue
            
            print(f"\n🔄 Processando {account_name}...")
            
            bot = AdvancedDropeeBot(account_name, tg_web_data, proxy, config)
            success = bot.run_account()
            
            if success:
                successful_runs += 1
            else:
                failed_runs += 1
            
            # Delay entre contas
            if account_name != list(enabled_accounts.keys())[-1]:  # Não delay na última conta
                delay = random.randint(
                    config.get("delay_min", 5), 
                    config.get("delay_max", 15)
                )
                print(f"⏳ Aguardando {delay}s antes da próxima conta...")
                await asyncio.sleep(delay)
            
        except Exception as e:
            print(f"❌ Erro executando bot para {account_name}: {e}")
            failed_runs += 1
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA EXECUÇÃO")
    print(f"✅ Sucessos: {successful_runs}")
    print(f"❌ Falhas: {failed_runs}")
    print(f"📈 Taxa de sucesso: {(successful_runs/(successful_runs+failed_runs)*100):.1f}%")
    print("=" * 50)
    
    # Mostrar estatísticas
    show_stats()

if __name__ == "__main__":
    try:
        # Configurar encoding UTF-8
        if sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass
    
    # Executar bot
    asyncio.run(run_advanced_bot())