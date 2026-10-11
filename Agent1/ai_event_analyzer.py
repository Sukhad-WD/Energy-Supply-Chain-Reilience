import json
import os
import re
from urllib import response

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def analyze_events_with_ai(articles):
    """
    Use Gemini to understand the meaning of news articles.
    This does NOT calculate the final risk score.
    It only extracts structured event information.
    """

    if not articles:
        return []

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )

    articles_text = ""

    for index, article in enumerate(articles):
        title = article.get("title", "")
        summary = article.get("summary", "")
        source = article.get("source", "")

        articles_text += f"""
ARTICLE {index}

Source: {source}
Title: {title}
Summary: {summary}

"""

    prompt = f"""
You are an energy supply-chain risk event analyzer.

Analyze the following news articles.

Your job is NOT to invent facts and NOT to calculate a numeric risk score.

Instead, understand what actually happened in each article.

For every article, identify:

1. event_type
2. event_description
3. direct_energy_impact
4. supply_impact
5. transport_impact
6. price_impact
7. severity
8. affected_corridors
9. confidence

Use these severity levels only:
LOW
MEDIUM
HIGH
CRITICAL

Use these impact levels only:
NONE
LOW
MEDIUM
HIGH
CRITICAL

Possible event types include:
- military_conflict
- tanker_attack
- maritime_disruption
- shipping_disruption
- pipeline_disruption
- refinery_disruption
- port_disruption
- export_restriction
- blockade
- sanctions
- geopolitical_tension
- infrastructure_attack
- production_disruption
- price_shock
- general_signal

These are examples, NOT a keyword list.
If the article describes an event that does not fit one of them,
use the closest meaningful event_type.

IMPORTANT RULES:

- Understand the meaning of the article, not just individual keywords.
- A tanker/vessel attack can be a maritime disruption even if the
  article never uses the word "disruption".
- A shipping suspension can be a transport disruption even if there
  is no attack.
- A pipeline shutdown can be a supply disruption even if there is no
  military attack.
- Do not classify ordinary diplomatic or political news as a supply
  disruption unless the article provides evidence of an actual impact.
- Do not invent affected corridors.
- Only identify a corridor when the article explicitly mentions it
  or the location clearly identifies it.
- Do not invent quantities, losses, casualties, production volumes,
  or economic effects.
- If something cannot be determined from the article, use NONE,
  UNKNOWN, or an empty list as appropriate.
- Return ONLY valid JSON.
- Return exactly one object for every article.

Required JSON format:

[
  {{
    "article_index": 0,
    "event_type": "maritime_disruption",
    "event_description": "Short factual description",
    "direct_energy_impact": true,
    "supply_impact": "HIGH",
    "transport_impact": "CRITICAL",
    "price_impact": "HIGH",
    "severity": "CRITICAL",
    "affected_corridors": ["Strait of Hormuz"],
    "confidence": 0.95
  }}
]

ARTICLES:
{articles_text}
"""

    response = llm.invoke(prompt)

    content = response.content

# Gemini/LangChain may return content as a list of blocks
    if isinstance(content, list):
       content = "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
        )

    content = str(content)

# Gemini can occasionally return ```json ... ```
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content)
    content = content.strip()
    content = re.sub(r"```\s*", "", content)
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try extracting the JSON array if additional text appeared
        match = re.search(r"\[.*\]", content, re.DOTALL)

        if not match:
            raise ValueError(
                "Gemini returned invalid JSON for Agent 1 event analysis."
            )

        return json.loads(match.group(0))