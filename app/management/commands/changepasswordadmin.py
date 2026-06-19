from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password, check_password
from app.models import Account

class Command(BaseCommand):
    help = 'Doi mat khau thu cong cho tai khoan Admin'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username Admin can doi mat khau')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- DOI MAT KHAU ADMIN ---'))
        username = options.get('username')
        if not username:
            username = input('Nhap username Admin: ').strip()
        else:
            username = username.strip()

        if not username:
            self.stdout.write(self.style.ERROR('Username khong duoc de trong.'))
            return

        try:
            admin = Account.objects.get(username=username, role='ADMIN')
            
            # Xac thuc mat khau cu
            while True:
                old_password = input('Nhap mat khau cu: ').strip()
                if not old_password:
                    self.stdout.write(self.style.ERROR('Mat khau cu khong duoc de trong.'))
                    continue
                if not check_password(old_password, admin.password):
                    self.stdout.write(self.style.ERROR('Mat khau cu khong chinh xac.'))
                    continue
                break

            while True:
                password = input('Nhap mat khau moi (toi thieu 6 ky tu): ').strip()
                if not password:
                    self.stdout.write(self.style.ERROR('Mat khau khong duoc de trong.'))
                    continue
                if len(password) < 6:
                    self.stdout.write(self.style.ERROR('Mat khau phai co toi thieu 6 ky tu.'))
                    continue
                
                confirm_password = input('Nhap lai mat khau moi de xac nhan: ').strip()
                if password != confirm_password:
                    self.stdout.write(self.style.ERROR('Mat khau xac nhan khong khop.'))
                    continue
                break
                
            admin.password = make_password(password)
            admin.save()
            
            self.stdout.write(self.style.SUCCESS(f"Da doi mat khau thanh cong cho Admin '{username}'."))
            
        except Account.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Khong tim thay Admin voi username '{username}'."))
