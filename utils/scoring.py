def route_penalty(supplier, affected_route):

    if affected_route.lower() in supplier["route"].lower():
        return 40

    return 0


def volume_score(volume_needed, supplier_volume):

    if supplier_volume >= volume_needed:
        return 20

    return supplier_volume / volume_needed * 20