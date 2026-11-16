"""Unit tests for the DX54C protocol helpers."""
import os

from custom_components.zyxel_dx54c.api import _pack, _stations, _unpack


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
