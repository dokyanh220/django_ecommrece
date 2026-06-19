import string
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from app.models import Account

class Command(BaseCommand):
    help = 'Tao tai khoan Admin qua terminal UI voi mat khau sinh ngau nhien'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- TAO TAI KHOAN QUAN TRI (ADMIN) ---'))
        
        while True:
            fullname = input("Nhap ho va ten: ").strip()
            if fullname:
                break
            self.stdout.write(self.style.ERROR('Ho va ten khong duoc de trong.'))

        while True:
            username = input("Nhap ten dang nhap: ").strip()
            if not username:
                self.stdout.write(self.style.ERROR('Ten dang nhap khong duoc de trong.'))
                continue
            if Account.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR('Ten dang nhap da ton tai.'))
                continue
            break

        while True:
            email = input("Nhap email: ").strip()
            if not email:
                self.stdout.write(self.style.ERROR('Email khong duoc de trong.'))
                continue
            if Account.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR('Email da ton tai.'))
                continue
            break

        # Generate random password (length 8, containing at least one letter and one number)
        alphabet = string.ascii_letters + string.digits
        while True:
            password = ''.join(secrets.choice(alphabet) for i in range(8))
            if (any(c.isalpha() for c in password) and any(c.isdigit() for c in password)):
                break

        # Save account
        Account.objects.create(
            fullname=fullname,
            username=username,
            email=email,
            password=make_password(password),
            role='ADMIN',
            status=True
        )

        self.stdout.write(self.style.SUCCESS(f'\n[+] Da tao thanh cong tai khoan Admin: {username}'))
        self.stdout.write(self.style.WARNING(f'[!] Mat khau tu dong cua ban la: {password}'))
        self.stdout.write(self.style.WARNING('Luu y: Vui long copy va luu lai mat khau nay can than!'))
