from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pontuacao.models import Unidade, Desbravador

class Command(BaseCommand):
    help = "Cria/atualiza as contas da Diretoria, senhas dos Desbravadores, Unidade Aspirantes e Desbravadores de Teste"

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

        # 4. Garantir que a unidade 'Aspirantes' existe no banco
        unidade_asp, created_asp = Unidade.objects.get_or_create(nome='Aspirantes', defaults={'ativo': True})
        if created_asp:
            self.stdout.write(self.style.SUCCESS("Unidade 'Aspirantes' criada com sucesso."))

        # 5. Garantir que os dados dos desbravadores estao carregados se o banco estiver novo/vazio
        from django.core.management import call_command
        if Desbravador.objects.count() == 0:
            try:
                call_command('loaddata', 'initial_data.json')
                self.stdout.write(self.style.SUCCESS("Dados dos desbravadores restaurados automaticamente do initial_data.json."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao carregar initial_data.json: {e}"))

        # 6. Atualizar senhas dos desbravadores no padrão: animal + 3 dígitos únicos
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

        # 7. Criar 3 Desbravadores de Teste para Treinamento da Diretoria (sem conta de usuário)
        testes = ["Desbravador Teste 1", "Desbravador Teste 2", "Desbravador Teste 3"]
        for nome_t in testes:
            d_t, t_created = Desbravador.objects.get_or_create(
                nome=nome_t,
                defaults={
                    'unidade': unidade_asp,
                    'user': None,
                    'ativo': True
                }
            )
            if t_created:
                self.stdout.write(self.style.SUCCESS(f"Desbravador de teste '{nome_t}' criado com sucesso."))
