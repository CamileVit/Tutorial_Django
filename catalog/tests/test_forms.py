from django.test import TestCase

# Crie seus testes aqui.

import datetime
from catalog.forms import RenewBookForm


class RenewBookFormTest(TestCase):

    def test_renew_form_date_in_past(self):
        """Testa se o formulário é inválido se renewal_date estiver antes de hoje."""
        data = datetime.date.today() - datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': data})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        """Testa se o formulário é inválido se renewal_date estiver a mais de 4 semanas a partir de hoje."""
        data = datetime.date.today() + datetime.timedelta(weeks=4) + datetime.timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': data})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        """Testa se o formulário é válido se renewal_date for hoje."""
        data = datetime.date.today()
        form = RenewBookForm(data={'renewal_date': data})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        """Testa se o formulário é válido se renewal_date estiver dentro de 4 semanas."""
        data = datetime.date.today() + datetime.timedelta(weeks=4)
        form = RenewBookForm(data={'renewal_date': data})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_field_label(self):
        """Testa se o rótulo de renewal_date é 'renewal date'."""
        form = RenewBookForm()
        self.assertTrue(
            form.fields['renewal_date'].label is None or
            form.fields['renewal_date'].label == 'renewal date')

    def test_renew_form_date_field_help_text(self):
        """Testa se o texto de ajuda de renewal_date está como esperado."""
        form = RenewBookForm()
        self.assertEqual(
            form.fields['renewal_date'].help_text,
            'Enter a date between now and 4 weeks (default 3).')