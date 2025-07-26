# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import importlib
import random
import sys
import os
import json
import asyncio
from pathlib import Path
import threading
import hashlib
import time

import utilities.utilities as utilities
from FarmBot.FarmBot import FarmBot
from mcf_utils.api import API

# Constants
CHECK_INTERVAL = utilities.getConfig("check_interval", 3600)
MASTER_CRYPTO_FARM_BOT_DIR = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent

PYROGRAM_ACCOUNTS_FILE = os.path.join(
    MASTER_CRYPTO_FARM_BOT_DIR, "telegram_accounts/accounts.json"
)
MODULE_ACCOUNTS_FILE = os.path.join(MODULE_DIR, "accounts.json")
MODULE_DISABLED_SESSIONS_FILE = os.path.join(MODULE_DIR, "disabled_sessions.json")

CONFIG_ERROR_MSG = (
    "\033[31mEste módulo foi projetado para MasterCryptoFarmBot.\033[0m\n"
    "\033[31mVocê não pode executar este módulo como aplicação standalone.\033[0m\n"
    "\033[31mPor favor, instale o MasterCryptoFarmBot primeiro, depois coloque este módulo dentro do diretório modules.\033[0m\n"
    "\033[31mGitHub: \033[0m\033[32mhttps://github.com/masterking32/MasterCryptoFarmBot\033[0m"
)

sys.path.append(str(MASTER_CRYPTO_FARM_BOT_DIR))

try:
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
except Exception as e:
    pass

try:
    import mcf_utils.logColors as lc
    from mcf_utils.tgAccount import tgAccount

    config_path = os.path.join(MASTER_CRYPTO_FARM_BOT_DIR, "config.py")
    if not os.path.exists(config_path):
        print(CONFIG_ERROR_MSG)
        exit(1)

    spec = importlib.util.spec_from_file_location("config", config_path)
    cfg = importlib.util.module_from_spec(spec)
    sys.modules["config"] = cfg
    spec.loader.exec_module(cfg)

    from mcf_utils.database import Database
    from mcf_utils import utils
    from mcf_utils.api import API as MCF_API
except Exception as e:
    print(CONFIG_ERROR_MSG)
    print(f"Erro: {e}")
    exit(1)

async def check_cd(log, bot_globals):
    sleep_time = CHECK_INTERVAL
    if not module_available(log, bot_globals["license"], bot_globals["module_name"]):
        sleep_time = 600

    log.info(f"<y>💤 Verificando novamente em </y><c>{sleep_time}</c><y> segundos ...</y>")
    time.sleep(sleep_time)
    random_wait = random.randint(60, 120)
    log.info(f"<y>💤 Aguardando aleatoriamente por </y><c>{random_wait}</c><y> segundos ...</y>")
    await asyncio.sleep(random_wait)

# Edit the following variables
BOT_ID = "DropeeBot"
REFERRAL_TOKEN = "ref"
SHORT_APP_NAME = "Dropee"
APP_URL = "https://dropee.clicker-game-api.tropee.com"
VERSION_HASH = "v1.0.0"
# End of variables to edit

recent_checks = {}

def module_available(logger, license, module_name):
    if not license or not module_name:
        return False

    if not VERSION_HASH or VERSION_HASH == "":
        return True

    if (
        "status" in recent_checks
        and recent_checks["status"]
        and "date" in recent_checks
    ):
        if time.time() - recent_checks["date"] < 600:
            return recent_checks["status"]
    recent_checks["date"] = time.time()
    recent_checks["status"] = False

    apiObj = API(logger)
    data = {
        "action": "version_check",
        "module_name": module_name,
        "version": VERSION_HASH,
    }

    response = apiObj.get_task_answer(license, data)
    if "error" in response:
        logger.error(f"<y>⭕ Erro da API: {response['error']}</y>")
    elif "status" in response and response["status"] == "success":
        recent_checks["status"] = True
    elif (
        "status" in response and response["status"] == "error" and "message" in response
    ):
        logger.info(f"<y>🟡 {response['message']}</y>")
    else:
        logger.error(
            f"<y>🟡 Não foi possível verificar a versão do módulo, tente novamente mais tarde</y>"
        )

    return recent_checks["status"]

def load_json_file(file_path, default=None):
    try:
        if not os.path.exists(file_path):
            return default

        with open(file_path, "r", encoding="utf-8") as f:
            json_result = json.load(f)
            if not json_result or len(json_result) == 0:
                return default
            return json_result

    except Exception as e:
        pass

    return default

async def process_pg_account(account, bot_globals, log, group_id=None):
    try:
        if "disabled" in account and account["disabled"]:
            log.info(
                f"<y>🟨 Conta <c>{account['session_name']}</c> do grupo <c>{group_id}</c> está desabilitada!</y>"
            )
            return

        log.info(
            f"<g>🔆 Iniciando processamento da conta Pyrogram/Telethon <c>{account['session_name']}</c> do grupo <c>{group_id}</c> ...</g>"
        )

        if account.get("proxy") == "":
            account["proxy"] = None

        tg = tgAccount(
            bot_globals=bot_globals,
            log=log,
            accountName=account["session_name"],
            proxy=account["proxy"],
            BotID=BOT_ID,
            ReferralToken=REFERRAL_TOKEN,
            ShortAppName=SHORT_APP_NAME,
            AppURL=APP_URL,
        )

        web_app_data = await tg.run()
        if not web_app_data:
            utilities.inc_display_data(
                "display_data.json",
                "telegram_issues",
                {"title": "Problemas com Telegram", "name": "count"},
            )
            utilities.add_account_to_display_data(
                "display_data_telegram_issues.json", account["session_name"]
            )
            log.error(
                f"<r>└─ ❌ Conta <c>{account['session_name']}</c> do grupo <c>{group_id}</c> não está pronta! Não foi possível obter dados do WebApp.</r>"
            )
            return

        web_app_query = utils.extract_tg_query_from_url(web_app_data)
        if not web_app_query:
            utilities.add_account_to_display_data(
                "display_data_telegram_issues.json", account["session_name"]
            )
            utilities.inc_display_data(
                "display_data.json",
                "telegram_issues",
                {"title": "Problemas com Telegram", "name": "count"},
            )
            log.error(
                f"<r>└─ ❌ Query do WebApp da conta <c>{account['session_name']}</c> do grupo <c>{group_id}</c> não é válida!</r>"
            )
            return

        log.info(
            f"<g>└─ ✅ Conta <c>{account['session_name']}</c> do grupo <c>{group_id}</c> está pronta!</g>"
        )
        fb = FarmBot(
            log=log,
            bot_globals=bot_globals,
            account_name=account["session_name"],
            web_app_query=web_app_query,
            proxy=account["proxy"],
            user_agent=account["user_agent"],
            isPyrogram=True,
            tgAccount=tg,
        )

        await fb.run()
    except Exception as e:
        log.error(
            f"<r>❌ Conta <c>{account['session_name']}</c> do grupo <c>{group_id}</c>, Erro ao processar conta Pyrogram/Telethon: {e}</r>"
        )
        return False
    finally:
        log.info(
            f"<g>✅ Conta Pyrogram/Telethon <c>{account['session_name']}</c> do grupo <c>{group_id}</c> foi processada.</g>"
        )

async def process_module_account(account, bot_globals, log, group_id=None):
    try:
        proxy = account.get("proxy")
        if proxy == "":
            proxy = None

        account_name = account.get("session_name")
        web_app_data = account.get("web_app_data")

        log.info(
            f"<g>🔆 Iniciando processamento da conta do módulo <c>{account_name}</c> do grupo <c>{group_id}</c></g>"
        )

        user_agent = account.get("user_agent")
        if account.get("disabled"):
            log.info(
                f"<y>❌ Conta <c>{account_name}</c> do grupo <c>{group_id}</c> está desabilitada!</y>"
            )
            return

        if not web_app_data:
            log.error(
                f"<r>❌ Conta <c>{account_name}</c> do grupo <c>{group_id}</c> dados do WebApp estão vazios!</r>"
            )
            return

        web_app_query = utils.extract_tg_query_from_url(web_app_data)
        if not web_app_query:
            log.error(
                f"<r>❌ Query do WebApp da conta {account_name} do grupo <c>{group_id}</c> não é válida!</r>"
            )
            return

        fb = FarmBot(
            log=log,
            bot_globals=bot_globals,
            account_name=account_name,
            web_app_query=web_app_query,
            proxy=proxy,
            user_agent=user_agent,
            isPyrogram=False,
        )
        await fb.run()
    except Exception as e:
        log.error(
            f"<r>❌ Conta {account_name} do grupo <c>{group_id}</c> Erro ao processar conta do módulo: {e}</r>"
        )
        return False
    finally:
        log.info(
            f"<g>✅ Conta do módulo <c>{account_name}</c> do grupo <c>{group_id}</c> foi processada.</g>"
        )

async def handle_accounts(group_id, accounts, bot_globals, log):
    try:
        log.info(
            f"<g>🖥️ Iniciando processamento do grupo <c>{group_id}</c> com <c>{len(accounts)}</c> contas ...</g>"
        )

        for account in accounts:
            try:
                module_status = module_available(
                    log, bot_globals["license"], bot_globals["module_name"]
                )
                if not module_status:
                    log.error(
                        f"<r>❌ Módulo <c>{bot_globals['module_name']}</c> API foi alterada. Aguarde uma atualização.</r>"
                    )
                    return

                if account["is_pyrogram"]:
                    await process_pg_account(account, bot_globals, log, group_id)
                else:
                    await process_module_account(account, bot_globals, log, group_id)
            except Exception as e:
                log.error(
                    f"<r>❌ Erro ao processar conta do grupo <c>{group_id}</c>: {e}</r>"
                )
                continue
    except Exception as e:
        log.error(f"<r>❌ Erro ao processar contas do grupo <c>{group_id}</c>: {e}</r>")
    finally:
        log.info(
            f"<g>🔚 Grupo <c>{group_id}</c> com <c>{len(accounts)}</c> contas foi processado. Aguardando outras tarefas do grupo terminarem</g>"
        )

    await asyncio.sleep(5)

def load_accounts():
    pyrogram_accounts_count = 0
    module_accounts_count = 0
    all_accounts = []
    disabled_accounts = load_json_file(MODULE_DISABLED_SESSIONS_FILE, [])

    try:
        pyrogram_accounts = load_json_file(PYROGRAM_ACCOUNTS_FILE, None)
        if pyrogram_accounts is not None:
            for account in pyrogram_accounts:
                if account.get("disabled", False):
                    utilities.inc_display_data(
                        "display_data.json",
                        "disabled_accounts",
                        {"title": "Contas Desabilitadas", "name": "count"},
                    )
                    continue

                if account["session_name"] in disabled_accounts:
                    utilities.inc_display_data(
                        "display_data.json",
                        "disabled_accounts",
                        {"title": "Contas Desabilitadas", "name": "count"},
                    )
                    continue

                pyrogram_accounts_count += 1
                account["is_pyrogram"] = True
                all_accounts.append(account)

        module_accounts = load_json_file(MODULE_ACCOUNTS_FILE, None)
        if module_accounts is not None:
            for account in module_accounts:
                if account.get("disabled", False):
                    utilities.inc_display_data(
                        "display_data.json",
                        "disabled_accounts",
                        {"title": "Contas Desabilitadas", "name": "count"},
                    )
                    continue

                module_accounts_count += 1
                account["is_pyrogram"] = False
                all_accounts.append(account)
    except Exception as e:
        pass

    return pyrogram_accounts_count, module_accounts_count, all_accounts

def group_by_proxy(accounts):
    proxies = {}
    for account in accounts:
        proxy = account.get("proxy")
        if proxy is None:
            proxy = "None"

        proxy_hash = hashlib.md5(proxy.encode()).hexdigest()

        if proxy_hash not in proxies:
            proxies[proxy_hash] = []
        proxies[proxy_hash].append(account)

    return proxies

async def main():
    utilities.clean_logs()
    module_dir = Path(__file__).resolve().parent
    module_name = module_dir.name
    log = lc.getLogger(str(module_dir / "bot.log"), module_name)

    mcf_pid = None
    if len(sys.argv) > 1:
        mcf_pid = sys.argv[1]
        threading.Thread(
            target=utilities.check_mcf_status, args=(log, mcf_pid, module_name)
        ).start()
    else:
        log.error(
            "<red>❌ Por favor, execute o bot com o script MasterCryptoFarmBot!❌</red>"
        )

    log.info(f"<g>🔧 Módulo {module_name} está iniciando ...</g>")

    bot_globals = {
        "module_name": module_name,
        "mcf_dir": str(MASTER_CRYPTO_FARM_BOT_DIR),
        "module_dir": str(module_dir),
    }

    db_location = os.path.join(MASTER_CRYPTO_FARM_BOT_DIR, "database.db")
    db = Database(db_location, log)
    license_key = db.getSettings("license", None)
    if license_key is None or license_key == "":
        log.error("<r>❌ Chave de licença não está definida!</r>")
        exit(1)
    else:
        log.info(f"<g>🔑 Chave de licença: </g><c>{utils.hide_text(license_key)}</c>")

    bot_globals["license"] = license_key
    bot_globals["config"] = cfg.config
    apiObj = MCF_API(log)
    modules = apiObj.get_user_modules(license_key)

    if modules is None or "error" in modules:
        log.error(f"<r>❌ Não foi possível obter módulos: {modules['error']}</r>")
        exit(1)

    module_found = False
    for module in modules:
        if module["name"] == module_name:
            module_found = True
            break

    if not module_found:
        log.error(f"<r>❌ Módulo {module_name} não foi encontrado na licença!</r>")
        exit(1)

    log.info(f"<g>📦 Módulo {module_name} foi encontrado na licença!</g>")

    if utilities.is_module_disabled(bot_globals, log):
        log.info(f"<r>🚫 Módulo {module_name} está desabilitado!</r>")
        exit(0)

    bot_globals["telegram_api_id"] = cfg.config["telegram_api"]["api_id"]
    bot_globals["telegram_api_hash"] = cfg.config["telegram_api"]["api_hash"]

    while True:
        try:
            log.info("<g>🔍 Verificando contas ...</g>")

            utilities.clear_display_data("display_data.json")
            utilities.clear_display_data("display_data_telegram_issues.json")
            utilities.clear_display_data("display_data_bot_issues.json")
            utilities.clear_display_data("display_data_success_accounts.json")

            pyrogram_accounts, module_accounts, all_accounts = load_accounts()
            if all_accounts is None or len(all_accounts) == 0:
                log.info("<y>🟠 Nenhuma conta encontrada!</y>")
                await check_cd(log, bot_globals)
                continue

            log.info(
                f"<g>👥 Encontradas <c>{len(all_accounts)}</c> contas: <c>{pyrogram_accounts}</c> contas Pyrogram/Telethon, <c>{module_accounts}</c> contas do módulo.</g>"
            )

            utilities.update_display_data(
                "display_data.json",
                "active_accounts",
                {"title": "Contas Ativas", "count": len(all_accounts)},
            )

            utilities.update_display_data(
                "display_data.json",
                "pyrogram_accounts",
                {"title": "Contas Pyrogram/Telethon", "count": pyrogram_accounts},
            )

            utilities.update_display_data(
                "display_data.json",
                "module_accounts",
                {"title": "Contas do Módulo", "count": module_accounts},
            )

            utilities.update_display_data(
                "display_data.json",
                "success_accounts",
                {"title": "Contas com farm finalizado com sucesso", "count": 0},
            )

            if pyrogram_accounts > 0 and (
                bot_globals["telegram_api_id"] == 1234
                or bot_globals["telegram_api_hash"] == ""
            ):
                log.error(
                    "<r>❌ API ID e API Hash do Telegram não estão definidos no arquivo de configuração!</r>"
                )
                return False

            grouped_accounts = group_by_proxy(all_accounts)

            utilities.update_display_data(
                "display_data.json",
                "proxy_groups",
                {"title": "Grupos de Proxy", "count": len(grouped_accounts)},
            )

            utilities.update_display_data(
                "display_data.json",
                "telegram_issues",
                {"title": "Problemas com Telegram", "count": 0},
            )

            log.info(
                f"<g>🔄 Contas foram agrupadas em <c>{len(grouped_accounts)}</c> baseado em seus proxies. Cada grupo será executado em uma thread separada.</g>"
            )

            group_id = 1
            log.info("<g>👥 Detalhes dos grupos de contas:</g>")
            log.info(
                "<g>└──────────────────────────────────────────────────────────────</g>"
            )
            try:
                for _, accounts in grouped_accounts.items():
                    first_account_proxy = accounts[0].get("proxy", "UNSET")
                    if first_account_proxy is None or first_account_proxy == "":
                        first_account_proxy = "UNSET"

                    hide_chars = (
                        0
                        if first_account_proxy == "UNSET"
                        else min(10, int(len(first_account_proxy) / 2))
                    )

                    log.info(
                        f"<g>└─🔗 Grupo <c>{group_id}</c> tem <c>{len(accounts)}</c> contas com proxy <c>{utils.hide_text(first_account_proxy,hide_chars)}</c>:</g>"
                    )
                    for account in accounts:
                        log.info(f"<g>│  ├─ <c>{account['session_name']}</c></g>")

                    group_id += 1

                    log.info(
                        "<g>└──────────────────────────────────────────────────────────────</g>"
                    )
            except Exception as e:
                log.error(f"<r>❌ Erro ao agrupar contas: {e}</r>")
                await check_cd(log, bot_globals)
                continue

            tasks = []
            max_threads = min(
                utilities.getConfig("max_threads", 5), len(grouped_accounts)
            )
            log.info(
                f"<g>🚀 Iniciando processamento de contas com máximo de <c>{max_threads}</c> threads ...</g>"
            )

            await asyncio.sleep(5)
            group_id = 1
            for _, accounts in grouped_accounts.items():
                try:
                    while len(tasks) >= max_threads:
                        for task in tasks:
                            if not task.is_alive():
                                tasks.remove(task)
                                break

                        await asyncio.sleep(5)

                except Exception as e:
                    log.error(f"<r>❌ Erro ao aguardar tarefas: {e}</r>")
                    await asyncio.sleep(30)
                    continue

                try:
                    task = threading.Thread(
                        target=lambda: asyncio.run(
                            handle_accounts(group_id, accounts, bot_globals, log)
                        )
                    )
                    task.start()
                    tasks.append(task)
                    group_id += 1
                except Exception as e:
                    log.error(f"<r>❌ Erro ao criar tarefa: {e}</r>")
                    await asyncio.sleep(30)
                    continue

            try:
                for task in tasks:
                    task.join()
            except Exception as e:
                log.error(f"<r>❌ Erro ao aguardar tarefas: {e}</r>")
                await asyncio.sleep(30)
                continue

            log.info(
                "<g>✅ Todas as contas e grupos foram processados com sucesso. Aguardando próxima verificação ...</g>"
            )
            await check_cd(log, bot_globals)
        except Exception as e:
            log.error(f"<r>❌ Erro ao processar contas Pyrogram/Telethon: {e}</r>")
            await check_cd(log, bot_globals)
        except KeyboardInterrupt:
            log.info(f"<r>🛑 Módulo do Bot interrompido pelo usuário ...</r>")
            break

if __name__ == "__main__":
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"{lc.r}🛑 Módulo do Bot interrompido pelo usuário ... {lc.rs}")
    except Exception as e:
        print(f"{lc.r}🛑 Módulo do Bot parou com erro: {e} ... {lc.rs}")

    try:
        os._exit(0)
    except Exception as e:
        print(f"{lc.r}🛑 Erro ao parar o bot: {e} ... {lc.rs}")
        exit()