from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str
    email: str


def get_user_by_id(user_id: str) -> User:
    raise NotImplementedError("get_user_by_id is not implemented")


def create_user(user: User) -> User:
    raise NotImplementedError("create_user is not implemented")