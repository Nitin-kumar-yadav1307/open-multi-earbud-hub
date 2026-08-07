import pytest
from src.audio.native_bridge import (
    BridgeError,
    BridgeInvalidArgumentsError,
    BridgeBackendError,
    BridgeInternalError,
    ERROR_CODE_MAP,
)


def test_error_code_map_contains_expected_codes():
    assert 1 in ERROR_CODE_MAP
    assert 2 in ERROR_CODE_MAP
    assert 3 in ERROR_CODE_MAP


def test_error_code_map_maps_to_correct_types():
    assert ERROR_CODE_MAP[1] is BridgeInvalidArgumentsError
    assert ERROR_CODE_MAP[2] is BridgeBackendError
    assert ERROR_CODE_MAP[3] is BridgeInternalError


def test_bridge_error_hierarchy():
    assert issubclass(BridgeInvalidArgumentsError, BridgeError)
    assert issubclass(BridgeBackendError, BridgeError)
    assert issubclass(BridgeInternalError, BridgeError)
    assert issubclass(BridgeError, Exception)


def test_unknown_error_code_falls_back_to_internal():
    exc_class = ERROR_CODE_MAP.get(999, BridgeInternalError)
    assert exc_class is BridgeInternalError