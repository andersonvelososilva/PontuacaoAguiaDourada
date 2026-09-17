from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pontuacao.models import Unidade, Desbravador, Pontuacao, ConfiguracaoSistema

class Command(BaseCommand):
    help = 'Popula o banco de dados com unidades, desbravadores, usuários de teste e pontuações.'

    def handle(self, *args, **options):
        self.stdout.write("Criando ou buscando superusuário da Diretoria...")
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
            self.stdout.write(self.style.SUCCESS("Superusuário Diretoria: admin / admin123"))

        self.stdout.write("Garantindo configurações do sistema...")
        config = ConfiguracaoSistema.get_solo()
        config.ranking_publico = True
        config.top3_publico = True
        config.modo_top3 = 'NOME_FOTO_PONTOS'
        config.save()

        self.stdout.write("Criando unidades...")
        u1, _ = Unidade.objects.get_or_create(nome="Águias Reais")
        u2, _ = Unidade.objects.get_or_create(nome="Falcões do Vale")
        u3, _ = Unidade.objects.get_or_create(nome="Leões da Tribo")

        self.stdout.write("Criando contas de usuário para desbravadores...")
        user_joao, created = User.objects.get_or_create(
            username="joao",
            defaults={"email": "joao@clube.com"}
        )
        if created or not user_joao.check_password("senha123"):
            user_joao.set_password("senha123")
            user_joao.save()

        user_beatriz, created = User.objects.get_or_create(
            username="beatriz",
            defaults={"email": "beatriz@clube.com"}
        )
        if created or not user_beatriz.check_password("senha123"):
            user_beatriz.set_password("senha123")
            user_beatriz.save()

        self.stdout.write("Criando desbravadores...")
        d1, _ = Desbravador.objects.get_or_create(
            nome="João Silva",
            defaults={"unidade": u1, "user": user_joao}
        )
        if not d1.user:
            d1.user = user_joao
            d1.save()

        d2, _ = Desbravador.objects.get_or_create(
            nome="Beatriz Santos",
            defaults={"unidade": u1, "user": user_beatriz}
        )
        if not d2.user:
            d2.user = user_beatriz
            d2.save()

        d3, _ = Desbravador.objects.get_or_create(nome="Lucas Mendes", unidade=u2)
        d4, _ = Desbravador.objects.get_or_create(nome="Mariana Lima", unidade=u2)
        d5, _ = Desbravador.objects.get_or_create(nome="Matheus Ferreira", unidade=u3)

        self.stdout.write("Criando lançamentos de pontuação...")
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=15, motivo="Especialidade de Arte de Acampar", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=20, motivo="Acampamento de Fim de Semana", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=-3, motivo="Atraso na formação", criado_por=admin_user)

        Pontuacao.objects.get_or_create(desbravador=d2, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d2, pontos=20, motivo="Pontualidade e Uniforme Completo", criado_por=admin_user)

        Pontuacao.objects.get_or_create(desbravador=d4, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d4, pontos=25, motivo="Campeã da Ordem Unida", criado_por=admin_user)

        self.stdout.write(self.style.SUCCESS("Banco de dados populado com sucesso! Contas de teste: joao/senha123, beatriz/senha123, admin/admin123"))
