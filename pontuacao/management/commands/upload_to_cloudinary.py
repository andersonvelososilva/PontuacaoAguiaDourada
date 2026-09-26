import os
from django.core.management.base import BaseCommand
from django.conf import settings
from pontuacao.models import Desbravador

class Command(BaseCommand):
    help = "Uploads all local media photos of desbravadores directly to Cloudinary"

    def handle(self, *args, **options):
        cloud_name = getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME')
        if not cloud_name:
            self.stdout.write(self.style.ERROR("CLOUDINARY_CLOUD_NAME nao esta configurado no settings."))
            return

        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )

        media_dir = os.path.join(settings.BASE_DIR, 'media', 'desbravadores')
        if not os.path.exists(media_dir):
            self.stdout.write(self.style.WARNING(f"Diretorio {media_dir} nao encontrado."))
            return

        files = [f for f in os.listdir(media_dir) if os.path.isfile(os.path.join(media_dir, f))]
        self.stdout.write(self.style.SUCCESS(f"Encontrados {len(files)} arquivos de fotos locais em media/desbravadores/."))

        for filename in files:
            file_path = os.path.join(media_dir, filename)
            try:
                result = cloudinary.uploader.upload(
                    file_path,
                    folder="desbravadores",
                    use_filename=True,
                    unique_filename=False,
                    overwrite=True
                )
                self.stdout.write(self.style.SUCCESS(f"Enviado {filename} -> {result.get('secure_url')}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao enviar {filename}: {e}"))
