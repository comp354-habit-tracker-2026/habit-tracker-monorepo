class Database:
    async def connect(self) -> None:
        print("Mock DB connected")

    async def disconnect(self) -> None:
        print("Mock DB disconnected")


db = Database()
