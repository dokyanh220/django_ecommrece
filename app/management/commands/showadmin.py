from django.core.management.base import BaseCommand
from app.models import Account

class Command(BaseCommand):
    help = 'Hien thi danh sach tai khoan Admin'

    def handle(self, *args, **options):
        admins = Account.objects.filter(role='ADMIN')
        self.stdout.write(self.style.SUCCESS(f'--- DANH SACH ADMIN ({admins.count()}) ---'))
        
        # In header
        header = f"{'ID':<5} | {'Username':<20} | {'Email':<30} | {'Status':<10}"
        self.stdout.write(header)
        self.stdout.write('-' * len(header))
        
        for admin in admins:
            status = 'Active' if admin.status else 'Locked'
            row = f"{admin.id:<5} | {admin.username:<20} | {admin.email:<30} | {status:<10}"
            if admin.status:
                self.stdout.write(row)
            else:
                self.stdout.write(self.style.ERROR(row))
