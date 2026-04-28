# tests/test_extractor.py
from amazon_ledger_converter.path_validation import *
from pathlib import Path
import pandas as pd
import tempfile

##############################
# Test the validator factory #
##############################

def test_path_exists_returns_validator_function():
    """path_exists return a callable function"""
    validator = path_exists()
    assert callable(validator)

    
def test_validator_returns_none_when_path_exists():
    def fake_exists(path):
        return True
    validator = path_exists(fake_exists)
    result = validator("some-file.txt")
    assert result is None

    
def test_validator_returns_error_when_path_does_not_exist():
    def fake_exists(path):
        return False
    validator = path_exists(fake_exists)
    result = validator("missing-file.txt")
    assert result == "No file at: missing-file.txt"
    
def test_validator_passes_path_to_exists_function():
    called_with = []
    def fake_exists(path):
        called_with.append(path)
        return True
    validator = path_exists(fake_exists)
    validator("abc.txt")
    assert called_with == ["abc.txt"]

    

