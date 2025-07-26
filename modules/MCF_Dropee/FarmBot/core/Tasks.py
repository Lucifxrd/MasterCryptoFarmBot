# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import asyncio
import json
import random
import time
from .Wallet import Wallet
from .Game import Game
from utilities.utilities import getConfig
from mcf_utils.tgAccount import tgAccount as TG
from mcf_utils.api import API

class Tasks:
    def __init__(
        self,
        log,
        httpRequest,
        account_name,
        bot_globals,
        tgAccount=None,
        license_key=None,
    ):
        self.log = log
        self.http = httpRequest
        self.account_name = account_name
        self.tgAccount = tgAccount
        self.recheck_claim = False
        self.license_key = license_key
        self.bot_globals = bot_globals
        self.processed_tasks = []
        self.game = Game(self.log, self.http, self.account_name)
        self.total_recheck = 0

    async def claim_tasks(self):
        try:
            if self.total_recheck > 3:
                return False

            self.total_recheck += 1
            self.recheck_claim = False
            self.log.info(
                f"<g>📃 Reivindicando tarefas para a conta <cyan>{self.account_name}</cyan>...</g>"
            )

            self.processed_tasks = []
            tasks_list = self.get_tasks()
            if tasks_list is None:
                return False

            for section in tasks_list:
                if "tasks" in section:
                    for task in section["tasks"]:
                        await self.handle_task(task)

                if self.recheck_claim:
                    time.sleep(random.randint(5, 10))
                    return await self.claim_tasks()

                if "subSections" in section:
                    for sub_section in section["subSections"]:
                        await self.handle_sub_section(sub_section)

            if self.recheck_claim:
                time.sleep(random.randint(5, 10))
                self.log.info(
                    f"<g>📃 Reverificando tarefas para a conta <cyan>{self.account_name}</cyan>...</g>"
                )
                return await self.claim_tasks()

            self.log.info(
                f"<g>✅ Tarefas reivindicadas para a conta <cyan>{self.account_name}</cyan>!</g>"
            )

            return True
        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao reivindicar tarefas!</r>")
            return False

    async def handle_task(self, task):
        try:
            if ("isHidden" in task and task["isHidden"]) or "type" not in task:
                return

            task_id = task.get("id")
            task_status = task.get("status")
            if task_status is None or task_id is None:
                return

            if task_status == "FINISHED":
                return

            task_title = task.get("title", "Tarefa Desconhecida")

            if task_status == "READY_FOR_CLAIM":
                if task_id in self.processed_tasks:
                    return

                self.log.info(f"<g>🎯 Reivindicando tarefa: {task_title}</g>")
                result = self.claim_task(task_id)
                if result:
                    self.log.info(f"<g>✅ Tarefa reivindicada: {task_title}</g>")
                    self.processed_tasks.append(task_id)
                    self.recheck_claim = True
                else:
                    self.log.warning(f"<y>⚠️ Falha ao reivindicar tarefa: {task_title}</y>")

            elif task_status == "NOT_STARTED":
                if task_id in self.processed_tasks:
                    return

                self.log.info(f"<g>🚀 Iniciando tarefa: {task_title}</g>")
                result = self.start_task(task_id)
                if result:
                    self.log.info(f"<g>✅ Tarefa iniciada: {task_title}</g>")
                    self.processed_tasks.append(task_id)
                    self.recheck_claim = True
                else:
                    self.log.warning(f"<y>⚠️ Falha ao iniciar tarefa: {task_title}</y>")

        except Exception as e:
            self.log.error(f"<r>⛔ {e} falhou ao processar tarefa!</r>")

    async def handle_sub_section(self, sub_section):
        try:
            if "tasks" in sub_section:
                for task in sub_section["tasks"]:
                    await self.handle_task(task)
        except Exception as e:
            self.log.error(f"<r>⛔ {e} falhou ao processar subseção!</r>")

    def get_tasks(self):
        try:
            response = self.http.get(
                url="/api/v1/tasks",
                domain="earn",
            )

            if response is None:
                self.log.error(f"<r>⭕ {self.account_name} falhou ao obter tarefas!</r>")
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter tarefas!</r>")
            return None

    def start_task(self, task_id):
        try:
            response = self.http.post(
                url=f"/api/v1/tasks/{task_id}/start",
                domain="earn",
            )

            if response is None:
                return False

            return True

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao iniciar tarefa!</r>")
            return False

    def claim_task(self, task_id):
        try:
            response = self.http.post(
                url=f"/api/v1/tasks/{task_id}/claim",
                domain="earn",
            )

            if response is None:
                return False

            return True

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao reivindicar tarefa!</r>")
            return False

    def validate_task(self, task_id, keyword=None):
        try:
            data = {}
            if keyword:
                data["keyword"] = keyword

            response = self.http.post(
                url=f"/api/v1/tasks/{task_id}/validate",
                domain="earn",
                data=json.dumps(data) if data else None,
            )

            if response is None:
                return False

            return True

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao validar tarefa!</r>")
            return False