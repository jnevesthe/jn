from django import forms
from .models import Contato


class ContatoForm(forms.ModelForm):
    """Validação real dos dados (evita salvar nome/email/mensagem
    vazios ou em formato inválido, que o request.POST.get() cru
    permitia passar direto para o banco)."""

    class Meta:
        model = Contato
        fields = ["nome", "email", "mensagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Seu nome"}),
            "email": forms.EmailInput(attrs={"placeholder": "seu@email.com"}),
            "mensagem": forms.Textarea(attrs={"rows": 5, "placeholder": "Sua mensagem..."}),
        }
