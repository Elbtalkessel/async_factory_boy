import factory

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from . import models
from .conftest import sc_session


def get_scoped_session():
    return sc_session


class StandardFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = sc_session

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class SessionGetterFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = None
        sqlalchemy_session_factory = get_scoped_session

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class NonIntegerPkFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.NonIntegerPk
        sqlalchemy_session = sc_session

    id = factory.Sequence(lambda n: "foo%d" % n)


class NoSessionFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_session = None

    id = factory.Sequence(lambda n: n)


class MultifieldModelFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.MultiFieldModel
        sqlalchemy_get_or_create = ("slug",)
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithGetOrCreateFieldFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.StandardModel
        sqlalchemy_get_or_create = ("foo",)
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    foo = factory.Sequence(lambda n: "foo%d" % n)


class WithMultipleGetOrCreateFieldsFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.MultifieldUniqueModel
        sqlalchemy_get_or_create = (
            "slug",
            "text",
        )
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    slug = factory.Sequence(lambda n: "slug%s" % n)
    text = factory.Sequence(lambda n: "text%s" % n)


class ParentModelFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.ParentModel
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "name%d" % n)


class ChildModelWithSelfAttributeFactory(AsyncSQLAlchemyFactory):
    class Meta:
        model = models.ChildModel
        sqlalchemy_session = sc_session
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "name%d" % n)
    parent = factory.SubFactory(ParentModelFactory)
    parent_name = factory.SelfAttribute("parent.name")
