import json
import math
from pathlib import Path

from Agent1.event_analyzer import get_severity


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

AGENT1_OUTPUT = (
    BASE_DIR
    / "Agent1"
    / "agent1_output.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "Agent2"
    / "scenario_model_output.json"
)


# =========================================================
# LOAD AGENT 1 OUTPUT
# =========================================================

def load_agent1_output():

    if not AGENT1_OUTPUT.exists():
        raise FileNotFoundError(
            f"Agent 1 output not found: {AGENT1_OUTPUT}"
        )

    with open(
        AGENT1_OUTPUT,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# =========================================================
# SCENARIO MODEL
# =========================================================

def calculate_scenario(agent1_data):

    risk_score = agent1_data["overall_risk"]["score"]
    if (
        isinstance(risk_score, bool)
        or not isinstance(risk_score, (int, float))
        or not math.isfinite(risk_score)
        or not 0 <= risk_score <= 100
    ):
        raise ValueError("Agent 1 risk score must be a finite number from 0 to 100.")

    risk_score = round(risk_score)
    risk_level = get_severity(risk_score)

    compound_risk = agent1_data["compound_risk"]

    corridors = agent1_data["corridors"]
    if (
        not isinstance(compound_risk, dict)
        or not isinstance(compound_risk.get("detected"), bool)
    ):
        raise ValueError("Agent 1 compound_risk must include a detected flag.")
    if not isinstance(corridors, dict):
        raise ValueError("Agent 1 corridors must be an object.")
    for corridor_name, corridor_data in corridors.items():
        if (
            not isinstance(corridor_name, str)
            or not isinstance(corridor_data, dict)
        ):
            raise ValueError("Each Agent 1 corridor must have a name and risk data.")
        corridor_score = corridor_data.get("risk_score")
        if (
            isinstance(corridor_score, bool)
            or not isinstance(corridor_score, (int, float))
            or not math.isfinite(corridor_score)
            or not 0 <= corridor_score <= 100
        ):
            raise ValueError(
                f"Corridor risk score for {corridor_name!r} "
                "must be a finite number from 0 to 100."
            )


    # -----------------------------------------------------
    # BASELINE DAILY OIL REQUIREMENT
    # -----------------------------------------------------

    baseline_daily_requirement = 5_000_000  # barrels/day


    # -----------------------------------------------------
    # SUPPLY GAP
    # -----------------------------------------------------

    if risk_score >= 80:
        supply_gap_percent = 25

    elif risk_score >= 65:
        supply_gap_percent = 15

    elif risk_score >= 50:
        supply_gap_percent = 10

    elif risk_score >= 30:
        supply_gap_percent = 5

    else:
        supply_gap_percent = 2


    # Compound disruption increases supply pressure

    if compound_risk["detected"]:
        supply_gap_percent += 5


    # -----------------------------------------------------
    # REQUIRED REPLACEMENT VOLUME
    # -----------------------------------------------------

    required_volume = round(
        baseline_daily_requirement
        * supply_gap_percent
        / 100
    )


    # -----------------------------------------------------
    # PRICE IMPACT
    # -----------------------------------------------------

    if risk_score >= 80:
        price_increase_percent = 18

    elif risk_score >= 65:
        price_increase_percent = 12

    elif risk_score >= 50:
        price_increase_percent = 8

    elif risk_score >= 30:
        price_increase_percent = 5

    else:
        price_increase_percent = 2


    # -----------------------------------------------------
    # REFINERY STRESS
    # -----------------------------------------------------

    refinery_stress = min(
        round(risk_score * 0.9),
        95
    )


    # -----------------------------------------------------
    # STRATEGIC RESERVE
    # -----------------------------------------------------

    if risk_score >= 80:
        reserve_days = 12

    elif risk_score >= 65:
        reserve_days = 20

    elif risk_score >= 50:
        reserve_days = 30

    elif risk_score >= 30:
        reserve_days = 45

    else:
        reserve_days = 60


    # -----------------------------------------------------
    # DISRUPTION SEVERITY
    # -----------------------------------------------------

    disruption_severity = risk_level


    # -----------------------------------------------------
    # AFFECTED CORRIDORS
    # -----------------------------------------------------

    affected_corridors = []

    for corridor_name, corridor_data in corridors.items():

        if corridor_data["risk_score"] >= 50:

            affected_corridors.append(
                corridor_name
            )


    # -----------------------------------------------------
    # PRIMARY AFFECTED ROUTE
    # -----------------------------------------------------

    if corridors:

        affected_route = max(
            corridors.items(),
            key=lambda item: (
                item[1]["risk_score"],
                item[0],
            )
        )[0]

    else:

        affected_route = "Unknown"


    # -----------------------------------------------------
    # AFFECTED REFINERIES
    # -----------------------------------------------------

    ROUTE_REFINERIES = {

        "Middle East": [
            "Jamnagar Refinery",
            "Vadinar Refinery"
        ],

        "Middle East Oil Supply": [
            "Jamnagar Refinery",
            "Vadinar Refinery"
        ],

        "Strait of Hormuz": [
            "Jamnagar Refinery",
            "Vadinar Refinery"
        ],

        "Gulf of Oman": [
            "Jamnagar Refinery",
            "Vadinar Refinery"
        ],

        "Red Sea": [
            "Jamnagar Refinery",
            "Kochi Refinery"
        ],

        "Black Sea": [
            "Vadinar Refinery"
        ],

        "Bab el-Mandeb": [
            "Jamnagar Refinery"
        ]
    }


    affected_refineries = ROUTE_REFINERIES.get(
        affected_route,
        []
    )


    # -----------------------------------------------------
    # SCENARIO RESULT
    # -----------------------------------------------------

    scenario = {

        "risk_score": risk_score,

        "risk_level": risk_level,

        "disruption_severity":
            disruption_severity,

        "supply_gap_percent":
            supply_gap_percent,

        "required_volume":
            required_volume,

        "price_increase_percent":
            price_increase_percent,

        "refinery_stress_percent":
            refinery_stress,

        "reserve_days":
            reserve_days,

        "affected_corridors":
            affected_corridors,

        "affected_route":
            affected_route,

        "affected_refineries":
            affected_refineries,

        "compound_risk":
            compound_risk["detected"],

        "estimates_are_heuristic": True,

        "model_assumptions": {
            "baseline_daily_oil_requirement_barrels": baseline_daily_requirement,
            "required_volume_unit": "barrels/day",
            "impact_estimates": (
                "Rule-based planning estimates; not calibrated forecasts."
            ),
        }

    }

    return scenario


# =========================================================
# SAVE OUTPUT
# =========================================================

def save_output(data):

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


# =========================================================
# PIPELINE FUNCTION
# =========================================================

def run_agent2():

    agent1_data = load_agent1_output()

    scenario = calculate_scenario(
        agent1_data
    )

    output = {
        "agent": "Agent 2",
        "scenario": scenario
    }

    save_output(output)

    return output


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 50)
    print("   ENERGY SUPPLY CHAIN - AGENT 2")
    print("   Disruption Scenario Modeller")
    print("=" * 50)

    print("\nLoading Agent 1 output...")

    agent1_data = load_agent1_output()

    print("Agent 1 output loaded successfully.")

    print("\nRunning disruption scenario model...")

    scenario = calculate_scenario(
        agent1_data
    )

    print("\n========================================")
    print("          SCENARIO RESULT")
    print("========================================")

    print(
        f"\nRisk Score: "
        f"{scenario['risk_score']}/100"
    )

    print(
        f"Disruption Severity: "
        f"{scenario['disruption_severity']}"
    )

    print(
        f"Estimated Supply Gap: "
        f"{scenario['supply_gap_percent']}%"
    )

    print(
        f"Required Replacement Volume: "
        f"{scenario['required_volume']:,} barrels/day"
    )

    print(
        f"Estimated Price Increase: "
        f"{scenario['price_increase_percent']}%"
    )

    print(
        f"Refinery Stress: "
        f"{scenario['refinery_stress_percent']}%"
    )

    print(
        f"Strategic Reserve: "
        f"{scenario['reserve_days']} days"
    )

    print("\nAffected Corridors:")

    for corridor in scenario[
        "affected_corridors"
    ]:

        print(
            f"  - {corridor}"
        )

    print(
        f"\nPrimary Affected Route: "
        f"{scenario['affected_route']}"
    )

    print("\nAffected Refineries:")

    for refinery in scenario[
        "affected_refineries"
    ]:

        print(
            f"  - {refinery}"
        )

    print(
        f"\nCompound Risk: "
        f"{scenario['compound_risk']}"
    )

    output = {

        "agent": "Agent 2",

        "scenario": scenario

    }

    save_output(output)

    print(
        "\nOutput saved to: "
        "scenario_model_output.json"
    )


if __name__ == "__main__":
    main()