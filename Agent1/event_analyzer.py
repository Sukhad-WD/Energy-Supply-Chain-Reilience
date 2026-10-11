from datetime import datetime, timezone
from typing import Dict


# =========================================================
# EVENT RULES
# =========================================================

EVENT_RULES = {

    # -----------------------------------------------------
    # CRITICAL INFRASTRUCTURE EVENTS
    # -----------------------------------------------------

    "infrastructure_attack": {
        "keywords": [
            "pipeline attack",
            "pipeline attacked",
            "refinery attack",
            "refinery attacked",
            "oil facility attacked",
            "oil facility hit",
            "drone attack",
            "missile attack",
            "facility attack",
        ],
        "severity_score": 92,
        "supply_impact": "HIGH",
        "transport_impact": "HIGH",
        "price_impact": "HIGH",
    },

    "pipeline_disruption": {
    "keywords": [
        "pipeline shutdown",
        "pipeline shut",
        "pipeline shuts",
        "pipeline closed",
        "pipeline closes",
        "pipeline closure",
        "pipeline disruption",
        "pipeline disrupted",
        "oil pipeline shut",
        "oil pipeline shuts",
        "oil pipeline shutdown",
        "oil pipeline disrupted",
        "key oil pipeline",
        "pipeline temporarily shut"
    ],
    "severity_score": 85,
    "supply_impact": "HIGH",
    "transport_impact": "HIGH",
    "price_impact": "HIGH",
        },

    # -----------------------------------------------------
    # SHIPPING
    # -----------------------------------------------------

    "shipping_disruption": {
        "keywords": [
            "shipping disruption",
            "shipping halted",
            "shipping suspended",
            "shipping blocked",
            "shipping lane disruption",
            "tanker attack",
            "vessel attack",
            "red sea shipping",
            "shipping lane",
        ],
        "severity_score": 78,
        "supply_impact": "HIGH",
        "transport_impact": "HIGH",
        "price_impact": "HIGH",
    },

    # -----------------------------------------------------
    # ACTUAL MILITARY EVENTS
    # -----------------------------------------------------

    "military_conflict": {
        "keywords": [
            "airstrike",
            "air strike",
            "missile strike",
            "missile attack",
            "drone strike",
            "drone attack",
            "military attack",
            "military strike",
            "forces struck",
            "troops attacked",
            "bombing",
            "fighting erupted",
            "fighting re-erupted",
            "armed conflict",
        ],
        "severity_score": 68,
        "supply_impact": "MEDIUM",
        "transport_impact": "MEDIUM",
        "price_impact": "HIGH",
    },

    # -----------------------------------------------------
    # SANCTIONS
    # -----------------------------------------------------

    "sanctions": {
        "keywords": [
            "sanctioned",
            "new sanctions",
            "sanctions imposed",
            "sanctions announced",
            "export ban",
            "import ban",
            "embargo",
        ],
        "severity_score": 60,
        "supply_impact": "MEDIUM",
        "transport_impact": "LOW",
        "price_impact": "MEDIUM",
    },

    # -----------------------------------------------------
    # SUPPLY SHORTAGE
    # -----------------------------------------------------

    "supply_shortage": {
        "keywords": [
            "oil shortage",
            "supply shortage",
            "supply crisis",
            "production cut",
            "production cuts",
            "oil supply disruption",
            "supply disruption",
        ],
        "severity_score": 75,
        "supply_impact": "HIGH",
        "transport_impact": "MEDIUM",
        "price_impact": "HIGH",
    },

    # -----------------------------------------------------
    # GENERAL GEOPOLITICAL TENSION
    # -----------------------------------------------------

    "geopolitical_tension": {
        "keywords": [
            "tensions rise",
            "rising tensions",
            "heightened tensions",
            "geopolitical tension",
            "geopolitical tensions",
            "threat",
            "crisis",
            "dispute",
        ],
        "severity_score": 35,
        "supply_impact": "LOW",
        "transport_impact": "LOW",
        "price_impact": "MEDIUM",
    },
}


# =========================================================
# ENERGY CORRIDORS
# =========================================================

CORRIDOR_RULES = {

    "Strait of Hormuz": [
        "strait of hormuz",
        "hormuz",
        "persian gulf",
    ],

    "Red Sea": [
        "red sea",
    ],

    "Bab el-Mandeb": [
        "bab el-mandeb",
        "bab al-mandab",
    ],

    "Suez Canal": [
        "suez canal",
        "suez",
    ],

    "Saudi East-West Pipeline": [
        "east-west pipeline",
        "east west pipeline",
        "petroline",
        "yanbu",
        "saudi pipeline",
    ],

    "Black Sea": [
        "black sea",
        "cargo vessels",
        "black sea port",
    ],

    "Russia-Ukraine Energy Route": [
        "druzhba",
        "russia-ukraine pipeline",
    ],

    "Middle East Oil Supply": [
        "saudi oil",
        "saudi arabia",
        "iraq oil",
        "iran oil",
        "opec",
        "persian gulf",
    ],
}


# =========================================================
# SEVERITY
# =========================================================

def get_severity(score: int) -> str:
    if score >= 80:
        return "CRITICAL"

    if score >= 65:
        return "HIGH"

    if score >= 50:
        return "MEDIUM"

    if score >= 30:
        return "LOW"

    return "LOW" if score > 0 else "NO SIGNAL"


def calculate_source_weight(source: str) -> float:
    source_weights = {
        "BBC": 1.00,
        "Reuters": 1.00,
        "Al Jazeera": 0.95,
    }
    return source_weights.get(source, 0.85)


# =========================================================
# RECENCY
# =========================================================

def calculate_recency_weight(
    published_at: str
) -> float:

    try:

        published = datetime.fromisoformat(
            published_at.replace(
                "Z",
                "+00:00"
            )
        )

        if published.tzinfo is None:
            published = published.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(
            timezone.utc
        )

        age_hours = (
            now - published
        ).total_seconds() / 3600

        if age_hours < 0:
            age_hours = 0

        if age_hours <= 6:
            return 1.00

        if age_hours <= 24:
            return 0.95

        if age_hours <= 72:
            return 0.80

        if age_hours <= 168:
            return 0.60

        return 0.35

    except Exception:
        return 0.75


# =========================================================
# EVENT CLASSIFICATION
# =========================================================

def classify_event(article: Dict) -> Dict:

    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()

    full_text = f"{title} {summary}"

    # =====================================================
    # 1. PIPELINE DISRUPTION
    # =====================================================

    pipeline_words = [
        "pipeline",
        "petroline",
        "east-west pipeline",
        "east west pipeline"
    ]

    disruption_words = [
        "shut",
        "shuts",
        "shutdown",
        "closed",
        "closure",
        "disruption",
        "disrupted",
        "offline",
        "halted"
    ]

    if (
        any(word in title for word in pipeline_words)
        and any(word in title for word in disruption_words)
    ):
        return {
            "event_type": "pipeline_disruption",
            "severity_score": 85,
            "matched_keywords": [
                word for word in pipeline_words
                if word in title
            ],
            "supply_impact": "HIGH",
            "transport_impact": "HIGH",
            "price_impact": "HIGH"
        }

    # =====================================================
    # 2. INFRASTRUCTURE ATTACK
    # =====================================================

    infrastructure_words = [
        "pipeline attack",
        "pipeline attacked",
        "refinery attack",
        "refinery attacked",
        "oil facility attacked",
        "oil facility hit",
        "drone attack",
        "missile attack",
        "facility attack"
    ]

    for keyword in infrastructure_words:
        if keyword in title:
            return {
                "event_type": "infrastructure_attack",
                "severity_score": 92,
                "matched_keywords": [keyword],
                "supply_impact": "HIGH",
                "transport_impact": "HIGH",
                "price_impact": "HIGH"
            }

    # =====================================================
    # 3. SHIPPING DISRUPTION
    # =====================================================

    shipping_words = [
        "shipping disruption",
        "shipping halted",
        "shipping suspended",
        "shipping blocked",
        "shipping lane disruption",
        "tanker attack",
        "vessel attack",
        "red sea shipping"
    ]

    for keyword in shipping_words:
        if keyword in title:
            return {
                "event_type": "shipping_disruption",
                "severity_score": 78,
                "matched_keywords": [keyword],
                "supply_impact": "HIGH",
                "transport_impact": "HIGH",
                "price_impact": "HIGH"
            }

    # =====================================================
    # 4. MILITARY CONFLICT
    # =====================================================

    military_words = [
        "airstrike",
        "air strike",
        "missile strike",
        "military attack",
        "military strike",
        "forces struck",
        "troops attacked",
        "bombing",
        "fighting erupted",
        "fighting re-erupted",
        "armed conflict"
    ]

    for keyword in military_words:
        if keyword in title:
            return {
                "event_type": "military_conflict",
                "severity_score": 68,
                "matched_keywords": [keyword],
                "supply_impact": "MEDIUM",
                "transport_impact": "MEDIUM",
                "price_impact": "HIGH"
            }

    # =====================================================
    # 5. SANCTIONS
    # =====================================================

    sanctions_words = [
        "sanctioned",
        "new sanctions",
        "sanctions imposed",
        "sanctions announced",
        "export ban",
        "import ban",
        "embargo"
    ]

    for keyword in sanctions_words:
        if keyword in title:
            return {
                "event_type": "sanctions",
                "severity_score": 60,
                "matched_keywords": [keyword],
                "supply_impact": "MEDIUM",
                "transport_impact": "LOW",
                "price_impact": "MEDIUM"
            }

    # =====================================================
    # 6. SUPPLY SHORTAGE
    # =====================================================

    supply_words = [
        "oil shortage",
        "supply shortage",
        "supply crisis",
        "production cut",
        "production cuts",
        "oil supply disruption",
        "supply disruption"
    ]

    for keyword in supply_words:
        if keyword in title:
            return {
                "event_type": "supply_shortage",
                "severity_score": 75,
                "matched_keywords": [keyword],
                "supply_impact": "HIGH",
                "transport_impact": "MEDIUM",
                "price_impact": "HIGH"
            }

    # =====================================================
    # 7. GENERAL GEOPOLITICAL TENSION
    # =====================================================

    tension_words = [
        "tensions rise",
        "rising tensions",
        "heightened tensions",
        "geopolitical tension",
        "geopolitical tensions",
        "threat",
        "crisis",
        "dispute"
    ]

    for keyword in tension_words:
        if keyword in title:
            return {
                "event_type": "geopolitical_tension",
                "severity_score": 35,
                "matched_keywords": [keyword],
                "supply_impact": "LOW",
                "transport_impact": "LOW",
                "price_impact": "MEDIUM"
            }

    # =====================================================
    # 8. FALLBACK
    # =====================================================

    return {
        "event_type": "general_signal",
        "severity_score": 15,
        "matched_keywords": [],
        "supply_impact": "LOW",
        "transport_impact": "LOW",
        "price_impact": "LOW"
    }

# =========================================================
# CORRIDOR DETECTION
# =========================================================

def detect_corridors(
    article: Dict
):

    title = article.get(
        "title",
        ""
    ).lower()

    summary = article.get(
        "summary",
        ""
    ).lower()

    text = f"{title} {summary}"

    detected = []

    for corridor, keywords in (
        CORRIDOR_RULES.items()
    ):

        if any(
            keyword in text
            for keyword in keywords
        ):

            detected.append(
                corridor
            )

    return detected


# =========================================================
# EVENT ANALYSIS
# =========================================================

def analyze_event(
    article: Dict
) -> Dict:

    classification = classify_event(
        article
    )

    corridors = detect_corridors(
        article
    )

    base_score = classification[
        "severity_score"
    ]

    recency_weight = (
        calculate_recency_weight(
            article.get(
                "published_at",
                ""
            )
        )
    )

    source = article.get("source", "")
    source_weight = calculate_source_weight(source)

    adjusted_score = round(
        base_score
        * recency_weight
        * source_weight
    )

    adjusted_score = min(
        adjusted_score,
        100
    )

    return {

        "source": source,

        "title":
            article.get(
                "title",
                ""
            ),

        "summary":
            article.get(
                "summary",
                ""
            ),

        "url":
            article.get(
                "url",
                ""
            ),

        "published_at":
            article.get(
                "published_at",
                ""
            ),

        "event_type":
            classification[
                "event_type"
            ],

        "severity_score":
            adjusted_score,

        "severity":
            get_severity(
                adjusted_score
            ),

        "affected_corridors":
            corridors,

        "supply_impact":
            classification[
                "supply_impact"
            ],

        "transport_impact":
            classification[
                "transport_impact"
            ],

        "price_impact":
            classification[
                "price_impact"
            ],

        "matched_keywords":
            classification[
                "matched_keywords"
            ],
    }