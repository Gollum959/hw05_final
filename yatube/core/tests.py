from django.test import TestCase


class StaticURLTests(TestCase):

    def test_template_for_exeption_404(self):
        """Testing unexist page return 404."""
        response = self.client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
