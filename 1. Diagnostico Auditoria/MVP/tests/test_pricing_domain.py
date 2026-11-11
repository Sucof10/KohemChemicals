import pytest

from app.domain.services import PricingDomainService


@pytest.fixture
def pricing():
    return PricingDomainService()


def test_subtotal_exacto(pricing):
    assert pricing.subtotal(18000, 2) == 36000.0
    assert pricing.subtotal(85000, 0.5) == 42500.0


def test_subtotal_redondea_a_dos_decimales(pricing):
    assert pricing.subtotal(1234.567, 3) == 3703.7
    assert pricing.subtotal(0.1, 3) == 0.3


def test_total_suma_subtotales(pricing):
    assert pricing.total([36000.0, 42500.0, 12000.0]) == 90500.0
    assert pricing.total([]) == 0.0


def test_iva_del_19_por_ciento(pricing):
    assert pricing.impuesto(100000) == 19000.0
    assert pricing.impuesto(0) == 0.0


def test_tope_comercial(pricing):
    assert pricing.aplicar_tope(49_000_000) == 49_000_000
    assert pricing.aplicar_tope(85_000_000) == 50_000_000.0


def test_revision_por_stock_minimo(pricing):
    assert pricing.requiere_revision(9.99) is True
    assert pricing.requiere_revision(10.0) is False


def test_cantidad_cero_o_negativa(pricing):
    with pytest.raises(ValueError):
        pricing.subtotal(18000, 0)
    with pytest.raises(ValueError):
        pricing.subtotal(18000, -2)


def test_precio_invalido(pricing):
    with pytest.raises(ValueError):
        pricing.subtotal(0, 2)


def test_base_gravable_negativa(pricing):
    with pytest.raises(ValueError):
        pricing.impuesto(-1)
