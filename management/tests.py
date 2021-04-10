from django.test import TestCase

from .models import User, Unit, Tenant, Maintenance, Document, Email
# Create your tests here.

class UnitTestCase(TestCase):
    def setUp(self):
        pass

    def test_valid_unit(self):
        p1 = User.objects.create(role="manager", phone_number="0123456789")
        u = Unit.objects.create(manager=p1, lease=1000, sqft=800, bed=2, bath=1, photo="None", location="USA")
        self.assertTrue(u.is_valid_unit())

    def test_invalid_unit(self):
        p1 = User.objects.create(role="manager", phone_number="0123456789")
        u = Unit.objects.create(manager=p1, lease=-1000, sqft=800, bed=2, bath=1, photo="None", location="USA")
        self.assertFalse(u.is_valid_unit())
