def filtrar_tormentas(eventos):
    """Se queda con los eventos de alto impacto del país que nos interesa, ignorando los que no tienen hora concreta (00:00 exactas)."""
    return [
        e
        for e in eventos
        if e.get("country") == "USD"
        and e.get("impact") == "High"
        and e["date"][11:19] != "00:00:00"
    ]
