from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Unidade(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Unidade")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Unidade"
        verbose_name_plural = "Unidades"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Desbravador(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='desbravador',
        verbose_name="Conta de Usuário",
        help_text="Conta associada para que o desbravador possa fazer login e ver seu próprio perfil."
    )
    nome = models.CharField(max_length=150, verbose_name="Nome Completo")
    unidade = models.ForeignKey(
        Unidade, 
        on_delete=models.PROTECT, 
        related_name='desbravadores',
        verbose_name="Unidade"
    )
    foto = models.ImageField(
        upload_to='desbravadores/',
        null=True,
        blank=True,
        verbose_name="Foto do Desbravador",
        help_text="Opcional. Foto de perfil do desbravador."
    )
    ativo = models.BooleanField(
        default=True, 
        verbose_name="Ativo",
        help_text="Desbravadores inativos não aparecem no ranking ou Top 3 públicos."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Desbravador"
        verbose_name_plural = "Desbravadores"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.unidade.nome})"

    @property
    def total_pontos(self):
        """Calcula o total acumulado derivado do histórico de registros."""
        total = self.pontuacoes.aggregate(total=models.Sum('pontos'))['total']
        return total if total is not None else 0


class Pontuacao(models.Model):
    desbravador = models.ForeignKey(
        Desbravador, 
        on_delete=models.CASCADE, 
        related_name='pontuacoes',
        verbose_name="Desbravador"
    )
    pontos = models.IntegerField(
        verbose_name="Pontos",
        help_text="Utilize valores positivos (ex: 10) ou negativos (ex: -5)."
    )
    motivo = models.CharField(max_length=255, verbose_name="Motivo")
    data_hora = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora")
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Registrado por"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Pontuação"
        verbose_name_plural = "Pontuações"
        ordering = ['-data_hora', '-created_at']

    def __str__(self):
        sinal = "+" if self.pontos > 0 else ""
        return f"{sinal}{self.pontos} pts — {self.desbravador.nome} ({self.motivo})"


class ConfiguracaoSistema(models.Model):
    MODO_TOP3_CHOICES = [
        ('NOME_FOTO_PONTOS', 'Nome + Foto + Pontos'),
        ('NOME_FOTO_SEMPONTOS', 'Nome + Foto sem Pontos'),
        ('OCULTO_PONTOS', 'Apenas Pontos com Identidade Oculta (🔒)'),
        ('NOME_PONTOS_SEMFOTO', 'Nome + Pontos sem Foto'),
    ]

    ranking_publico = models.BooleanField(
        default=False,
        verbose_name="Exibir Ranking Publicamente",
        help_text="Se desativado, o ranking geral não exibirá nomes ou posições públicas."
    )
    top3_publico = models.BooleanField(
        default=True,
        verbose_name="Exibir Top 3 Publicamente",
        help_text="Se desativado, a seção do Top 3 será oculta na página pública."
    )
    modo_top3 = models.CharField(
        max_length=30,
        choices=MODO_TOP3_CHOICES,
        default='NOME_FOTO_PONTOS',
        verbose_name="Modo de Exibição do Top 3",
        help_text="Define quais elementos (nome, foto, pontos) aparecem no Top 3 público."
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")

    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"

    def __str__(self):
        return "Configurações Globais de Exibição Pública"

    @classmethod
    def get_solo(cls):
        """Retorna ou cria a instância única de configuração do sistema."""
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
