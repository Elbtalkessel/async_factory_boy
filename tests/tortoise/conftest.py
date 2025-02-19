import asyncio

import pytest
from tortoise.contrib.test import finalizer, initializer
from tortoise.transactions import current_transaction_map


@pytest.fixture(scope="function", autouse=True)
def db(request, event_loop: asyncio.AbstractEventLoop):
    initializer(['tests.tortoise.models'], db_url="sqlite://test.db", loop=event_loop)
    current_transaction_map["default"] = current_transaction_map["models"]

    yield

    request.addfinalizer(finalizer)
