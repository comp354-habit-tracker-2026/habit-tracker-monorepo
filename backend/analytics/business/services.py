from core.business import BaseService
from analytics.data import AnalyticsRepository
<<<<<<< HEAD
=======
from core.business.predict_model import predict


import numpy as np
>>>>>>> c1b80755e34f9331fa233c528bd7615129b5d34b


class AnalyticsService(BaseService):
    def __init__(self, repository=None):
        self.repository = repository or AnalyticsRepository()

    def activity_statistics(self, user):
        return self.repository.activity_statistics(user)

    def trend_snapshot(self, user):
        return self.repository.trend_snapshot(user)

    def forecast_preview(self, user):
<<<<<<< HEAD
        return self.repository.forecast_preview(user)
=======
        #this info is to be changed when the dataset is connected, just hardcoded to be able to output
        X_last=np.array([1,2,3])
        return predict(X_last, horizon=3)
        #return self.repository.forecast_preview(user)

>>>>>>> c1b80755e34f9331fa233c528bd7615129b5d34b
