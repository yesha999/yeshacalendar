from pytest_factoryboy import register

from tests.factories import UserFactory

pytest_plugins = "tests.fixtures"
register(UserFactory)

