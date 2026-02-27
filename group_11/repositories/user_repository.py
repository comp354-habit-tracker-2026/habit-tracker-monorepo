from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: str


class UserRepository(Protocol):
    def create_user(self, user: User) -> User:
        ...

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        ...

    def get_user_by_email(self, email: str) -> Optional[User]:
        ...


class NotImplementedUserRepository:
    def create_user(self, user: User) -> User:
        raise NotImplementedError("create_user is not implemented")

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        raise NotImplementedError("get_user_by_id is not implemented")

    def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError("get_user_by_email is not implemented")
