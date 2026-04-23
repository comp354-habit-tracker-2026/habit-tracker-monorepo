def test_repository_imports():
    from group_11.repositories.user_repository import UserRepository
    from group_11.repositories.activity_repository import ActivityRepository
    from group_11.repositories.goal_repository import GoalRepository

    assert UserRepository is not None
