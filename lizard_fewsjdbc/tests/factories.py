import factory

from ..models import JdbcSource


class JdbcSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = JdbcSource
