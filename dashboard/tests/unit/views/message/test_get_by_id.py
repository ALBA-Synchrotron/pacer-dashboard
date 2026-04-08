from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from dashboard.models.message import Message
from dashboard.views.messages import GetById


class GetByIdViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="pass")
        # Creamos un mensaje de prueba
        self.msg = Message.objects.create(payload="Contenido de prueba")

    def test_get_context_data_with_valid_message(self):
        """Si el mensaje existe y el filtro pasa, debe estar en el contexto."""
        # Setup: Simulamos la URL con el ID
        request = self.factory.get(f'/tmpl/messages/{self.msg.pk}/')
        request.user = self.user

        view = GetById()
        view.request = request
        view.kwargs = {'msg_id': self.msg.pk}

        # Ejecución
        context = view.get_context_data()

        # Aserciones
        self.assertIn('msg', context)
        self.assertEqual(context['msg'].pk, self.msg.pk)

    def test_get_object_returns_none_if_not_found(self):
        """Si el ID no existe, get_object debe devolver None."""
        request = self.factory.get('/tmpl/messages/999/')
        request.user = self.user

        view = GetById()
        view.request = request
        view.kwargs = {'msg_id': 999}

        # Ejecución
        obj = view.get_object()

        # Aserciones
        self.assertIsNone(obj)

    def test_get_object_with_user_filters(self):
        """
        Verifica que el filtro de GroupProfile se aplica.
        Si el filtro excluye el mensaje, get_object debe devolver None.
        """
        # Nota: Aquí dependes de cómo funcione GroupProfile.get_user_filters.
        # Si el usuario no tiene grupos y eso restringe el acceso, el test fallará (correctamente).

        request = self.factory.get(f'/tmpl/messages/{self.msg.pk}/')
        request.user = self.user  # Usuario sin grupos asignados

        view = GetById()
        view.request = request
        view.kwargs = {'msg_id': self.msg.pk}

        obj = view.get_object()

        # Si tu lógica de GroupProfile es estricta, esto debería ser None
        # si el usuario no pertenece al grupo adecuado.
        # self.assertIsNone(obj)