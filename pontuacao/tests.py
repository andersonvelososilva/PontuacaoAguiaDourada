from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Unidade, Desbravador, Pontuacao, ConfiguracaoSistema

class PontuacaoCompletaTest(TestCase):
    def setUp(self):
        # 1. Unidades
        self.unidade_a = Unidade.objects.create(nome="Águias", ativo=True)
        self.unidade_b = Unidade.objects.create(nome="Falcões", ativo=True)

        # 2. Usuários
        self.diretoria_user = User.objects.create_superuser(
            username="diretor",
            email="diretor@clube.com",
            password="diretorpassword123"
        )
        self.user_joao = User.objects.create_user(
            username="joao",
            password="senha123"
        )
        self.user_beatriz = User.objects.create_user(
            username="beatriz",
            password="senha123"
        )
        self.user_inativo = User.objects.create_user(
            username="carlos",
            password="senha123",
            is_active=False
        )

        # 3. Desbravadores
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
        self.desbravador_carlos = Desbravador.objects.create(
            nome="Carlos Souza",
            unidade=self.unidade_a,
            user=self.user_inativo,
            ativo=False
        )

        # 4. Lançamentos Iniciais
        Pontuacao.objects.create(desbravador=self.desbravador_joao, pontos=50, motivo="Presença", criado_por=self.diretoria_user)
        Pontuacao.objects.create(desbravador=self.desbravador_beatriz, pontos=100, motivo="Campeã Ordem Unida", criado_por=self.diretoria_user)

        # 5. Configuração Inicial
        self.config = ConfiguracaoSistema.get_solo()
        self.config.ranking_modo = 'COMPLETO'
        self.config.mostrar_nomes_ranking = True
        self.config.mostrar_pontos_ranking = True
        self.config.save()

    # --- 1. TESTES DA TELA INICIAL LIMPA (HOME /) ---

    def test_pagina_inicial_exibe_titulo_e_opcoes_ver_ranking_e_entrar(self):
        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sistema de Pontos")
        self.assertContains(response, "Ver Ranking")
        self.assertContains(response, "Entrar")

    # --- 2. TESTES DE LOGIN E REDIRECIONAMENTO ---

    def test_login_diretoria_redireciona_para_painel_diretoria(self):
        client = Client()
        response = client.post(reverse('pontuacao:login'), {'username': 'diretor', 'password': 'diretorpassword123'})
        self.assertRedirects(response, '/diretoria/')

    def test_login_desbravador_redireciona_para_perfil(self):
        client = Client()
        response = client.post(reverse('pontuacao:login'), {'username': 'joao', 'password': 'senha123'})
        self.assertRedirects(response, '/perfil/')

    def test_login_credenciais_invalidas(self):
        client = Client()
        response = client.post(reverse('pontuacao:login'), {'username': 'joao', 'password': 'senhaincorreta'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuário ou senha incorretos")

    # --- 3. TESTES DE AUTORIZAÇÃO E SEGURANÇA ---

    def test_desbravador_bloqueado_ao_acessar_painel_diretoria(self):
        client = Client()
        client.login(username='joao', password='senha123')
        response = client.get(reverse('pontuacao:diretoria_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_desbravador_bloqueado_ao_acessar_perfil_de_outro_membro(self):
        client = Client()
        client.login(username='joao', password='senha123')
        response = client.get(f"{reverse('pontuacao:perfil')}?id={self.desbravador_beatriz.id}")
        self.assertEqual(response.status_code, 403)

    def test_diretoria_acessa_painel_com_sucesso(self):
        client = Client()
        client.login(username='diretor', password='diretorpassword123')
        response = client.get(reverse('pontuacao:diretoria_dashboard'))
        self.assertEqual(response.status_code, 200)

    # --- 4. TESTES DE LANÇAMENTO E REMOÇÃO DE PONTOS ---

    def test_lancar_pontos_positivos(self):
        client = Client()
        client.login(username='diretor', password='diretorpassword123')

        response = client.post(reverse('pontuacao:diretoria_pontuacao'), {
            'desbravador': self.desbravador_joao.id,
            'tipo': 'ADICIONAR',
            'quantidade': 20,
            'motivo': 'Especialidade de Acampamento'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.desbravador_joao.total_pontos, 70)

    def test_lancar_remocao_de_pontos_punicao(self):
        client = Client()
        client.login(username='diretor', password='diretorpassword123')

        response = client.post(reverse('pontuacao:diretoria_pontuacao'), {
            'desbravador': self.desbravador_joao.id,
            'tipo': 'REMOVER',
            'quantidade': 15,
            'motivo': 'Atraso na Formação'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.desbravador_joao.total_pontos, 35)

    # --- 5. TESTES DE CLASSIFICAÇÃO INDIVIDUAL NO PERFIL ---

    def test_desbravador_ve_propria_posicao_no_perfil_mesmo_ranking_oculto(self):
        self.config.ranking_modo = 'OCULTO'
        self.config.save()

        client = Client()
        client.login(username='joao', password='senha123')
        response = client.get(reverse('pontuacao:perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['posicao_ranking'], 2)

    # --- 6. TESTES DA ROTA DEDICADA DE RANKING PÚBLICO (/ranking/) E ATUALIZAÇÃO DINÂMICA ---

    def test_ranking_modo_completo_no_endpoint_ranking(self):
        self.config.ranking_modo = 'COMPLETO'
        self.config.save()

        response = self.client.get(reverse('pontuacao:public_ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beatriz Santos")
        self.assertContains(response, "João Silva")

    def test_ranking_modo_parcial_no_endpoint_ranking(self):
        self.config.ranking_modo = 'PARCIAL'
        self.config.ranking_limite_publico = 1
        self.config.save()

        response = self.client.get(reverse('pontuacao:public_ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ranking_list']), 1)
        self.assertContains(response, "Beatriz Santos")
        self.assertNotContains(response, "João Silva")

    def test_ranking_modo_oculto_no_endpoint_ranking(self):
        self.config.ranking_modo = 'OCULTO'
        self.config.save()

        response = self.client.get(reverse('pontuacao:public_ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['ranking_list'])
        self.assertContains(response, "Ranking Indisponível no Momento")

    def test_atualizacao_dinamica_apos_modificacao_na_diretoria(self):
        client = Client()
        client.login(username='diretor', password='diretorpassword123')

        # Diretoria altera o ranking para OCULTO via formulário de configurações
        response_post = client.post(reverse('pontuacao:diretoria_configuracoes'), {
            'ranking_modo': 'OCULTO',
            'ranking_limite_publico': 3,
            'mostrar_nomes_ranking': True,
            'mostrar_pontos_ranking': True,
            'mostrar_fotos_ranking': False,
        })
        self.assertEqual(response_post.status_code, 302)

        # Consulta pública a /ranking/ deve refletir imediatamente a alteração para OCULTO
        response_public = self.client.get(reverse('pontuacao:public_ranking'))
        self.assertEqual(response_public.status_code, 200)
        self.assertIsNone(response_public.context['ranking_list'])
        self.assertContains(response_public, "Ranking Indisponível no Momento")
