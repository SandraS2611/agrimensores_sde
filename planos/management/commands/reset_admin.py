from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        admin = User.objects.get(username="admin")  # Cambiá por tu username
        admin.set_password("TuPasswordSegura123")
        admin.save()
        self.stdout.write(self.style.SUCCESS("Contraseña del admin reseteada"))
