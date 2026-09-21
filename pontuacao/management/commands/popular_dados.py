from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pontuacao.models import Unidade, Desbravador, Pontuacao, ConfiguracaoSistema

class Command(BaseCommand):
    help = 'Limpa os dados antigos e cadastra as unidades e desbravadores reais do clube Águia Dourada.'

    def handle(self, *args, **options):
        self.stdout.write("Garantindo conta da Diretoria (admin)...")
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@clube.com",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created or not admin_user.check_password("admin123"):
            admin_user.set_password("admin123")
            admin_user.save()

        self.stdout.write("Limpando contas de usuários simulados (exceto diretoria)...")
        User.objects.filter(is_staff=False, is_superuser=False).delete()

        self.stdout.write("Limpando registros antigos de pontuações, desbravadores e unidades...")
        Pontuacao.objects.all().delete()
        Desbravador.objects.all().delete()
        Unidade.objects.all().delete()

        self.stdout.write("Garantindo configurações iniciais do sistema...")
        config = ConfiguracaoSistema.get_solo()
        config.ranking_modo = 'PARCIAL'
        config.ranking_limite_publico = 3
        config.mostrar_nomes_ranking = True
        config.mostrar_pontos_ranking = True
        config.mostrar_fotos_ranking = False
        config.save()

        self.stdout.write("Criando as novas Unidades reais...")
        u_arara = Unidade.objects.create(nome="Arara Azul", ativo=True)
        u_harpia = Unidade.objects.create(nome="Harpia", ativo=True)

        novos_desbravadores = [
            ("Ana Sofia", u_arara, "anasofia"),
            ("Davi Luis", u_harpia, "daviluis"),
            ("Mariano", u_harpia, "mariano"),
            ("Luis Paulo", u_harpia, "luispaulo"),
            ("João Inácio", u_harpia, "joaoinacio"),
            ("Aylla Suellen", u_arara, "ayllasuellen"),
            ("Arthur", u_harpia, "arthur"),
            ("Deuzilane", u_arara, "deuzilane"),
            ("Isis", u_arara, "isis"),
            ("Renan", u_harpia, "renan"),
            ("João Lucas", u_harpia, "joaolucas"),
        ]

        self.stdout.write("Cadastrando os novos Desbravadores reais e suas contas de usuário...")
        for nome, unidade, username in novos_desbravadores:
            # Criar conta de usuário associada
            user = User.objects.create_user(
                username=username,
                password="senha123"
            )
            # Criar perfil do Desbravador
            Desbravador.objects.create(
                nome=nome,
                unidade=unidade,
                user=user,
                ativo=True
            )

        self.stdout.write(self.style.SUCCESS(
            "Limpeza e cadastro concluídos com sucesso!\n"
            "Unidades criadas: Arara Azul, Harpia\n"
            "Desbravadores cadastrados: 11 membros reais.\n"
            "Senha padrão para os desbravadores: senha123 (Ex de login: anasofia / senha123)"
        ))
