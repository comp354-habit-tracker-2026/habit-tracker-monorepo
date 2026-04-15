from django.contrib.auth import get_user_model
from django.test import TestCase
from datetime import date
from users.data.repositories import UserRepository, VALID_PROVIDERS
from activities.models import Activity, ConnectedAccount

User = get_user_model()


class RepositoryTests(TestCase):

    def create_user(self, username):
        return User.objects.create_user(
            username=username,
            email=f"{username}@test.com",
            password="pass"
        )

    def create_activity(self, user, provider):
        account = ConnectedAccount.objects.create(
            user=user,
            provider=provider
        )
        return Activity.objects.create(
            account=account,
            duration=30,
            distance=5.0,
            date=date.today()
        )

    def test_delete_provider_data_invalid_provider(self):
        repo = UserRepository()
        user = self.create_user('test')

        with self.assertRaises(ValueError):
            repo.delete_provider_data(user, provider='invalid_provider')

    def test_delete_provider_data_returns_correct_format(self):
        repo = UserRepository()
        user = self.create_user('test2')

        provider = next(iter(VALID_PROVIDERS))
        result = repo.delete_provider_data(user, provider)

        self.assertIn('deleted_count', result)
        self.assertEqual(result['provider'], provider)
        self.assertIsInstance(result['deleted_count'], int)

    def test_delete_provider_data_filters_by_provider(self):
        repo = UserRepository()
        user = self.create_user('test3')

        providers = list(VALID_PROVIDERS)
        if len(providers) < 2:
            self.skipTest("Need at least two providers")

        provider1, provider2 = providers[:2]

        self.create_activity(user, provider1)
        self.create_activity(user, provider2)

        repo.delete_provider_data(user, provider1)

        self.assertEqual(
            Activity.objects.filter(account__provider=provider1).count(), 0
        )
        self.assertEqual(
            Activity.objects.filter(account__provider=provider2).count(), 1
        )

    def test_delete_provider_data_no_activities(self):
        repo = UserRepository()
        user = self.create_user('test4')

        provider = next(iter(VALID_PROVIDERS))

        result = repo.delete_provider_data(user, provider)

        self.assertEqual(result['deleted_count'], 0)