from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Unidade, Desbravador, Pontuacao

class PontuacaoModelTest(TestCase):
    def setUp(self):
        self.unidade = Unidade.objects.create(nome="Águias-Reais", ativo=True)
        self.desbravador = Desbravador.objects.create(
            nome="João Silva",
            unidade=self.unidade,
            ativo=True
        )
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@clube.com",
            password="adminpassword123"
        )

    def test_criacao_unidade_e_desbravador(self):
        self.assertEqual(self.unidade.nome, "Águias-Reais")
        self.assertEqual(self.desbravador.nome, "João Silva")
        self.assertEqual(self.desbravador.unidade, self.unidade)
        self.assertTrue(self.desbravador.ativo)

    def test_calculo_pontuacao_positiva_e_negativa(self):
        # Desbravador recém criado deve ter 0 pontos
        self.assertEqual(self.desbravador.total_pontos, 0)

        # Adiciona +10 por presença
        Pontuacao.objects.create(
            desbravador=self.desbravador,
            pontos=10,
            motivo="Presença na reunião",
            criado_por=self.admin_user
        )
        self.assertEqual(self.desbravador.total_pontos, 10)

        # Adiciona +5 por especialidade
        Pontuacao.objects.create(
            desbravador=self.desbravador,
            pontos=5,
            motivo="Especialidade concluída",
            criado_por=self.admin_user
        )
        self.assertEqual(self.desbravador.total_pontos, 15)

        # Subtrai -3 por atraso
        Pontuacao.objects.create(
            desbravador=self.desbravador,
            pontos=-3,
            motivo="Atraso",
            criado_por=self.admin_user
        )
        self.assertEqual(self.desbravador.total_pontos, 12)

    def test_desbravador_inativo(self):
        desbravador_inativo = Desbravador.objects.create(
            nome="Carlos Souza",
            unidade=self.unidade,
            ativo=False
        )
        Pontuacao.objects.create(
            desbravador=desbravador_inativo,
            pontos=20,
            motivo="Acampamento",
            criado_por=self.admin_user
        )
        # O histórico permanece no banco
        self.assertEqual(desbravador_inativo.total_pontos, 20)

        # Não deve aparecer na listagem pública
        response = self.client.get(reverse('pontuacao:index'))
        self.assertContains(response, "João Silva")
        self.assertNotContains(response, "Carlos Souza")


class PontuacaoViewsTest(TestCase):
    def setUp(self):
        self.unidade_a = Unidade.objects.create(nome="Falcões", ativo=True)
        self.unidade_b = Unidade.objects.create(nome="Leões", ativo=True)
        
        self.d1 = Desbravador.objects.create(nome="Ana Maria", unidade=self.unidade_a, ativo=True)
        self.d2 = Desbravador.objects.create(nome="Bruno Costa", unidade=self.unidade_b, ativo=True)

    def test_acesso_pagina_inicial(self):
        response = self.client.get(reverse('pontuacao:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Maria")
        self.assertContains(response, "Bruno Costa")

    def test_pesquisa_por_nome(self):
        response = self.client.get(reverse('pontuacao:index') + '?q=Ana')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Maria")
        self.assertNotContains(response, "Bruno Costa")

    def test_pesquisa_por_unidade(self):
        response = self.client.get(reverse('pontuacao:index') + f'?unidade={self.unidade_a.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Maria")
        self.assertNotContains(response, "Bruno Costa")

    def test_acesso_pagina_detalhe(self):
        response = self.client.get(reverse('pontuacao:detalhe', kwargs={'pk': self.d1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Maria")
        self.assertContains(response, "Falcões")

    def test_acesso_ranking(self):
        response = self.client.get(reverse('pontuacao:ranking'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ana Maria")
        self.assertContains(response, "Bruno Costa")

    def test_protecao_admin(self):
        # Acesso sem login deve redirecionar para o login do admin
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/admin/login/' in response.url)
