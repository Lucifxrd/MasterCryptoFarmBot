# Developed by: MasterkinG32
# Date: 2024
# Github: https://github.com/masterking32
# Telegram: https://t.me/MasterCryptoFarmBot

import json
import time
import cloudscraper
import utilities.BL as BL

class HttpRequest:
    def __init__(
        self,
        log,
        proxy=None,
        user_agent=None,
        tgWebData=None,
        account_name=None,
    ):
        self.log = log
        self.proxy = proxy
        self.user_agent = user_agent
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
        self.tgWebData = tgWebData
        self.account_name = account_name
        self.token_refreshed = False

        if not self.user_agent or self.user_agent == "":
            self.user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.3"

        if "windows" in self.user_agent.lower():
            self.log.warning(
                "🟡 <y>User Agent do Windows detectado, para segurança use user-agent mobile</y>"
            )

        self.scraper = cloudscraper.create_scraper()

    def get(
        self,
        url,
        domain="game",
        headers=None,
        send_option_request=True,
        valid_response_code=200,
        valid_option_response_code=204,
        auth_header=True,
        return_headers=False,
        display_errors=True,
        retries=3,
    ):
        try:
            url = self._fix_url(url, domain)
            default_headers = self._get_default_headers() if "dropee.clicker-game-api.tropee.com" in url else {}

            if headers is None:
                headers = {}

            if auth_header and self.authToken:
                headers["authorization"] = f"Bearer {self.authToken}"

            if headers:
                for key, value in headers.items():
                    default_headers[key] = value

            if send_option_request:
                self.options(
                    url=url,
                    method="GET",
                    headers=headers,
                    valid_response_code=valid_option_response_code,
                    display_errors=display_errors,
                )

            response = self.scraper.get(
                url=url,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )
            if response.status_code == 401:
                if self.renew_access_token():
                    self.log.info(
                        "🟡 <y>Tentando novamente após renovar token de acesso...</y>"
                    )
                    BL.save_auth_token(
                        self.account_name, self.authToken, self.RefreshToken
                    )
                    return self.get(
                        url=url,
                        domain=domain,
                        headers=headers,
                        send_option_request=False,
                        valid_response_code=valid_response_code,
                        valid_option_response_code=valid_option_response_code,
                        auth_header=auth_header,
                        return_headers=return_headers,
                        display_errors=display_errors,
                        retries=retries - 1,
                    )

            if response.status_code != valid_response_code:
                if display_errors:
                    self.log.error(
                        f"<r>⭕ URL: {url} | Status: {response.status_code} | Response: {response.text}</r>"
                    )
                return None

            response_json = response.json()
            if return_headers:
                return response_json, response.headers
            return response_json

        except Exception as e:
            if display_errors:
                self.log.error(f"<r>⭕ {e}</r>")
            time.sleep(1)
            if retries > 0:
                return self.get(
                    url=url,
                    domain=domain,
                    headers=headers,
                    send_option_request=send_option_request,
                    valid_response_code=valid_response_code,
                    valid_option_response_code=valid_option_response_code,
                    auth_header=auth_header,
                    return_headers=return_headers,
                    display_errors=display_errors,
                    retries=retries - 1,
                )
            return None

    def post(
        self,
        url,
        data=None,
        domain="game",
        headers=None,
        send_option_request=True,
        valid_response_code=200,
        valid_option_response_code=204,
        auth_header=True,
        return_headers=False,
        display_errors=True,
        retries=3,
    ):
        try:
            url = self._fix_url(url, domain)
            default_headers = self._get_default_headers() if "dropee.clicker-game-api.tropee.com" in url else {}

            if headers is None:
                headers = {}

            if auth_header and self.authToken:
                headers["authorization"] = f"Bearer {self.authToken}"

            if headers:
                for key, value in headers.items():
                    default_headers[key] = value

            if send_option_request:
                self.options(
                    url=url,
                    method="POST",
                    headers=headers,
                    valid_response_code=valid_option_response_code,
                    display_errors=display_errors,
                )

            response = self.scraper.post(
                url=url,
                data=data,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )

            if response.status_code == 401:
                if self.renew_access_token():
                    self.log.info(
                        "🟡 <y>Tentando novamente após renovar token de acesso...</y>"
                    )
                    BL.save_auth_token(
                        self.account_name, self.authToken, self.RefreshToken
                    )
                    return self.post(
                        url=url,
                        data=data,
                        domain=domain,
                        headers=headers,
                        send_option_request=False,
                        valid_response_code=valid_response_code,
                        valid_option_response_code=valid_option_response_code,
                        auth_header=auth_header,
                        return_headers=return_headers,
                        display_errors=display_errors,
                        retries=retries - 1,
                    )

            if response.status_code != valid_response_code:
                if display_errors:
                    self.log.error(
                        f"<r>⭕ URL: {url} | Status: {response.status_code} | Response: {response.text}</r>"
                    )
                return None

            response_json = response.json()
            if return_headers:
                return response_json, response.headers
            return response_json

        except Exception as e:
            if display_errors:
                self.log.error(f"<r>⭕ {e}</r>")
            time.sleep(1)
            if retries > 0:
                return self.post(
                    url=url,
                    data=data,
                    domain=domain,
                    headers=headers,
                    send_option_request=send_option_request,
                    valid_response_code=valid_response_code,
                    valid_option_response_code=valid_option_response_code,
                    auth_header=auth_header,
                    return_headers=return_headers,
                    display_errors=display_errors,
                    retries=retries - 1,
                )
            return None

    def delete(
        self,
        url,
        domain="game",
        headers=None,
        send_option_request=True,
        valid_response_code=200,
        valid_option_response_code=204,
        auth_header=True,
        return_headers=False,
        display_errors=True,
        retries=3,
    ):
        try:
            url = self._fix_url(url, domain)
            default_headers = self._get_default_headers() if "dropee.clicker-game-api.tropee.com" in url else {}

            if headers is None:
                headers = {}

            if auth_header and self.authToken:
                headers["authorization"] = f"Bearer {self.authToken}"

            if headers:
                for key, value in headers.items():
                    default_headers[key] = value

            if send_option_request:
                self.options(
                    url=url,
                    method="DELETE",
                    headers=headers,
                    valid_response_code=valid_option_response_code,
                    display_errors=display_errors,
                )

            response = self.scraper.delete(
                url=url,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )

            if response.status_code == 401:
                if self.renew_access_token():
                    self.log.info(
                        "🟡 <y>Tentando novamente após renovar token de acesso...</y>"
                    )
                    BL.save_auth_token(
                        self.account_name, self.authToken, self.RefreshToken
                    )
                    return self.delete(
                        url=url,
                        domain=domain,
                        headers=headers,
                        send_option_request=False,
                        valid_response_code=valid_response_code,
                        valid_option_response_code=valid_option_response_code,
                        auth_header=auth_header,
                        return_headers=return_headers,
                        display_errors=display_errors,
                        retries=retries - 1,
                    )

            if response.status_code != valid_response_code:
                if display_errors:
                    self.log.error(
                        f"<r>⭕ URL: {url} | Status: {response.status_code} | Response: {response.text}</r>"
                    )
                return None

            response_json = response.json()
            if return_headers:
                return response_json, response.headers
            return response_json

        except Exception as e:
            if display_errors:
                self.log.error(f"<r>⭕ {e}</r>")
            time.sleep(1)
            if retries > 0:
                return self.delete(
                    url=url,
                    domain=domain,
                    headers=headers,
                    send_option_request=send_option_request,
                    valid_response_code=valid_response_code,
                    valid_option_response_code=valid_option_response_code,
                    auth_header=auth_header,
                    return_headers=return_headers,
                    display_errors=display_errors,
                    retries=retries - 1,
                )
            return None

    def _fix_url(self, url, domain):
        if url.startswith("http"):
            return url

        base_url = self.game_url.get(domain, self.game_url["game"])
        return f"{base_url}{url}"

    def _get_default_headers(self):
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://webapp.game.dropee.xyz",
            "priority": "u=1, i",
            "referer": "https://webapp.game.dropee.xyz/",
            "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": self.user_agent,
        }

    def _get_proxy(self):
        if self.proxy is None:
            return None

        return {"http": self.proxy, "https": self.proxy}

    def options(
        self,
        url,
        method="GET",
        headers=None,
        valid_response_code=204,
        display_errors=True,
    ):
        try:
            default_headers = self._get_default_headers() if "dropee.clicker-game-api.tropee.com" in url else {}
            default_headers["access-control-request-method"] = method

            if headers:
                for key, value in headers.items():
                    default_headers[f"access-control-request-headers"] = key

            response = self.scraper.options(
                url=url,
                headers=default_headers,
                proxies=self._get_proxy(),
                timeout=30,
            )

            if response.status_code != valid_response_code:
                if display_errors:
                    self.log.error(
                        f"<r>⭕ Options - URL: {url} | Status: {response.status_code}</r>"
                    )
                return False

            return True

        except Exception as e:
            if display_errors:
                self.log.error(f"<r>⭕ Options error: {e}</r>")
            return False

    def renew_access_token(self):
        if self.token_refreshed:
            BL.delete_auth_token(self.account_name)
            return False

        if not self.RefreshToken:
            BL.delete_auth_token(self.account_name)
            return False

        try:
            response = self.post(
                url="/api/v1/auth/refresh",
                domain="user",
                data=json.dumps({"refresh": self.RefreshToken}),
                auth_header=False,
                send_option_request=False,
                display_errors=False,
            )

            if response is None:
                BL.delete_auth_token(self.account_name)
                return False

            access_token = response.get("access")
            refresh_token = response.get("refresh")

            if not access_token:
                BL.delete_auth_token(self.account_name)
                return False

            self.authToken = access_token
            self.RefreshToken = refresh_token
            self.token_refreshed = True
            return True

        except Exception as e:
            BL.delete_auth_token(self.account_name)
            return False