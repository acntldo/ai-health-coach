import httpx
from pydantic import BaseModel

from .config import USDA_API_KEY

SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
# generic foods only. branded products are noisy and often incomplete
DATA_TYPES = ["Foundation", "SR Legacy", "Survey (FNDDS)"]
ENERGY_KCAL_ID = 1008  # usda's id for energy in kcal, values are per 100 g


class UsdaError(Exception):
    """The nutrition lookup failed (no key, network, unexpected response)."""


class FoodMatch(BaseModel):
    fdc_id: int
    description: str
    data_type: str
    kcal_per_100g: float


def search_foods(query: str, limit: int = 8) -> list[FoodMatch]:
    if not USDA_API_KEY:
        raise UsdaError("USDA_API_KEY is not set")

    # dataType must be a json list, usda answers 400 to one joined string.
    # the key goes in a header so it never ends up in a logged url
    body = {"query": query, "pageSize": limit, "dataType": DATA_TYPES}
    try:
        resp = httpx.post(SEARCH_URL, headers={"X-Api-Key": USDA_API_KEY}, json=body, timeout=10)
        resp.raise_for_status()
        foods = resp.json().get("foods", [])
    except (httpx.HTTPError, ValueError) as exc:
        raise UsdaError("Nutrition lookup is unavailable right now") from exc

    matches = []
    for food in foods:
        kcal = next(
            (n.get("value") for n in food.get("foodNutrients", []) if n.get("nutrientId") == ENERGY_KCAL_ID),
            None,
        )
        # skip entries missing an id, name or kcal value, there is nothing to calculate from
        if kcal is None or not food.get("fdcId") or not food.get("description"):
            continue
        matches.append(
            FoodMatch(
                fdc_id=food["fdcId"],
                description=food["description"],
                data_type=food.get("dataType", ""),
                kcal_per_100g=kcal,
            )
        )
    return matches