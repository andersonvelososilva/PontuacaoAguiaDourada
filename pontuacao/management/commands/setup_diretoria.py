from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Cria/atualiza as contas da Diretoria (Fernanda Mazur, Jancira Dantas e Admin)"

    def handle(self, *args, **options):
        # 1. Admin
        admin_user, _ = User.objects.get_or_create(username='admin')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('vcmleblon')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS("Senha do admin atualizada com sucesso para 'vcmleblon'."))

        # 2. Fernanda Mazur
        f_user, _ = User.objects.get_or_create(username='fernandamazur')
        f_user.first_name = 'Fernanda'
        f_user.last_name = 'Mazur'
        f_user.is_staff = True
        f_user.is_superuser = True
        f_user.set_password('mazur07')
        f_user.save()
        self.stdout.write(self.style.SUCCESS("Conta 'Fernanda Mazur' (usuario: fernandamazur) criada/atualizada com sucesso."))

        # 3. Jancira Dantas
        j_user, _ = User.objects.get_or_create(username='janciradantas')
        j_user.first_name = 'Jancira'
        j_user.last_name = 'Dantas'
        j_user.is_staff = True
        j_user.is_superuser = True
        j_user.set_password('Cira0603')
        j_user.save()
        self.stdout.write(self.style.SUCCESS("Conta 'Jancira Dantas' (usuario: janciradantas) criada/atualizada com sucesso."))
