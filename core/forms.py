from django import forms
from .models import Solicitacao


class SolicitacaoForm(forms.ModelForm):
    class Meta:
        model = Solicitacao
        fields = [
            "descricao",
            "foto",
            "materiais",
            "tipo_solicitacao",
            "requested_date",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # restrict available days for agendamento requests
        choices = []
        for d in Solicitacao.available_days(count=10):
            choices.append((d, d.strftime("%Y-%m-%d")))
        self.fields["requested_date"] = forms.ChoiceField(
            choices=[("", "--------")] + choices,
            required=False,
            help_text="Pick an available day for the cleanup crew",
        )

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get("tipo_solicitacao")
        req_date = cleaned.get("requested_date")
        if tipo == Solicitacao.TipoSolicitacao.AGENDAMENTO:
            if not req_date:
                raise forms.ValidationError("A date is required for pickup requests.")
            if not Solicitacao.is_date_available(req_date):
                raise forms.ValidationError("Selected date is not available for scheduling.")
        else:
            # denuncias should not supply a requested_date
            cleaned["requested_date"] = None
        return cleaned
