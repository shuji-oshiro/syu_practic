from app.src.outprint import getData, getData2
from app.tests import conftest


def test_getData():
    assert getData(10) == 20 

def test_getData2():
    assert getData2(10) == 30


