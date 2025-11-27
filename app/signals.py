from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Usuario

@receiver(post_save, sender=User)
def criar_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Usuario.objects.create(
            user=instance,
            nome=instance.username,
            email=instance.email,
            data_nasc="2000-01-01",  
            cpf="00000000000",
            telefone="00000000000",
            doenca="Não informado",
            cidade_id=1,
            ocupacao_id=1,
        )
