from django.test import Client, TestCase


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_template_for_exeption_404(self):
        """Testing unexist page return 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
