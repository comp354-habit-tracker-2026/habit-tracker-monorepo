from core.business import BaseService

from data_integration.models import DataConsent


class DataIntegrationService(BaseService):
    def __init__(self):
        super().__init__()
        self.provider_names = {provider: label for provider, label in DataConsent.PROVIDER_CHOICES}

    def get_user_integrations(self, user, params):
        provider = params.get("provider")
        status = params.get("status")

        consents = {consent.provider: consent for consent in DataConsent.objects.filter(user=user)}

        integrations = [
            {
                "id": f"{provider_key}-{user.id}",
                "name": self.provider_names.get(provider_key, provider_key.title()),
                "provider": provider_key,
                "external_id": f"{provider_key}-{user.id}",
                "status": "active" if consents.get(provider_key, None) and consents[provider_key].consent_granted else "revoked",
                "consent_granted": bool(consents.get(provider_key, None) and consents[provider_key].consent_granted),
                "metadata": {"source": "third_party_api"},
                "last_synced_at": "2026-03-23T00:00:00Z" if consents.get(provider_key, None) and consents[provider_key].consent_granted else None,
            }
            for provider_key, _ in DataConsent.PROVIDER_CHOICES
        ]

        if provider:
            integrations = [item for item in integrations if item["provider"] == provider]
        if status:
            integrations = [item for item in integrations if item["status"] == status]

        for integration in integrations:
            integration["is_synced"] = self.is_synced(integration["last_synced_at"])

        return integrations

    def set_user_consent(self, user, provider, consent_granted):
        provider_keys = [choice[0] for choice in DataConsent.PROVIDER_CHOICES]
        if provider not in provider_keys:
            raise ValueError(f"Invalid provider: {provider}")

        consent, _ = DataConsent.objects.get_or_create(user=user, provider=provider)
        consent.consent_granted = consent_granted
        consent.save(update_fields=["consent_granted", "updated_at"])
        return consent

    @staticmethod
    def is_synced(last_synced_at):
        return bool(last_synced_at)
