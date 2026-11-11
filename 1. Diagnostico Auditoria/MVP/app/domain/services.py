"""Reglas de negocio puras de Kohem Chemicals.

Sin FastAPI, SQLAlchemy, MCP ni RAG: solo aritmética y políticas comerciales.
"""


class PricingDomainService:
    """Cálculo de cotizaciones y políticas de inventario."""

    IVA_RATE = 0.19
    TOPE_PEDIDO = 50_000_000.0
    STOCK_MINIMO = 10.0

    def subtotal(self, precio_unitario: float, cantidad: float) -> float:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if precio_unitario <= 0:
            raise ValueError("El precio unitario debe ser mayor que cero.")
        return round(precio_unitario * cantidad, 2)

    def total(self, subtotales) -> float:
        return round(sum(subtotales), 2)

    def impuesto(self, base: float) -> float:
        if base < 0:
            raise ValueError("La base gravable no puede ser negativa.")
        return round(base * self.IVA_RATE, 2)

    def aplicar_tope(self, total: float) -> float:
        return round(min(total, self.TOPE_PEDIDO), 2)

    def requiere_revision(self, stock_actual: float) -> bool:
        """Política RAG: por debajo del stock mínimo la venta requiere asesor."""
        return stock_actual < self.STOCK_MINIMO
