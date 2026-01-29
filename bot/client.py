import hashlib
import hmac
import time
from typing import Any
import requests

from .exceptions import ApiError, NetworkError


class BinanceFuturesClient:
    """
    Minimal REST client for Binance USDT-M Futures Testnet.

    Base URL required by task:
      https://testnet.binancefuture.com
    """

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout_s: int = 10,
        logger=None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.logger = logger

        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, query_string: str) -> str:
        return hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _ts_ms(self) -> int:
        return int(time.time() * 1000)

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        """
        Make an HTTP request. If signed=True, adds timestamp + signature.
        """
        params = dict(params or {})
        url = f"{self.base_url}{path}"

        if signed:
            params.setdefault("timestamp", self._ts_ms())
            params.setdefault("recvWindow", 5000)

        # Prepare signature (Binance signs query string, not JSON body for this endpoint)
        if signed:
            # requests will encode params in URL form order; we must sign the querystring ourselves consistently
            query_string = "&".join([f"{k}={params[k]}" for k in sorted(params.keys())])
            signature = self._sign(query_string)
            params["signature"] = signature

        # Logging (redact signature)
        if self.logger:
            safe_params = dict(params)
            if "signature" in safe_params:
                safe_params["signature"] = "***redacted***"
            self.logger.info("HTTP %s %s params=%s signed=%s", method.upper(), path, safe_params, signed)

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,  # Binance futures order endpoint expects query params
                timeout=self.timeout_s,
            )
        except requests.RequestException as e:
            if self.logger:
                self.logger.exception("Network failure: %s", str(e))
            raise NetworkError(f"Network failure: {e}") from e

        text = resp.text
        if self.logger:
            self.logger.info("HTTP %s -> %s body=%s", path, resp.status_code, text)

        # Try parse JSON (Binance usually returns JSON)
        try:
            data = resp.json()
        except ValueError:
            data = {"raw": text}

        # Handle non-2xx
        if not (200 <= resp.status_code < 300):
            msg = None
            if isinstance(data, dict):
                msg = data.get("msg") or data.get("message")
            raise ApiError(
                message=f"Binance API error ({resp.status_code}): {msg or text}",
                status_code=resp.status_code,
                payload=data if isinstance(data, dict) else {"raw": text},
            )

        # Binance can still return {code, msg} in 200 sometimes; guard it
        if isinstance(data, dict) and "code" in data and data.get("code") not in (0, None):
            raise ApiError(
                message=f"Binance API error: {data.get('msg')}",
                status_code=resp.status_code,
                payload=data,
            )

        if not isinstance(data, dict):
            return {"data": data}
        return data
