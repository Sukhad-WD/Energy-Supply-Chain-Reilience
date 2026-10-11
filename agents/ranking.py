from utils.scoring import route_penalty
from utils.scoring import volume_score


def calculate_score(supplier, impact):

    score = 100

    score -= supplier["cost_per_barrel"] * 0.3

    score -= supplier["delivery_days"] * 2

    score -= supplier["risk"] * 0.5

    score -= route_penalty(
        supplier,
        impact["affected_route"]
    )

    score += volume_score(
        impact["required_volume"],
        supplier["available_volume"]
    )

    return round(score,2)


def rank_suppliers(suppliers, impact):

    for supplier in suppliers:

        supplier["score"] = calculate_score(
            supplier,
            impact
        )

    suppliers.sort(
        key=lambda x:x["score"],
        reverse=True
    )

    return suppliers