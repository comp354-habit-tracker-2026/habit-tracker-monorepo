import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import os
#with help from chatgpt
model_path = os.path.join(os.path.dirname(__file__), "model.pkl") #path to where to save the trained model

def train_model(X=None, y=None):
    try:
        if (X is None or y is None):
            raise ValueError("Missing dataset input")
        if(len(X)==0 or len(y)==0):
            raise ValueError("Dataset is empty")

        model = LinearRegression()
        model.fit(X,y)

        joblib.dump(model, model_path) #saving the model to the model path
        
        return f"Model trained and saved, saved to: {model_path}"
    
    except Exception as e:
        return f"Error {str(e)}" 

if __name__ == "__main__":
    X = np.array([[10], [30], [40], [20]]) #these 2 lines to be changed depending on inputed dataset
    y = np.array([10, 7, 5, 8])

    result = train_model(X, y)
    print(result)