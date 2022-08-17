import factory.django

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "username%s" % n)
    password = "Test1234"
    email = factory.Sequence(lambda n: "%s@test.test" % n)
