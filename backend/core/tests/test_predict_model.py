import os
import numpy as np
import pytest

from core.business.train_model import train_model
from core.business.predict_model import predict, model_path

# --------------------
# Fixture to ensure a trained model exists
# --------------------
@pytest.fixture(autouse=True)
def ensure_model_exists():
    if not os.path.exists(model_path):
        X = np.array([[1], [2], [3]])
        y = np.array([2, 4, 6])
        train_model(X, y)

def test_predict_success():
    result = predict(np.array([4]), horizon=3)
    assert result["status"] == "success"
    assert len(result["predictions"]) == 3

def test_predict_horizon_one():
    result = predict(np.array([4]), horizon=1)
    assert result["status"] == "success"
    assert len(result["predictions"]) == 1

def test_predict_multi_step_input():
    result = predict(np.array([4]), horizon=3)
    assert result["status"] == "success"
    assert len(result["predictions"]) == 3

def test_predict_no_model():
    if os.path.exists(model_path):
        os.remove(model_path)
    result = predict(np.array([4]), horizon=3)
    assert "Model not found" in result
    

def test_predict_invalid_horizon():
    result = predict(np.array([4]), horizon=0)
    assert "Horizon must be positive" in result

def test_predict_missing_input():
    result = predict(None, horizon=3)
    assert "Missing input data" in result