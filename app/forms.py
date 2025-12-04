from django import forms
from django.utils import timezone
from .models import Agendamento

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['titulo', 'data_agend', 'horario']   # ← ADICIONADO
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'data_agend': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horario': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned = super().clean()
        data_agend = cleaned.get('data_agend')
        horario = cleaned.get('horario')

        if not data_agend or not horario:
            return cleaned

        today = timezone.localdate()
        now_time = timezone.localtime().time()

        if data_agend < today:
            raise forms.ValidationError("A data deve ser hoje ou futura.")

        if data_agend == today and horario <= now_time:
            raise forms.ValidationError("O horário deve ser no futuro.")

        qs = Agendamento.objects.filter(
            usuario=self.user,
            data_agend=data_agend,
            horario=horario
        )

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Já existe um agendamento seu nesse dia e horário.")

        return cleaned
