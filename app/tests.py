from django.test import TestCase
from django.urls import resolve
from .views import dashboard


class DashBoardPageTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dashboard_page_resolves(self):
        view = resolve('/dashboard/')
        self.assertEqual(
            view.func.__name__, dashboard.__name__
        )
