import json
from datetime import datetime, timezone
from Agent1.ai_event_analyzer import analyze_events_with_ai
from Agent1.news_fetchers import fetch_news
from Agent1.risk_analyzer import analyze_articles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# =========================================================
# PIPELINE FUNCTION
# =========================================================

def run_agent1():
    articles = fetch_news(limit=30)

    # --------------------------------
    # AI SEMANTIC EVENT ANALYSIS
    # --------------------------------
    ai_events = analyze_events_with_ai(articles)

    # Attach AI understanding to each article
    for event in ai_events:
        index = event.get("article_index")

        if index is not None and 0 <= index < len(articles):
            articles[index]["ai_event"] = event

    # --------------------------------
    # EXISTING DETERMINISTIC ANALYSIS
    # --------------------------------
    analysis = analyze_articles(articles)

    analysis["generated_at"] = datetime.now(timezone.utc).isoformat()

    # --------------------------------
    # SAVE OUTPUT
    # --------------------------------
    output_file = BASE_DIR / "agent1_output.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            analysis,
            file,
            indent=4,
            ensure_ascii=False
        )

    return analysis




def main():

    print("========================================")
    print("   ENERGY SUPPLY CHAIN - AGENT 1")
    print("   Geopolitical Risk Intelligence")
    print("========================================\n")

    print("Fetching geopolitical news...\n")

    articles = fetch_news(limit=30)

    print(
        f"Articles collected: {len(articles)}"
    )

    print("\nAnalyzing events and risk...\n")

    analysis = analyze_articles(
        articles
    )

    # Add generation timestamp.
    analysis["generated_at"] = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    overall = analysis[
        "overall_risk"
    ]

    print("========================================")
    print("             RISK RESULT")
    print("========================================\n")

    print(
        f"Overall Risk Score: "
        f"{overall['score']}/100"
    )

    print(
        f"Overall Risk Level: "
        f"{overall['level']}"
    )

    print(
        f"Articles Analyzed: "
        f"{analysis['articles_analyzed']}"
    )

    print(
        f"Unique Events: "
        f"{analysis['unique_events']}\n"
    )

    print("Corridor Risk:\n")

    if analysis["corridors"]:

        for corridor, result in (
            analysis["corridors"].items()
        ):

            print(
                f"  {corridor}: "
                f"{result['risk_score']}/100 "
                f"({result['risk_level']}) "
                f"- {result['event_count']} events"
            )

    else:
        print("  No affected corridors detected.")

    compound = analysis[
        "compound_risk"
    ]

    print("\nCompound Risk:")

    print(
        f"  Detected: "
        f"{compound['detected']}"
    )

    print(
        f"  Severity: "
        f"{compound['severity']}"
    )

    print("\nRisk Explanation:")

    print(
        analysis["risk_explanation"]
    )

    print("\n========================================")
    print("Agent 1 completed successfully.")
    print("========================================")

    with open(
        "agent1_output.json",
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            analysis,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print(
        "\nOutput saved to: "
        "agent1_output.json"
    )


if __name__ == "__main__":
    main()