"""Unit tests for the DX54C protocol helpers.

Load api.py directly so these protocol tests do not require the full
Home Assistant runtime just to import the integration package.
"""
import importlib.util
import os
from pathlib import Path

_API_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "zyxel_dx54c"
    / "api.py"
)
_SPEC = importlib.util.spec_from_file_location("zyxel_dx54c_api", _API_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_API = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_API)

_pack = _API._pack
_stations = _API._stations
_unpack = _API._unpack


def test_parse_two_point_four_ghz_station():
    raw = "MACAddress Rate RSSI SNR Level 70:C9:32:F8:DC:0F 72222 -46 41 5"
    assert _stations(raw, "2.4 GHz") == [{
        "mac": "70:C9:32:F8:DC:0F",
        "band": "2.4 GHz",
        "rate_mbps": 72.222,
        "rssi": -46,
        "snr": 41,
        "level": 5,
    }]


def test_parse_multiple_records_from_list():
    raw = [
        "MACAddress Rate RSSI SNR Level",
        "70:C9:32:F8:DC:0F 72222 -46 41 5",
        "D4:D4:DA:4D:49:C4 65000 -49 38 4",
    ]
    assert len(_stations(raw, "2.4 GHz")) == 2


def test_empty_table():
    assert _stations(None, "5 GHz") == []


def test_aes_envelope_round_trip():
    key = os.urandom(32)
    payload = {"result": "ZCFG_SUCCESS", "sessionkey": "test-session"}
    assert _unpack(_pack(payload, key), key) == payload


def test_parse_five_ghz_station():
    raw = "MACAddress Rate RSSI SNR Level 24:5E:BE:12:34:56 866000 -51 39 4"
    assert _stations(raw, "5 GHz") == [{
        "mac": "24:5E:BE:12:34:56",
        "band": "5 GHz",
        "rate_mbps": 866.0,
        "rssi": -51,
        "snr": 39,
        "level": 4,
    }]


def test_ignore_malformed_station_rows():
    raw = (
        "MACAddress Rate RSSI SNR Level "
        "not-a-mac 1000 -50 30 3 "
        "24:5E:BE:12:34:56 invalid -51 39 4"
    )
    assert _stations(raw, "2.4 GHz") == []
