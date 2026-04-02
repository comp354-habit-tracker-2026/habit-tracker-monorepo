import os
import importlib.util
import numpy as np

#using chatGPT
CURRENT_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
)

spec = importlib.util.spec_from_file_location("train_model", FILE_PATH)
train_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_module)

train_model = train_module.train_model
model_path = train_module.model_path


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
    result = train_model([], [])
    assert "Dataset is empty" in result


def test_train_model_mismatch():
    X = [[1], [2]]
    y = [1]

    result = train_model(X, y)
    assert "Error" in result

def test_train_model_mismatch_length():
    from importlib.util import spec_from_file_location, module_from_spec

    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2]])
    y = np.array([1])  # mismatch
    result = train_model(X, y)
    assert "Error" in result

def test_train_model_mismatch_length():
    from importlib.util import spec_from_file_location, module_from_spec

    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2]])
    y = np.array([1])  # mismatch length
    result = train_model(X, y)
    assert "Error" in result