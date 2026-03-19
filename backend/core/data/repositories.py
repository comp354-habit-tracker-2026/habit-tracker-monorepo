class BaseRepository:
    """Base class for repository implementations."""

    def __init__(self, model):
        self.model = model
