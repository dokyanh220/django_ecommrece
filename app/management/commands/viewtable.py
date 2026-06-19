from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Xem du lieu cua 1 bang (toi da 20 dong)'

    def add_arguments(self, parser):
        parser.add_argument('model_name', nargs='?', type=str, help='Ten bang can xem (VD: Account, Product...)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- XEM DU LIEU BANG ---'))
        model_name = options.get('model_name')
        if not model_name:
            model_name = input("Nhap ten bang can xem (VD: Account, Product...): ").strip()
        else:
            model_name = model_name.strip()
        
        if not model_name:
            self.stdout.write(self.style.ERROR('Ten bang khong duoc de trong.'))
            return

        models = apps.get_models()
        target_model = None
        for m in models:
            if m.__name__.lower() == model_name.lower():
                target_model = m
                break
                
        if not target_model:
            self.stdout.write(self.style.ERROR(f"Khong tim thay bang nao co ten '{model_name}'."))
            return
            
        objects = target_model.objects.all().order_by('-id')[:20]
        count = target_model.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f"\nBang: {target_model.__name__} (Tong so: {count} dong. Hien thi max 20 dong moi nhat)"))
        
        if not objects:
            self.stdout.write("Bang nay hien chua co du lieu.")
            return
            
        # Lay cac field names
        fields = target_model._meta.fields
        field_names = [f.name for f in fields]
        
        # Tao header
        header_str = " | ".join(f"{name[:15]:<15}" for name in field_names)
        self.stdout.write('-' * len(header_str))
        self.stdout.write(header_str)
        self.stdout.write('-' * len(header_str))
        
        # Tao row data
        for obj in objects:
            row_vals = []
            for field in fields:
                val = getattr(obj, field.name)
                val_str = str(val)[:12] + '...' if len(str(val)) > 15 else str(val)
                row_vals.append(f"{val_str:<15}")
            
            self.stdout.write(" | ".join(row_vals))
            
        self.stdout.write('-' * len(header_str))
