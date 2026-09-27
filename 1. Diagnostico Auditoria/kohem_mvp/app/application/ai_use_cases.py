class AIUseCases:
    def respond(self, message: str) -> tuple[str, bool, str | None]:
        text = message.lower()
        transfer_terms = ["formulación", "formula", "técnico", "tecnico", "problema", "urgente", "reclamo", "asesor"]
        if any(term in text for term in transfer_terms):
            return (
                "Puedo registrar tu consulta, pero este caso requiere revisión de un asesor de Kohem Chemicals.",
                True,
                "La consulta puede requerir conocimiento técnico o intervención humana."
            )
        if "stock" in text or "disponibilidad" in text:
            return ("Puedes consultar la disponibilidad de materias primas mediante el catálogo del sistema.", False, None)
        if "pedido" in text or "comprar" in text:
            return ("Puedes crear un pedido seleccionando las materias primas disponibles y las cantidades requeridas.", False, None)
        return ("Puedo ayudarte con disponibilidad, pedidos y orientación inicial sobre el proceso de compra.", False, None)
