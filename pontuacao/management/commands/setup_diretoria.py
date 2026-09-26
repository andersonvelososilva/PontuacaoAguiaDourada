from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Cria/atualiza as contas da Diretoria (Fernanda Mazur, Jancira Dantas e Admin) e senhas dos Desbravadores"

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

        # 4. Garantir que os dados dos desbravadores estao carregados se o banco estiver novo/vazio
        from pontuacao.models import Desbravador
        from django.core.management import call_command
        if Desbravador.objects.count() == 0:
            try:
                call_command('loaddata', 'initial_data.json')
                self.stdout.write(self.style.SUCCESS("Dados dos desbravadores restaurados automaticamente do initial_data.json."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao carregar initial_data.json: {e}"))

        # 5. Atualizar senhas dos desbravadores no padrão: animal + 3 dígitos únicos
        senhas_desbravadores = {
            'anasofia': 'aguia248',
            'arthur': 'leao715',
            'ayllasuellen': 'tigre382',
            'daviluis': 'urso904',
            'deuzilane': 'panda526',
            'isis': 'zebra163',
            'joaoinacio': 'puma841',
            'joaolucas': 'falcao679',
            'luispaulo': 'pantera457',
            'mariano': 'tubarao291',
            'renan': 'gaviao738',
        }

        count = 0
        for username, pwd in senhas_desbravadores.items():
            try:
                u = User.objects.get(username=username)
                u.set_password(pwd)
                u.save()
                count += 1
            except User.DoesNotExist:
                pass
        self.stdout.write(self.style.SUCCESS(f"{count} senhas de desbravadores atualizadas no banco de dados."))
