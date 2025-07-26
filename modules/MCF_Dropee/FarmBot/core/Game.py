# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import random
from utilities.utilities import getConfig
import time
from .Wallet import Wallet
from mcf_utils.api import API

class Game:
    def __init__(self, log, httpRequest, account_name, license_key=None):
        self.log = log
        self.http = httpRequest
        self.account_name = account_name
        self.license_key = license_key

    def get_now(self):
        try:
            response = self.http.get(
                url="/api/v1/time/now",
                domain="game",
            )

            if response is None:
                self.log.error(
                    f"<r>⭕ {self.account_name} falhou ao obter horário do jogo!</r>")
                return None

            return response.get("now")

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter horário do jogo!</r>")
            return None

    def get_balance(self):
        try:
            response = self.http.get(
                url="/api/v1/user/balance",
                domain="game",
            )

            if response is None:
                self.log.error(
                    f"<r>⭕ {self.account_name} falhou ao obter saldo!</r>")
                return None

            if (
                response.get("playPasses") is None
                or response.get("availableBalance") is None
            ):
                self.log.error(
                    f"<r>⭕ {self.account_name} falhou ao obter saldo!</r>")
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter saldo!</r>")
            return None

    def get_daily_reward(self):
        try:
            response = self.http.get(
                url="/api/v2/daily-reward",
                domain="game",
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter recompensa diária!</r>")
            return None

    def claim_daily_reward(self):
        try:
            response = self.http.post(
                url="/api/v2/daily-reward",
                domain="game",
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao reivindicar recompensa diária!</r>")
            return None

    def get_farming_info(self):
        try:
            response = self.http.get(
                url="/api/v1/farming/claim",
                domain="game",
            )

            if response is None:
                return None

            return response

        except Exception as e:
            return None

    def start_farming(self):
        try:
            response = self.http.post(
                url="/api/v1/farming/start",
                domain="game",
            )

            if response is None:
                return None

            return response

        except Exception as e:
            return None

    def claim_farming(self):
        try:
            response = self.http.post(
                url="/api/v1/farming/claim",
                domain="game",
            )

            if response is None:
                return None

            return response

        except Exception as e:
            return None