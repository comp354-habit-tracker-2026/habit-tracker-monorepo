from unittest.mock import MagicMock
from rest_framework.exceptions import NotFound
import pytest
from activities.business.services import ActivityService
from rest_framework.exceptions import PermissionDenied


# unit test
def test_delete_activity_not_found():
    # ARRANGE
    mock_repo = MagicMock()
    mock_repo.get_by_id.return_value = None  # simulate not found

    service = ActivityService(repository=mock_repo)
    mock_user = MagicMock()

    # ACT & ASSERT
    with pytest.raises(NotFound):
        service.delete_activity(activity_id=999, user=mock_user)




def test_delete_activity_wrong_user():
    # ARRANGE
    mock_repo = MagicMock()
    mock_activity = MagicMock()
    mock_activity.user = MagicMock()          # activity belongs to user A
    mock_repo.get_by_id.return_value = mock_activity

    service = ActivityService(repository=mock_repo)
    different_user = MagicMock()              # user B is making the request

    # ACT & ASSERT
    with pytest.raises(PermissionDenied):
        service.delete_activity(activity_id=1, user=different_user)


def test_delete_activity_success():
    # ARRANGE
    mock_repo = MagicMock()
    mock_activity = MagicMock()
    mock_user = MagicMock()
    mock_activity.user = mock_user            # same user, ownership passes
    mock_repo.get_by_id.return_value = mock_activity

    service = ActivityService(repository=mock_repo)

    # ACT
    service.delete_activity(activity_id=1, user=mock_user)

    # ASSERT
    mock_repo.delete.assert_called_once_with(mock_activity)  