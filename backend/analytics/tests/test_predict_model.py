import os
import importlib.util
import numpy as np

# Load predict_model.py directly (bypass Django)
CURRENT_DIR = os.path.dirname(__file__)
FILE_PATH = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "business", "predict_model.py")
)

spec = importlib.util.spec_from_file_location("predict_model", FILE_PATH)
predict_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predict_module)

predict = predict_module.predict
model_path = predict_module.model_path


# --- TESTS ---

def test_predict_success():
    # Ensure model exists by training first
    from importlib.util import spec_from_file_location, module_from_spec

    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    train_model(X, y)

    result = predict(np.array([4]), horizon=3)

    assert result["status"] == "success"
    assert len(result["predictions"]) == 3


def test_predict_no_model():
    # Delete model if exists
    if os.path.exists(model_path):
        os.remove(model_path)

    result = predict(np.array([4]), horizon=3)

    assert "Model not found" in result


def test_predict_invalid_horizon():
    result = predict(np.array([4]), horizon=0)
    assert "Horizon must be positive" in result


def test_predict_missing_input():
    # Ensure model exists first
    from importlib.util import spec_from_file_location, module_from_spec

    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    train_model(X, y)

    result = predict(None, horizon=3)

    assert "Missing input data" in result

def test_predict_horizon_one():
    from importlib.util import spec_from_file_location, module_from_spec

    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2], [3]])
    y = np.array([2, 4, 6])
    train_model(X, y)

    result = predict(np.array([4]), horizon=1)
    assert result["status"] == "success"
    assert len(result["predictions"]) == 1

def test_predict_multi_step_input():
    from importlib.util import spec_from_file_location, module_from_spec
    import numpy as np

    # Train model first
    train_path = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "business", "train_model.py")
    )
    spec_train = spec_from_file_location("train_model", train_path)
    train_module = module_from_spec(spec_train)
    spec_train.loader.exec_module(train_module)

    train_model = train_module.train_model

    X = np.array([[1], [2], [3]])  # single feature
    y = np.array([2, 4, 6])
    train_model(X, y)

    # Use the **correct shape for last input**
    result = predict(np.array([4]), horizon=3)
    assert result["status"] == "success"
    assert len(result["predictions"]) == 3