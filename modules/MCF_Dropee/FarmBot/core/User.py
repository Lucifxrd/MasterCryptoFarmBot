# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

class User:
    def __init__(self, log, httpRequest, account_name):
        self.log = log
        self.http = httpRequest
        self.account_name = account_name

    def get_me(self):
        try:
            response = self.http.get(
                url="/api/v1/user/me",
                domain="user",
            )

            if response is None:
                self.log.error(
                    f"<r>⭕ {self.account_name} falhou ao obter informações do usuário!</r>"
                )
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter informações do usuário!</r>")
            return None

    def get_balance(self):
        try:
            response = self.http.get(
                url="/api/v1/friends/balance",
                domain="user",
            )

            if response is None:
                self.log.error(f"<r>⭕ {self.account_name} falhou ao obter saldo!</r>")
                return None

            return response

        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao obter saldo!</r>")
            return None

    def claim_friend_invite(self):
        try:
            response = self.http.post(
                url="/api/v1/friends/claim",
                domain="user",
            )

            if response is None:
                self.log.error(
                    f"<r>⭕ {self.account_name} falhou ao reivindicar convite de amigo!</r>"
                )
                return None

            return response
        except Exception as e:
            self.log.error(f"<r>⭕ {e} falhou ao reivindicar convite de amigo!</r>")
            return None