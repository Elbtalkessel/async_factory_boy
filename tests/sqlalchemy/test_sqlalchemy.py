import factory
import pytest
import sqlalchemy
from factory import FactoryError, Iterator

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from .conftest import sc_session
from .factory import (
    ChildModelWithSelfAttributeFactory,
    MultifieldModelFactory,
    NonIntegerPkFactory,
    NoSessionFactory,
    SessionGetterFactory,
    StandardFactory,
    WithGetOrCreateFieldFactory,
    WithMultipleGetOrCreateFieldsFactory,
)
from .models import MultiFieldModel, SpecialFieldModel


class TestSQLAlchemyPkSequence:
    @pytest.fixture(autouse=True)
    def setup(self):
        StandardFactory.reset_sequence(1)

    @pytest.mark.asyncio
    async def test_pk_first(self):
        std = await StandardFactory.build()
        assert "foo1" == std.foo

    @pytest.mark.asyncio
    async def test_pk_many(self):
        std1 = await StandardFactory.build()
        std2 = await StandardFactory.build()
        assert "foo1" == std1.foo
        assert "foo2" == std2.foo

    @pytest.mark.asyncio
    async def test_pk_many_batch(self):
        stds = await StandardFactory.build_batch(3)
        assert "foo1" == stds[0].foo
        assert "foo2" == stds[1].foo
        assert "foo3" == stds[2].foo

    @pytest.mark.asyncio
    async def test_pk_creation(self):
        std1 = await StandardFactory.create()
        assert "foo1" == std1.foo
        assert 1 == std1.id

        StandardFactory.reset_sequence()
        std2 = await StandardFactory.create()
        assert "foo0" == std2.foo
        assert 0 == std2.id

    @pytest.mark.asyncio
    async def test_pk_creation_batch(self):
        stds = await StandardFactory.create_batch(3)
        assert "foo1" == stds[0].foo
        assert "foo2" == stds[1].foo
        assert "foo3" == stds[2].foo

    @pytest.mark.asyncio
    async def test_pk_force_value(self):
        std1 = await StandardFactory.create(id=10)
        assert "foo1" == std1.foo  # sequence and pk are unrelated
        assert 10 == std1.id

        StandardFactory.reset_sequence()
        std2 = await StandardFactory.create()
        assert "foo0" == std2.foo  # Sequence doesn't care about pk
        assert 0 == std2.id


class TestSQLAlchemyGetOrCreate:
    @pytest.mark.asyncio
    async def test_simple_call(self):
        obj1 = await WithGetOrCreateFieldFactory(foo="foo1")
        obj2 = await WithGetOrCreateFieldFactory(foo="foo1")
        assert obj1 == obj2

    @pytest.mark.asyncio
    async def test_missing_arg(self):
        with pytest.raises(FactoryError):
            await MultifieldModelFactory()

    @pytest.mark.asyncio
    async def test_multicall(self, db_session):
        objs = await MultifieldModelFactory.create_batch(
            6,
            slug=Iterator(["main", "alt"]),
        )
        assert 6 == len(objs)
        assert 2 == len(set(objs))

        result = (
            (await db_session.execute(sqlalchemy.select(MultiFieldModel.slug).order_by(MultiFieldModel.slug)))
            .scalars()
            .all()
        )
        assert list(result) == ["alt", "main"]


class TestMultipleGetOrCreateFields:
    @pytest.mark.asyncio
    async def test_one_defined(self):
        obj1 = await WithMultipleGetOrCreateFieldsFactory()
        obj2 = await WithMultipleGetOrCreateFieldsFactory(slug=obj1.slug)
        assert obj1 == obj2

    @pytest.mark.asyncio
    async def test_both_defined(self):
        obj1 = await WithMultipleGetOrCreateFieldsFactory()
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            await WithMultipleGetOrCreateFieldsFactory(slug=obj1.slug, text="alt")

    @pytest.mark.asyncio
    async def test_unique_field_not_in_get_or_create(self):
        await WithMultipleGetOrCreateFieldsFactory(title="Title")
        with pytest.raises(sqlalchemy.exc.IntegrityError):
            await WithMultipleGetOrCreateFieldsFactory(title="Title")


class TestSQLAlchemyNonIntegerPk:
    @pytest.fixture(autouse=True)
    def setup(self):
        yield
        NonIntegerPkFactory.reset_sequence()

    @pytest.mark.asyncio
    async def test_first(self):
        nonint = await NonIntegerPkFactory.build()
        assert "foo0" == nonint.id

    @pytest.mark.asyncio
    async def test_many(self):
        nonint1 = await NonIntegerPkFactory.build()
        nonint2 = await NonIntegerPkFactory.build()

        assert "foo0" == nonint1.id
        assert "foo1" == nonint2.id

    @pytest.mark.asyncio
    async def test_creation(self):
        nonint1 = await NonIntegerPkFactory.create()
        assert "foo0" == nonint1.id

        NonIntegerPkFactory.reset_sequence()
        nonint2 = await NonIntegerPkFactory.build()
        assert "foo0" == nonint2.id

    @pytest.mark.asyncio
    async def test_force_pk(self):
        nonint1 = await NonIntegerPkFactory.create(id="foo10")
        assert "foo10" == nonint1.id

        NonIntegerPkFactory.reset_sequence()
        nonint2 = await NonIntegerPkFactory.create()
        assert "foo0" == nonint2.id


class TestSQLAlchemyNoSession:
    @pytest.mark.asyncio
    async def test_build_does_not_raises_exception_when_no_session_was_set(self):
        NoSessionFactory.reset_sequence()  # Make sure we start at test ID 0

        inst0 = await NoSessionFactory.build()
        inst1 = await NoSessionFactory.build()
        assert inst0.id == 0
        assert inst1.id == 1


class TestNameConflict:
    """Regression test for `TypeError: _save() got multiple values for argument 'session'`
    See #775.
    """

    @pytest.mark.asyncio
    async def test_no_name_conflict_on_save(self):
        class SpecialFieldWithSaveFactory(AsyncSQLAlchemyFactory):
            class Meta:
                model = SpecialFieldModel
                sqlalchemy_session = sc_session

            id = factory.Sequence(lambda n: n)
            session = ""

        saved_child = await SpecialFieldWithSaveFactory()
        assert saved_child.session == ""

    @pytest.mark.asyncio
    async def test_no_name_conflict_on_get_or_create(self):
        class SpecialFieldWithGetOrCreateFactory(AsyncSQLAlchemyFactory):
            class Meta:
                model = SpecialFieldModel
                sqlalchemy_get_or_create = ("session",)
                sqlalchemy_session = sc_session

            id = factory.Sequence(lambda n: n)
            session = ""

        get_or_created_child = await SpecialFieldWithGetOrCreateFactory()
        assert get_or_created_child.session == ""


class TestSQLAlchemyWithSessionGetterPkSequence:
    @pytest.fixture(autouse=True)
    def setup(self):
        SessionGetterFactory.reset_sequence(1)

    @pytest.mark.asyncio
    async def test_pk_creation(self):
        std1 = await SessionGetterFactory.create()
        assert "foo1" == std1.foo
        assert 1 == std1.id

        SessionGetterFactory.reset_sequence()
        std2 = await SessionGetterFactory.create()
        assert "foo0" == std2.foo
        assert 0 == std2.id

    @pytest.mark.asyncio
    async def test_pk_force_value(self):
        std1 = await SessionGetterFactory.create(id=10)
        assert "foo1" == std1.foo  # sequence and pk are unrelated
        assert 10 == std1.id

        SessionGetterFactory.reset_sequence()
        std2 = await SessionGetterFactory.create()
        assert "foo0" == std2.foo  # Sequence doesn't care about pk
        assert 0 == std2.id


class TestChildModelWithSelfAttributeFactory:
    @pytest.mark.asyncio
    async def test_subfactory(self):
        child = await ChildModelWithSelfAttributeFactory.create()

        assert child.id is not None
        assert child.name is not None
        assert child.parent_id is not None
        assert child.parent is not None
        assert child.parent.id is not None
        assert child.parent.name is not None
