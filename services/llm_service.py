import os
from dotenv import load_dotenv
import time
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()

# Initialize Gemini through LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3
)

# Prompt Template
template = """
You are a Senior Energy Procurement Consultant.

An oil supply disruption has occurred.

Your task is to analyze the provided Impact Report and Supplier Data and produce a professional procurement recommendation.

IMPORTANT DATA INTEGRITY RULES:
- Use ONLY the information explicitly provided in the Impact Report and Supplier Data.
- Do NOT invent, assume, or fabricate facts, dates, prices, refinery capacities, crude grades, transportation routes, market prices, savings, logistics details, or other numerical values.
- Do NOT introduce external real-world information.
- Do NOT claim that a supplier has a specific pipeline, terminal, route, crude grade, or capability unless it is explicitly provided in the Supplier Data.
- Do NOT create financial savings or cost-avoidance figures unless they can be calculated directly from the provided numbers.
- When information required for a statement is not provided, say "Not provided in the available data."
- Supplier available-volume units are not specified in the source dataset. For the
  ranking comparison only, the system assumes barrels/day; state this limitation
  and do not present that unit as source-verified.
- Required replacement volume is a heuristic barrels/day estimate, not a measured
  or forecast supply shortfall.
- All supplier rankings, costs, delivery times, available volumes, risks, and scores must come directly from the Supplier Data.
- Preserve the meaning and units of the provided data.
- Do not convert a volume expressed as barrels/day into barrels unless the calculation period is explicitly provided.
- Distinguish clearly between facts from the input data and your procurement interpretation.

==========================
IMPACT REPORT
==========================

Risk Score:
{risk_score}

Reserve Days:
{reserve_days}

Expected Price Increase:
{price_increase} %

Required Volume:
{required_volume} barrels/day (rule-based planning estimate)

Affected Route:
{affected_route}

Affected Refineries:
{affected_refineries}

==========================
TOP RECOMMENDED SUPPLIERS
==========================

{suppliers}

==========================
REPORT REQUIREMENTS
==========================

Write a detailed professional procurement recommendation.

Include the following sections:

1. Executive Summary

Summarize:
- Current risk score
- Reserve position
- Expected price increase
- Required procurement volume
- Affected route and refineries
- The suppliers available for procurement

Do not introduce information that is not provided.

2. Risk Analysis

Analyze the operational procurement risk using only:
- Risk score
- Reserve days
- Expected price increase
- Affected route
- Affected refineries

Do not invent additional geopolitical, logistics, refinery, or market information.

3. Supplier Recommendation Matrix

Create a table comparing the provided suppliers using:
- Supplier
- Country
- Cost per barrel
- Delivery days
- Available volume
- Supplier risk
- Ranking score

Do not add unsupported supplier attributes.

4. Why Each Supplier Was Selected

Explain the strengths and trade-offs of each supplier using only the supplied:
- Cost
- Delivery time
- Available volume
- Risk score
- Ranking score

Do not invent routes, terminals, pipelines, crude grades, or other capabilities.

5. Procurement Strategy

Develop a practical procurement strategy based on:
- Required volume
- Supplier available volumes
- Supplier costs
- Delivery times
- Supplier risk
- Ranking scores
- Reserve days

If proposing a volume allocation, make sure the allocation does not exceed the supplier's available volume and clearly show the calculation.

6. Financial Considerations

Calculate only values that can be derived from the supplied data.

For example:

Procurement Cost = Allocated Volume × Cost per Barrel

If a calculation cannot be supported by the provided data, state:

"Cannot be calculated from the available data."

Do not invent market prices, savings, penalties, premiums, or other financial values.

7. Final Recommendation

Provide a concise action plan based strictly on the available data.

Clearly distinguish:
- Data-supported facts
- Procurement recommendations

Return ONLY the report.
"""

prompt = PromptTemplate(
    input_variables=[
        "risk_score",
        "reserve_days",
        "price_increase",
        "required_volume",
        "affected_route",
        "affected_refineries",
        "suppliers"
    ],
    template=template
)

chain = prompt | llm | StrOutputParser()


def generate_procurement_report(impact, suppliers):

    supplier_text = ""

    for i, supplier in enumerate(suppliers, start=1):
        supplier_text += f"""
{i}.
Supplier : {supplier["supplier"]}
Country : {supplier["country"]}
Cost/Barrel : ${supplier["cost_per_barrel"]}
Delivery : {supplier["delivery_days"]} days
Available Volume : {supplier["available_volume"]}
Risk Score : {supplier["risk"]}
Ranking Score : {supplier["score"]}

"""

    request_data = {
        "risk_score": impact["risk_score"],
        "reserve_days": impact["reserve_days"],
        "price_increase": impact["price_increase"],
        "required_volume": impact["required_volume"],
        "affected_route": impact["affected_route"],
        "affected_refineries": ", ".join(
            impact["affected_refineries"]
        ),
        "suppliers": supplier_text,
    }

    # Retry Gemini if the service temporarily returns 503
    max_attempts = 4

    for attempt in range(1, max_attempts + 1):

        try:

            print(
                f"Calling Gemini... "
                f"attempt {attempt}/{max_attempts}"
            )

            report = chain.invoke(request_data)

            print("Gemini response received successfully.")

            return report

        except Exception as e:
            error_message = str(e)

            print(f"Gemini attempt {attempt} failed:")
            print(error_message)

            # Do not retry quota-exhaustion errors.
            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "quota" in error_message.lower()
            ):
                print(
                    "Gemini quota exhausted. "
                    "Stopping retries."
                )
                raise

            # Retry only temporary service/connection failures.
            is_temporary_error = any(
                marker in error_message
                for marker in [
                    "503",
                    "UNAVAILABLE",
                    "Server disconnected",
                    "RemoteProtocolError",
                    "ConnectionError",
                    "Timeout",
                ]
            )

            if not is_temporary_error:
                raise

            if attempt == max_attempts:
                print(
                    "Gemini failed after all retry attempts."
                )
                raise

            wait_time = 2 ** attempt

            print(
                f"Gemini temporarily unavailable. "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)