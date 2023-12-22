from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime  # para verificar o intervalo de datas de renovação.

from django import forms

class RenewBookForm(forms.Form):
    """Formulário para um bibliotecário renovar livros."""
    renewal_date = forms.DateField(
            help_text="Insira uma data entre hoje e 4 semanas (padrão: 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Verifique se a data não está no passado.
        if data < datetime.date.today():
            raise ValidationError(_('Data inválida - renovação no passado'))
        # Verifique se a data está no intervalo permitido para alteração pelo bibliotecário (+4 semanas)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Data inválida - renovação com mais de 4 semanas de antecedência'))

        # Lembre-se de sempre retornar os dados limpos.
        return data