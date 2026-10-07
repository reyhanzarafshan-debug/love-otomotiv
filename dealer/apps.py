from django.apps import AppConfig


class DealerConfig(AppConfig):
    name = "dealer"
    verbose_name = "Bayi / Ledger"

    def ready(self):
        from . import signals  # noqa: F401
