from .exceptions import DomainValidationError
from .services import BaseService

__all__ = ["BaseService", "DomainValidationError"]


#information inputted to run the code and get an output
from .train_model import train_model
from .predict_model import predict
import numpy as np

X = np.array([[1], [2], [3], [4]])
y = np.array([2, 4, 6,7])

print(train_model(X, y))
print(predict(np.array([4]), horizon=3))

