import os
os.environ["MIRROR_UNIT_TEST"] = True
import pytest

from .....models import User
from .....errors import Duplicate, Missing
from .....api.routes import users


@pytest.fixture
def sample() -> User:
    return User(username="BOBBI", email="yatest@mail.ru", password="testpassword", about="Ya testovaya zapis")


@pytest.fixture
def fakes() -> list[User]:
    return users.get_all()


