
import pytest

from app import hello_world, add, subtract


@pytest.mark.test_001
def test_hello_world():
    assert hello_world() == "Hello World"


@pytest.mark.test_002
def test_addition():
    assert add(10, 20) == 30


@pytest.mark.test_003
def test_subtraction():
    assert subtract(20, 10) == 10
