from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Unidade, Desbravador, Pontuacao, ConfiguracaoSistema

class PontuacaoEvolucaoTest(TestCase):
    def setUp(self):
        # 1. Criar Unidades
        self.unidade_a = Unidade.objects.create(nome="Águias", ativo=True)
        self.unidade_b = Unidade.objects.create(nome="Falcões", ativo=True)

        # 2. Criar Usuário Diretoria e Usuários Desbravadores
        self.admin_user = User.objects.create_superuser(
            username="admin_diretoria",
            email="admin@clube.com",
            password="adminpassword123"
        )

        self.user_joao = User.objects.create_user(
            username="joao",
            password="senha123"
        )
        self.user_beatriz = User.objects.create_user(
            username="beatriz",
            password="senha123"
        )

        # 3. Criar Desbravadores
        self.desbravador_joao = Desbravador.objects.create(
            nome="João Silva",
            unidade=self.unidade_a,
            user=self.user_joao,
            ativo=True
        )
        self.desbravador_beatriz = Desbravador.objects.create(
            nome="Beatriz Santos",
            unidade=self.unidade_b,
            user=self.user_beatriz,
            ativo=True
        )
        self.desbravador_inativo = Desbravador.objects.create(
            nome="Carlos Souza",
            unidade=self.unidade_a,
            ativo=False
        )

        # 4. Criar Lançamentos de Pontos
        Pontuacao.objects.create(
            desbravador=self.desbravador_joao,
            pontos=50,
            motivo="Acampamento",
            criado_por=self.admin_user
        )
        Pontuacao.objects.create(
            desbravador=self.desbravador_beatriz,
            pontos=100,
            motivo="Campeã de Ordem Unida",
            criado_por=self.admin_user
        )
        Pontuacao.objects.create(
            desbravador=self.desbravador_inativo,
            pontos=200,
            motivo="Pontos Inativo",
            criado_por=self.admin_user
        )

        # 5. Garantir Configuração do Sistema
        self.config = ConfiguracaoSistema.get_solo()
        self.config.ranking_publico = True
        self.config.top3_publico = True
        self.config.modo_top3 = 'NOME_FOTO_PONTOS'
        self.config.save()

    # --- TESTES DE AUTENTICAÇÃO E PERMISSÕES (SEGURANÇA BACKEND) ---

    def test_desbravador_login_e_acesso_ao_proprio_perfil(self):
        client = Client()
        login_success = client.login(username="joao", password="senha123")
        self.assertTrue(login_success)

        response = client.get(reverse('pontuacao:perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "João Silva")
        self.assertContains(response, "50 pts")
        self.assertContains(response, "Acampamento")

    def test_desbravador_bloqueado_ao_tentar_acessar_perfil_alheio(self):
        client = Client()
        client.login(username="joao", password="senha123")

        # Tentar passar ID do perfil da Beatriz na Query String
        response = client.get(f"{reverse('pontuacao:perfil')}?id={self.desbravador_beatriz.id}")
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Segurança", status_code=403)

    def test_desbravador_bloqueado_ao_tentar_acessar_django_admin(self):
        client = Client()
        client.login(username="joao", password="senha123")

        response = client.get('/admin/')
        # Deve redirecionar para login do admin (302) pois não é is_staff
        self.assertEqual(response.status_code, 302)

    def test_diretoria_acessa_admin_com_sucesso(self):
        client = Client()
        client.login(username="admin_diretoria", password="adminpassword123")

        response = client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    # --- TESTES DO RANKING GERAL ---

    def test_ranking_ativo_exibe_dados(self):
        self.config.ranking_publico = True
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ranking Geral")
        self.assertContains(response, "Beatriz Santos")
        self.assertContains(response, "João Silva")
        # Inativo não deve aparecer
        self.assertNotContains(response, "Carlos Souza")

    def test_ranking_inativo_nao_exibe_dados_e_mostra_mensagem(self):
        self.config.ranking_publico = False
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O ranking não está disponível no momento")
        self.assertContains(response, "ENTRAR")
        self.assertIsNone(response.context['ranking_list'])

    # --- TESTES DO TOP 3 E SEUS 4 MODOS ---

    def test_top3_inativo_nao_exibe_dados_e_mostra_mensagem(self):
        self.config.top3_publico = False
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O Top 3 não está disponível no momento")
        self.assertIsNone(response.context['top3_list'])

    def test_top3_modo_nome_foto_pontos(self):
        self.config.top3_publico = True
        self.config.modo_top3 = 'NOME_FOTO_PONTOS'
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beatriz Santos")
        self.assertContains(response, "+100")

    def test_top3_modo_oculto_pontos(self):
        self.config.top3_publico = True
        self.config.ranking_publico = False
        self.config.modo_top3 = 'OCULTO_PONTOS'
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desbravador 1")
        self.assertContains(response, "Identidade Oculta")
        # Não deve expor o nome real quando o ranking também está oculto
        self.assertNotContains(response, "Beatriz Santos")
        self.assertContains(response, "+100")

    def test_top3_modo_nome_foto_sempontos(self):
        self.config.top3_publico = True
        self.config.modo_top3 = 'NOME_FOTO_SEMPONTOS'
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beatriz Santos")

    def test_top3_modo_nome_pontos_semfoto(self):
        self.config.top3_publico = True
        self.config.modo_top3 = 'NOME_PONTOS_SEMFOTO'
        self.config.save()

        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beatriz Santos")
        self.assertContains(response, "+100")

    def test_alteracao_de_pontuacao_atualiza_posicao_top3(self):
        # Inicialmente Beatriz = 100, João = 50. Beatriz é o 1º no Top 3.
        # Adicionar +100 pontos para João => João fica com 150.
        Pontuacao.objects.create(
            desbravador=self.desbravador_joao,
            pontos=100,
            motivo="Super Destaque",
            criado_por=self.admin_user
        )
        self.assertEqual(self.desbravador_joao.total_pontos, 150)

        response = self.client.get(reverse('pontuacao:index'))
        top3_list = response.context['top3_list']
        self.assertEqual(top3_list[0], self.desbravador_joao)
