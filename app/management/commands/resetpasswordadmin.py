import string
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app.models import Account

class Command(BaseCommand):
    help = 'Reset mat khau cho tai khoan Admin'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username Admin can reset')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- RESET MAT KHAU ADMIN ---'))
        username = options.get('username')
        if not username:
            username = input('Nhap username Admin can reset: ').strip()
        else:
            username = username.strip()
        
        if not username:
            self.stdout.write(self.style.ERROR('Username khong duoc de trong.'))
            return

        try:
            admin = Account.objects.get(username=username, role='ADMIN')
            
            alphabet = string.ascii_letters + string.digits
            while True:
                password = ''.join(secrets.choice(alphabet) for i in range(8))
                if (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
                    break
                    
            admin.password = make_password(password)
            admin.save()
            
            self.stdout.write(self.style.SUCCESS(f"Da reset mat khau thanh cong cho '{username}'."))
            self.stdout.write(self.style.WARNING(f"Mat khau moi cua ban la: {password}"))
            self.stdout.write(self.style.WARNING("Luu y: Vui long copy va luu lai mat khau nay!"))
            
        except Account.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Khong tim thay Admin voi username '{username}'."))
