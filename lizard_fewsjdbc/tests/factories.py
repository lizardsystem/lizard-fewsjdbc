import factory

from lizard_fewsjdbc.models import JdbcSource


class JdbcSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = JdbcSource
