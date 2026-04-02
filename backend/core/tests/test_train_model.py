import os
import numpy as np
import pytest

from core.business.train_model import train_model, model_path

# --------------------
# TRAIN MODEL TESTS
# --------------------

def test_train_model_success():
    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    result = train_model(X, y)
    assert "Model trained and saved" in result
    assert os.path.exists(model_path)

def test_train_model_missing_input():
    result = train_model(None, None)
    assert "Missing dataset input" in result

def test_train_model_empty_input():
    X = np.array([])
    y = np.array([])
    result = train_model(X, y)
    assert "Dataset is empty" in result

def test_train_model_mismatch_length():
    X = np.array([[1], [2]])
    y = np.array([1])
    result = train_model(X, y)
    assert "Error" in result

def test_train_model_invalid_type():
    X = "invalid"
    y = "invalid"
    result = train_model(X, y)
    assert "Error" in result