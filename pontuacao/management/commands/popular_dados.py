from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pontuacao.models import Unidade, Desbravador, Pontuacao

class Command(BaseCommand):
    help = 'Popula o banco de dados com unidades, desbravadores e pontuações iniciais para testes.'

    def handle(self, *args, **options):
        self.stdout.write("Criando superusuário de teste se não existir...")
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@clube.com",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Superusuário criado: admin / admin123"))

        self.stdout.write("Criando unidades...")
        u1, _ = Unidade.objects.get_or_create(nome="Águias Reais")
        u2, _ = Unidade.objects.get_or_create(nome="Falcões do Vale")
        u3, _ = Unidade.objects.get_or_create(nome="Leões da Tribo")

        self.stdout.write("Criando desbravadores...")
        d1, _ = Desbravador.objects.get_or_create(nome="Gabriel Oliveira", unidade=u1)
        d2, _ = Desbravador.objects.get_or_create(nome="Beatriz Santos", unidade=u1)
        d3, _ = Desbravador.objects.get_or_create(nome="Lucas Mendes", unidade=u2)
        d4, _ = Desbravador.objects.get_or_create(nome="Mariana Lima", unidade=u2)
        d5, _ = Desbravador.objects.get_or_create(nome="Matheus Ferreira", unidade=u3)

        self.stdout.write("Criando pontuações...")
        # Lançamentos para Gabriel
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=15, motivo="Especialidade de Arte de Acampar", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d1, pontos=-3, motivo="Atraso na formação", criado_por=admin_user)

        # Lançamentos para Beatriz
        Pontuacao.objects.get_or_create(desbravador=d2, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d2, pontos=20, motivo="Pontualidade e Uniforme Completo", criado_por=admin_user)

        # Lançamentos para Lucas
        Pontuacao.objects.get_or_create(desbravador=d3, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d3, pontos=5, motivo="Participação na Feira de Saúde", criado_por=admin_user)

        # Lançamentos para Mariana
        Pontuacao.objects.get_or_create(desbravador=d4, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)
        Pontuacao.objects.get_or_create(desbravador=d4, pontos=25, motivo="Campeã da Ordem Unida", criado_por=admin_user)

        # Lançamentos para Matheus
        Pontuacao.objects.get_or_create(desbravador=d5, pontos=10, motivo="Presença na reunião de Domingo", criado_por=admin_user)

        self.stdout.write(self.style.SUCCESS("Banco de dados populado com sucesso!"))
