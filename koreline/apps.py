from django.apps import AppConfig


class KorelineConfig(AppConfig):
    name = 'koreline'

    def ready(self):
        import koreline.signals

