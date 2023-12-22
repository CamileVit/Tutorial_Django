from django.test import TestCase

# Testes para visualização da lista de autores

from catalog.models import Author
from django.urls import reverse

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Cria autores para testes de paginação
        numero_de_autores = 13
        for autor_id in range(numero_de_autores):
            Author.objects.create(first_name='Christian {0}'.format(autor_id),
                                  last_name='Sobrenome {0}'.format(autor_id))

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/autores/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/lista_autores.html')

    def test_paginacao_eh_dez(self):
        response = self.client.get(reverse('autores'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 10)

    def test_lista_todos_autores(self):
        # Obter a segunda página e confirmar que ela possui exatamente os 3 itens restantes
        response = self.client.get(reverse('autores')+'?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['author_list']), 3)


# Testes para visualização de livros emprestados por usuário

import datetime
from django.utils import timezone

from catalog.models import BookInstance, Book, Genre, Language

from django.contrib.auth import get_user_model
User = get_user_model()

class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Cria dois usuários
        test_user1 = User.objects.create_user(
            username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(
            username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Cria um livro
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasia')
        test_language = Language.objects.create(name='Inglês')
        test_book = Book.objects.create(
            title='Título do Livro',
            summary='Meu resumo do livro',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )
        # Cria gênero como passo posterior
        objetos_de_genero_para_livro = Genre.objects.all()
        test_book.genre.set(objetos_de_genero_para_livro)
        test_book.save()

        # Cria 30 objetos BookInstance
        numero_de_copias_do_livro = 30
        for copia_do_livro in range(numero_de_copias_do_livro):
            data_de_devolucao = timezone.now() + datetime.timedelta(days=copia_do_livro % 5)
            if copia_do_livro % 2:
                o_mutuario = test_user1
            else:
                o_mutuario = test_user2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Editora Improvável, 2016', due_back=data_de_devolucao,
                                        borrower=o_mutuario, status=status)

    def test_redireciona_se_nao_estiver_logado(self):
        response = self.client.get(reverse('meus-emprestimos'))
        self.assertRedirects(
            response, '/accounts/login/?next=/catalog/meuslivros/')

    def test_logado_usa_template_correto(self):
        login = self.client.login(
            username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('meus-emprestimos'))

        # Verifica se nosso usuário está logado
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Verifica se recebemos uma resposta "sucesso"
        self.assertEqual(response.status_code, 200)

        # Verifica se usamos o template correto
        self.assertTemplateUsed(
            response, 'catalog/lista_bookinstance_mutuario.html')

    def test_apenas_livros_emprestados_na_lista(self):
        login = self.client.login(
            username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('meus-emprestimos'))

        # Verifica se nosso usuário está logado
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Verifica se recebemos uma resposta "sucesso"
        self.assertEqual(response.status_code, 200)

        # Verifica se inicialmente não temos nenhum livro na lista (nenhum emprestado)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Agora muda todos os livros para estarem emprestados
        get_dez_livros = BookInstance.objects.all()[:10]

        for copia in get_dez_livros:
            copia.status = 'o'
            copia.save()

        # Verifica se agora temos livros emprestados na lista
        response = self.client.get(reverse('meus-emprestimos'))
        # Verifica se nosso usuário está logado
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Verifica se recebemos uma resposta "sucesso"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirma que todos os livros pertencem ao testuser1 e estão emprestados
        for item_do_livro in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], item_do_livro.borrower)
            self.assertEqual(item_do_livro.status, 'o')

    def test_paginas_paginadas_para_dez(self):

        # Muda todos os livros para estarem emprestados.
        # Isso deve fazer 15 do usuário de teste.
        for copia in BookInstance.objects.all():
            copia.status = 'o'
            copia.save()

        login = self.client.login(
            username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('meus-emprestimos'))

        # Verifica se nosso usuário está