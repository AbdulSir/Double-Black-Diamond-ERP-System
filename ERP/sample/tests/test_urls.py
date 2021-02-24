from django.test import SimpleTestCase
from django.urls import reverse, resolve
from sample.views import *


class TestUrls(SimpleTestCase):

    def test_home_url_is_resolved(self):
        url = reverse ('home')
        self.assertEquals(resolve(url).func, home)

    def test_login_url_is_resolved(self):
        url = reverse ('login')
        self.assertEquals(resolve(url).func, loginPage)

    def test_register_url_is_resolved(self):
        url = reverse ('register')
        self.assertEquals(resolve(url).func, register)

    def test_logout_url_is_resolved(self):
        url = reverse ('logout')
        self.assertEquals(resolve(url).func, logoutUser)

    def test_generate_url_is_resolved(self):
        url = reverse ('generate')
        self.assertEquals(resolve(url).func, generateReport)

    def test_sales_url_is_resolved(self):
        url = reverse ('sales')
        self.assertEquals(resolve(url).func, salesViewPage)

    def test_manufacturing_url_is_resolved(self):
        url = reverse ('manufacturing')
        self.assertEquals(resolve(url).func, manufacturingViewPage)

    def test_inventory_url_is_resolved(self):
        url = reverse ('inventory')
        self.assertEquals(resolve(url).func, inventory)                         