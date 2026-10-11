from typing import List, Dict

from Agent1.event_analyzer import (
    analyze_event,
    calculate_recency_weight,
    calculate_source_weight,
    get_severity,
)


def normalize_title(title: str) -> set:
    """
    Convert title into a set of useful words
    for simple duplicate/event similarity detection.
    """

    ignored_words = {
        "the",
        "a",
        "an",
        "of",
        "to",
        "in",
        "on",
        "for",
        "and",
        "after",
        "as",
        "with",
        "from",
    }

    words = (
        title.lower()
        .replace(",", "")
        .replace(".", "")
        .replace(":", "")
        .replace("'", "")
        .split()
    )

    return {
        word
        for word in words
        if len(word) > 2
        and word not in ignored_words
    }


def titles_are_similar(
    title1: str,
    title2: str,
) -> bool:
    """
    Simple duplicate-story detection.
    """

    words1 = normalize_title(title1)
    words2 = normalize_title(title2)

    if not words1 or not words2:
        return False

    overlap = len(
        words1.intersection(words2)
    )

    smaller = min(
        len(words1),
        len(words2)
    )

    similarity = overlap / smaller

    return similarity >= 0.60


def group_duplicate_events(
    events: List[Dict]
) -> List[Dict]:
    """
    Group articles likely describing the same event.

    We retain the highest-severity representation
    and record how many independent sources reported it.
    """

    groups = []

    for event in events:

        matched_group = None

        for group in groups:

            representative = group[
                "representative"
            ]

            same_type = (
                representative["event_type"]
                == event["event_type"]
            )

            similar_title = titles_are_similar(
                representative["title"],
                event["title"],
            )

            if same_type and similar_title:
                matched_group = group
                break

        if matched_group:

            matched_group["articles"].append(
                event
            )

            matched_group["sources"].add(
                event["source"]
            )

            if (
                event["severity_score"]
                >
                matched_group[
                    "representative"
                ]["severity_score"]
            ):
                matched_group[
                    "representative"
                ] = event

        else:

            groups.append(
                {
                    "representative": event,
                    "articles": [event],
                    "sources": {
                        event["source"]
                    },
                }
            )

    results = []

    for index, group in enumerate(
        groups,
        start=1
    ):

        representative = dict(
            group["representative"]
        )

        source_count = len(
            group["sources"]
        )

        # Multiple independent sources increase
        # confidence but do not create a fake new event.
        confidence_bonus = min(
            (source_count - 1) * 5,
            10
        )

        adjusted_score = min(
            representative["severity_score"]
            + confidence_bonus,
            100
        )

        if source_count >= 3:
            confidence = "HIGH"

        elif source_count == 2:
            confidence = "MEDIUM"

        else:
            confidence = "SINGLE_SOURCE"

        representative[
            "event_id"
        ] = f"EVT-{index:03d}"

        representative[
            "severity_score"
        ] = adjusted_score

        representative[
            "severity"
        ] = get_severity(
            adjusted_score
        )

        representative[
            "source_count"
        ] = source_count

        representative[
            "source_confidence"
        ] = confidence

        representative[
            "sources"
        ] = sorted(
            group["sources"]
        )

        results.append(
            representative
        )

    return results


def calculate_corridor_risk(
    events: List[Dict]
) -> Dict:

    corridor_event_scores = {}

    for event in events:

        for corridor in event[
            "affected_corridors"
        ]:

            corridor_event_scores.setdefault(
                corridor,
                []
            )

            corridor_event_scores[
                corridor
            ].append(
                event["severity_score"]
            )

    results = {}

    for corridor, scores in (
        corridor_event_scores.items()
    ):

        # Highest event matters most.
        highest = max(scores)

        average = sum(scores) / len(scores)

        score = round(
            highest * 0.70
            + average * 0.30
        )

        # Multiple events increase pressure,
        # but progressively less than the previous version.
        if len(scores) >= 4:
            score += 5

        elif len(scores) == 3:
            score += 3

        elif len(scores) == 2:
            score += 2

        score = min(score, 99)

        results[corridor] = {
            "risk_score": score,
            "risk_level": get_severity(score),
            "event_count": len(scores),
        }

    return results


def detect_compound_risk(
    events: List[Dict],
    corridors: Dict,
) -> Dict:

    high_events = [
        event
        for event in events
        if event["severity_score"] >= 60
    ]

    high_corridors = [
        name
        for name, result
        in corridors.items()
        if result["risk_score"] >= 60
    ]

    detected = (
        len(high_events) >= 2
        and len(high_corridors) >= 2
    )

    if (
        len(high_events) >= 3
        and len(high_corridors) >= 2
    ):
        severity = "CRITICAL"

    elif detected:
        severity = "HIGH"

    else:
        severity = "LOW"

    return {
        "detected": detected,
        "severity": severity,
        "high_risk_event_count": len(high_events),
        "high_risk_corridors": high_corridors,
    }


def calculate_overall_risk(
    events: List[Dict],
    corridors: Dict,
    compound: Dict,
) -> int:

    if not events:
        return 0

    event_scores = [
        event["severity_score"]
        for event in events
    ]

    highest_event = max(event_scores)

    # Take the three strongest events.
    strongest_events = sorted(
        event_scores,
        reverse=True
    )[:3]

    event_average = (
        sum(strongest_events)
        / len(strongest_events)
    )

    corridor_scores = [
        result["risk_score"]
        for result in corridors.values()
    ]

    highest_corridor = (
        max(corridor_scores)
        if corridor_scores
        else 0
    )

    overall_score = round(
        highest_event * 0.35
        + event_average * 0.25
        + highest_corridor * 0.25
        + (
            sum(corridor_scores)
            / len(corridor_scores)
            if corridor_scores
            else 0
        ) * 0.15
    )

    # Compound risk is important, but should not
    # automatically force the score to 100.
    if compound["detected"]:
        overall_score += 5

    return min(overall_score, 99)


def create_risk_explanation(
    overall_score: int,
    events: List[Dict],
    compound: Dict,
) -> str:

    if not events:
        return (
            "No significant geopolitical "
            "energy-supply signals were detected."
        )

    strongest = max(
        events,
        key=lambda event:
        event["severity_score"]
    )

    explanation = (
        f"Overall risk is "
        f"{get_severity(overall_score)}. "
        f"The strongest detected event is "
        f"'{strongest['title']}' "
        f"classified as "
        f"{strongest['event_type']} "
        f"with severity "
        f"{strongest['severity']}."
    )

    if compound["detected"]:

        explanation += (
            " Multiple simultaneous high-risk "
            "events affect more than one energy "
            "corridor, creating compound "
            "supply-chain risk."
        )

    return explanation


def analyze_articles(
    articles: List[Dict]
) -> Dict:

    raw_events = []

    for article in articles:

        # --------------------------------
        # USE AI SEMANTIC ANALYSIS
        # --------------------------------
        ai_event = article.get("ai_event")

        if ai_event:

            severity_map = {
                "LOW": 35,
                "MEDIUM": 55,
                "HIGH": 72,
                "CRITICAL": 90,
            }
            impact_map = {
                "NONE": 0,
                "LOW": 30,
                "MEDIUM": 55,
                "HIGH": 72,
                "CRITICAL": 90,
            }

            severity = str(
                ai_event.get("severity", "LOW")
            ).upper()

            if severity not in severity_map:
                severity = "LOW"

            severity_score = severity_map[severity]

            # --------------------------------
            # ENERGY RELEVANCE ADJUSTMENT
            # --------------------------------
            supply_impact = ai_event.get(
                "supply_impact",
                "NONE"
            )

            transport_impact = ai_event.get(
                "transport_impact",
                "NONE"
            )

            price_impact = ai_event.get(
                "price_impact",
                "NONE"
            )

            affected_corridors = ai_event.get(
                "affected_corridors",
                []
            )

            energy_impacts = [
                str(supply_impact).upper(),
                str(transport_impact).upper(),
                str(price_impact).upper(),
            ]
            valid_impacts = [
                impact if impact in impact_map else "NONE"
                for impact in energy_impacts
            ]

            has_energy_impact = any(
                impact != "NONE"
                for impact in valid_impacts
            )

            if not isinstance(affected_corridors, list):
                affected_corridors = []
            affected_corridors = [
                corridor.strip()
                for corridor in affected_corridors
                if isinstance(corridor, str) and corridor.strip()
            ]
            has_corridor = bool(affected_corridors)

            if (
                not has_energy_impact
                and not has_corridor
            ):
                severity_score = min(severity_score, 10)
            elif has_energy_impact:
                severity_score = min(
                    severity_score,
                    max(impact_map[impact] for impact in valid_impacts),
                )

            published_at = article.get("published_at", "")
            source = article.get("source", "")
            severity_score = round(
                severity_score
                * calculate_recency_weight(published_at or "")
                * calculate_source_weight(source)
            )
            severity_score = min(max(severity_score, 0), 100)

            event = {
                "source": article.get(
                    "source",
                    ""
                ),

                "title": article.get(
                    "title",
                    ""
                ),

                "summary": article.get(
                    "summary",
                    ""
                ),

                "url": article.get(
                    "url",
                    ""
                ),

                "published_at": article.get(
                    "published_at"
                ),

                "event_type": ai_event.get(
                    "event_type",
                    "general_signal"
                ),

                "severity_score": severity_score,

                "severity": get_severity(severity_score),

                "affected_corridors": affected_corridors,

                "supply_impact": valid_impacts[0],

                "transport_impact": valid_impacts[1],

                "price_impact": valid_impacts[2],

                "matched_keywords": [],

                "ai_event_description": ai_event.get(
                    "event_description",
                    ""
                ),

                "ai_confidence": ai_event.get(
                    "confidence"
                ),
            }

            raw_events.append(event)

        # --------------------------------
        # FALLBACK TO EXISTING RULE ENGINE
        # --------------------------------
        else:

            event = analyze_event(article)

            raw_events.append(event)

    # --------------------------------
    # DUPLICATE EVENT GROUPING
    # --------------------------------
    events = group_duplicate_events(
        raw_events
    )

    # --------------------------------
    # CORRIDOR RISK
    # --------------------------------
    corridors = calculate_corridor_risk(
        events
    )

    # --------------------------------
    # COMPOUND RISK
    # --------------------------------
    compound = detect_compound_risk(
        events,
        corridors,
    )

    # --------------------------------
    # OVERALL RISK
    # --------------------------------
    overall_score = calculate_overall_risk(
        events,
        corridors,
        compound,
    )

    return {
        "overall_risk": {
            "score": overall_score,
            "level": get_severity(
                overall_score
            ),
        },

        "risk_explanation":
            create_risk_explanation(
                overall_score,
                events,
                compound,
            ),

        "compound_risk": compound,

        "corridors": corridors,

        "articles_analyzed":
            len(articles),

        "unique_events":
            len(events),

        "events": events,
    }