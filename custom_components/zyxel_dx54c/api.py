"""Async local API client for the Zyxel DX54C."""
from __future__ import annotations

import base64
import json
import os
from typing import Any

import aiohttp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


class ZyxelError(Exception):
    """Router communication or protocol error."""


def _b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _pack(data: dict[str, Any], key: bytes) -> dict[str, str]:
    iv = os.urandom(32)
    padder = PKCS7(128).padder()
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
    padded = padder.update(raw) + padder.finalize()
    ctx = Cipher(algorithms.AES(key), modes.CBC(iv[:16])).encryptor()
    return {"iv": _b64(iv), "content": _b64(ctx.update(padded) + ctx.finalize())}


def _unpack(data: dict[str, Any], key: bytes) -> Any:
    try:
        iv = base64.b64decode(data["iv"], validate=True)
        encrypted = base64.b64decode(data["content"], validate=True)
        ctx = Cipher(algorithms.AES(key), modes.CBC(iv[:16])).decryptor()
        padded = ctx.update(encrypted) + ctx.finalize()
        unpad = PKCS7(128).unpadder()
        return json.loads(unpad.update(padded) + unpad.finalize())
    except (KeyError, ValueError, TypeError) as err:
        raise ZyxelError("Risposta cifrata del router non valida.") from err


def _stations(raw: Any, band: str) -> list[dict[str, Any]]:
    if raw is None:
        return []
    fields = str(raw).strip().strip('"').split()
    result = []
    for pos in range(5, len(fields) - 4, 5):
        mac, rate, rssi, snr, level = fields[pos:pos + 5]
        if len(mac) != 17 or mac.count(":") != 5:
            continue
        try:
            result.append({"mac": mac.upper(), "band": band, "rate_mbps": float(rate) / 1000,
                           "rssi": int(rssi), "snr": int(snr), "level": int(level)})
        except ValueError:
            continue
    return result


class ZyxelDX54CAPI:
    """Session client; only reads the wireless station table."""
    def __init__(self, host: str, username: str, password: str) -> None:
        self.host = host.rstrip("/")
        self.username = username
        self._password = password
        self._key = os.urandom(32)
        self._session_key: str | None = None
        self._http: aiohttp.ClientSession | None = None
        self._timeout = aiohttp.ClientTimeout(total=15)

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if self._http is None or self._http.closed:
            self._http = aiohttp.ClientSession(timeout=self._timeout)
        try:
            async with self._http.request(method, self.host + path, **kwargs) as response:
                response.raise_for_status()
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise ZyxelError(f"Comunicazione router non riuscita: {method} {path}.") from err

    async def async_login(self) -> None:
        key_data = await self._request("GET", "/getRSAPublickKey")
        pem = key_data.get("RSAPublicKey") if isinstance(key_data, dict) else None
        if not pem:
            raise ZyxelError("Chiave RSA del router non disponibile.")
        try:
            pub = serialization.load_pem_public_key(pem.encode("ascii"))
            wrapped = pub.encrypt(base64.b64encode(self._key), padding.PKCS1v15())
        except (ValueError, TypeError) as err:
            raise ZyxelError("Chiave RSA del router non riconosciuta.") from err
        data = {"Input_Account": self.username, "Input_Passwd": _b64(self._password.encode()),
                "RememberPassword": 0, "SHA512_password": False}
        payload = _pack(data, self._key)
        payload["key"] = _b64(wrapped)
        body = await self._request("POST", "/UserLogin", json=payload,
                                   headers={"Content-Type": "application/json"})
        if isinstance(body, dict) and "iv" in body and "content" in body:
            body = _unpack(body, self._key)
        if not isinstance(body, dict) or body.get("result") not in ("ZCFG_SUCCESS", "SUCCESS", True, 0):
            raise ZyxelError("Login rifiutato dal router: controlla le credenziali.")
        self._session_key = body.get("sessionkey") or body.get("sessionKey")
        if not self._session_key:
            raise ZyxelError("Token di sessione assente dopo il login.")

    async def async_get_stations(self) -> list[dict[str, Any]]:
        if not self._session_key:
            await self.async_login()
        body = await self._request("GET", "/cgi-bin/WLANTable_handle")
        if isinstance(body, dict) and "iv" in body and "content" in body:
            body = _unpack(body, self._key)
        if isinstance(body, list) and body and isinstance(body[0], dict):
            body = body[0]
        if not isinstance(body, dict):
            raise ZyxelError("Tabella WLAN con formato non riconosciuto.")
        return _stations(body.get("result"), "2.4 GHz") + _stations(body.get("result5"), "5 GHz")

    async def async_close(self) -> None:
        if self._http and not self._http.closed:
            await self._http.close()
        self._password = ""
        self._session_key = None
