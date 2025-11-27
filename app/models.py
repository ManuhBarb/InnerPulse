from django.db import models
from django.contrib.auth.models import User

class Cidade(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da cidade")
    uf = models.CharField(max_length=2, verbose_name="UF")

    def __str__(self):
        return f"{self.nome} - {self.uf}"

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

class Ocupacao(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da ocupação")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Ocupação"
        verbose_name_plural = "Ocupações"

class Usuario(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="usuario",
        primary_key=True
    )
    nome = models.CharField(max_length=100, blank=True, null=True)
    data_nasc = models.DateField(blank=True, null=True)
    cpf = models.CharField(max_length=11, blank=True, null=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    doenca = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, blank=True)
    ocupacao = models.ForeignKey(Ocupacao, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome if self.nome else self.user.username

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class Agendamento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Usuário")
    ocupacao = models.ForeignKey(Ocupacao, on_delete=models.CASCADE, verbose_name="Ocupação")
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, verbose_name="Cidade")
    data_agend = models.DateField(verbose_name="Data do Agendamento")
    horario = models.TimeField(verbose_name="Horário")
    endereco = models.CharField(max_length=255, verbose_name="Endereço")

    def __str__(self):
        return f"Agendamento de {self.usuario} em {self.data_agend}"

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"

class Relatorio(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, verbose_name="Agendamento")
    qnt_agendamento = models.IntegerField(verbose_name="Quantidade de Agendamentos")
    status = models.CharField(max_length=50, choices=[
        ("pendente", "Pendente"),
        ("concluido", "Concluído"),
        ("cancelado", "Cancelado")
    ])
    avaliacao = models.TextField(null=True, blank=True, verbose_name="Avaliação")

    def __str__(self):
        return f"Relatório - {self.agendamento} ({self.status})"

    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"

class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    data_inicio = models.DateField()
    data_termino = models.DateField()
    local = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"