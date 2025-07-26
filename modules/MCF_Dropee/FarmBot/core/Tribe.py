# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import random

class Tribe:
    def __init__(self, log, httpRequest, account_name):
        self.log = log
        self.http = httpRequest
        self.account_name = account_name

    def get_my(self):
        try:
            response = self.http.get(
                url="/api/v1/tribe/my",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter informações da tribo!</r>")
            return None

    def get_leaderboard(self):
        try:
            response = self.http.get(
                url="/api/v1/tribe/leaderboard",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter ranking da tribo!</r>")
            return None

    def get_bot(self):
        try:
            response = self.http.get(
                url="/api/v1/tribe/bot",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter bot da tribo!</r>")
            return None

    def get_tribe(self):
        try:
            response = self.http.get(
                url="/api/v1/tribe",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter tribo!</r>")
            return None

    def get_by_chat_name(self, chat_name):
        if chat_name is None or chat_name == "":
            return None

        try:
            response = self.http.get(
                url=f"/api/v1/tribe/by-chatname/{chat_name}",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response
        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter tribo por nome do chat!</r>")
            return None

    def join_tribe(self, chat_name):
        if chat_name is None or chat_name == "":
            return None

        try:
            response = self.http.post(
                url=f"/api/v1/tribe/{chat_name}/join",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response
        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao entrar na tribo!</r>")
            return None

    def leave_tribe(self):
        try:
            response = self.http.delete(
                url="/api/v1/tribe/leave",
                domain="tribe",
                display_errors=False,
            )

            if response is None:
                return None

            return response
        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao sair da tribo!</r>")
            return None