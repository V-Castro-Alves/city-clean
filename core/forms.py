import datetime

from django import forms
from django.conf import settings as djsettings
from .models import Solicitacao


class DenunciaForm(forms.ModelForm):
    latitude = forms.DecimalField(widget=forms.HiddenInput(), max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), max_digits=9, decimal_places=6)

    class Meta:
        model = Solicitacao
        fields = ["descricao", "materiais", "volume_estimado", "foto", "foto2", "foto3", "latitude", "longitude"]
        widgets = {
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descreva o problema observado, o tipo de resíduo e qualquer detalhe relevante..."}),
            "volume_estimado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: várias sacolas, entulho, móveis..."}),
            "materiais": forms.CheckboxSelectMultiple(),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "foto2": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "foto3": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descricao"].required = True
        self.fields["foto"].required = True
        self.fields["foto2"].required = False
        self.fields["foto3"].required = False
        self.fields["volume_estimado"].required = False

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lng = cleaned.get("longitude")
        if lat is not None and lng is not None:
            if not (djsettings.SERVICE_AREA_LAT_MIN <= lat <= djsettings.SERVICE_AREA_LAT_MAX) or \
               not (djsettings.SERVICE_AREA_LNG_MIN <= lng <= djsettings.SERVICE_AREA_LNG_MAX):
                raise forms.ValidationError("Localização fora da área de atendimento.")
        return cleaned


class AgendamentoForm(forms.ModelForm):
    latitude = forms.DecimalField(widget=forms.HiddenInput(), max_digits=9, decimal_places=6)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), max_digits=9, decimal_places=6)

    class Meta:
        model = Solicitacao
        fields = ["descricao", "foto", "foto2", "foto3", "materiais", "volume_estimado", "requested_date", "latitude", "longitude"]
        widgets = {
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descreva os itens que deseja descartar..."}),
            "volume_estimado": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: 2 sacolas, 1 geladeira, 3 caixas..."}),
            "materiais": forms.CheckboxSelectMultiple(),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "foto2": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "foto3": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["descricao"].required = True
        self.fields["volume_estimado"].required = True
        self.fields["foto"].required = True
        self.fields["foto2"].required = False
        self.fields["foto3"].required = False
        start_date = datetime.date.today() + datetime.timedelta(days=2)
        choices = []
        for d in Solicitacao.available_days(start_date=start_date, count=10):
            choices.append((d, d.strftime("%d/%m/%Y")))
        self.fields["requested_date"] = forms.ChoiceField(
            choices=[("", "Selecione uma data...")] + choices,
            required=True,
            widget=forms.Select(attrs={"class": "form-select"}),
        )

    def clean_requested_date(self):
        value = self.cleaned_data.get("requested_date")
        if not value:
            raise forms.ValidationError("Selecione uma data disponível.")
        if not Solicitacao.is_date_available(value):
            raise forms.ValidationError("A data selecionada não está mais disponível.")
        return value

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lng = cleaned.get("longitude")
        if lat is not None and lng is not None:
            if not (djsettings.SERVICE_AREA_LAT_MIN <= lat <= djsettings.SERVICE_AREA_LAT_MAX) or \
               not (djsettings.SERVICE_AREA_LNG_MIN <= lng <= djsettings.SERVICE_AREA_LNG_MAX):
                raise forms.ValidationError("Localização fora da área de atendimento.")
        return cleaned


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
