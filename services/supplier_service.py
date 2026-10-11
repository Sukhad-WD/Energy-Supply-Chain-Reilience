import json
import os

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "suppliers.json"
)


def get_all_suppliers():

    with open(DATA_PATH, "r") as file:
        suppliers = json.load(file)

    return suppliers