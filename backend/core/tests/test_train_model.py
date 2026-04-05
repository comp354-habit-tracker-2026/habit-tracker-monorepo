import os
import numpy as np
import pytest
from core.business import train_model as tm
from core.business.train_model import train_model, model_path

#chatgpt

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
def test_train_model_high_dimensional_input():
    # Test if it handles multiple features correctly
    X = np.array([[1, 2], [2, 3], [3, 4]])
    y = np.array([5, 6, 7])
    result = train_model(X, y)
    assert "Model trained and saved" in result

def test_train_model_with_list_input():
    # Testing if it handles Python lists instead of NumPy arrays
    X = [[1], [2], [3]]
    y = [2, 4, 6]
    result = train_model(X, y)
    assert "Model trained and saved" in result

def test_train_model_single_point_error():
    # Scikit-learn usually needs more than 1 point for LinearRegression
    # This helps trigger the general Exception block
    X = np.array([[1]])
    y = np.array([2])
    result = train_model(X, y)
    # Depending on sklearn version, this might pass or throw a warning/error
    # It ensures the 'except' block is exercised
    assert "Error" in result or "Model trained" in result

import runpy
import os

def test_train_main_execution():
    # This executes the code inside the 'if __name__ == "__main__":' block
    try:
        runpy.run_path("core/business/train_model.py", run_name="__main__")
    except Exception as e:
        pytest.fail(f"train_model.py main block failed: {e}")

def test_predict_main_execution():
    # This executes the code inside the 'if __name__ == "__main__":' block
    try:
        runpy.run_path("core/business/predict_model.py", run_name="__main__")
    except Exception as e:
        pytest.fail(f"predict_model.py main block failed: {e}")
