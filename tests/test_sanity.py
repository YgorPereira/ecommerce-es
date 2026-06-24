import pytest

@pytest.mark.unit
def test_unit_ok():
    assert 1 + 1 == 2

@pytest.mark.integration
def test_integration_ok():
    assert "banco" == "banco"

@pytest.mark.smoke
def test_smoke_ok():
    assert True