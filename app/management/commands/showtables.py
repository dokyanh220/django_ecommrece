from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Hien thi tat ca cac bang (models) trong he thong'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- DANH SACH BANG (MODELS) ---'))
        
        models = apps.get_models()
        app_models = [m for m in models if m._meta.app_label == 'app']
        
        header = f"{'Ten bang (Model)':<25} | {'So ban ghi':<10}"
        self.stdout.write(header)
        self.stdout.write('-' * len(header))
        
        for model in app_models:
            count = model.objects.count()
            row = f"{model.__name__:<25} | {count:<10}"
            self.stdout.write(row)
