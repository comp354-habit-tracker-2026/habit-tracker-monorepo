class Activity:

    def __init__(self, distance, duration, date, provider=None, external_id=None, activity_type=None):

        self.distance = float(distance)
        self.duration = duration
        self.date = date
        self.provider = provider
        self.external_id = external_id
        self.activity_type = activity_type