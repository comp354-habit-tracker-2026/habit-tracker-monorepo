import joblib
import numpy as np
import os
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
#with the help of ChatGPT
def predict(X_last=None, horizon=3):

    try:
        if horizon <= 0:
            raise ValueError("Horizon must be positive")

        if not os.path.exists(model_path):
            raise FileNotFoundError("Model not found. Train model first")

        if X_last is None:
            raise ValueError("Missing input data for prediction")

        model = joblib.load(model_path) #load trained model

        pred = []
        cur_input = np.array(X_last, dtype=float)

        for _ in range(horizon):
            next_val = model.predict(cur_input.reshape(1, -1))[0]
            pred.append(float(next_val))

            cur_input = np.roll(cur_input, -1)
            cur_input[-1] = next_val

        print("Predictions:", pred) 

        return {
            "status": "success",
            "horizon": horizon,
            "predictions": pred
        }

    except Exception as e:
        return f"Error {str(e)}" 



if __name__ == "__main__":
    test_input = np.array([4]) #to be modifed, depending on trained dataset
    result = predict(test_input, horizon=3)
    print(result)