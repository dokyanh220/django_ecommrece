from django.core.management.base import BaseCommand
from app.models import Account

class Command(BaseCommand):
    help = 'Xoa tai khoan Admin bang username'

    def add_arguments(self, parser):
        parser.add_argument('username', nargs='?', type=str, help='Username Admin can xoa')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- XOA TAI KHOAN ADMIN ---'))
        username = options.get('username')
        if not username:
            username = input('Nhap username Admin can xoa: ').strip()
        else:
            username = username.strip()
        
        if not username:
            self.stdout.write(self.style.ERROR('Username khong duoc de trong.'))
            return

        try:
            admin = Account.objects.get(username=username, role='ADMIN')
            confirm = input(f"Ban co chac chan muon xoa Admin '{username}' (Email: {admin.email})? [y/N]: ").strip().lower()
            if confirm == 'y':
                admin.delete()
                self.stdout.write(self.style.SUCCESS(f"Da xoa thanh cong Admin '{username}'."))
            else:
                self.stdout.write('Huy thao tac.')
        except Account.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Khong tim thay Admin voi username '{username}'."))
