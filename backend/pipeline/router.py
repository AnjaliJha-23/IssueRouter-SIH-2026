CATEGORY_TO_DEPARTMENT = {
    "Infrastructure": "PWD",
    "Sanitation":     "MCD",
    "Healthcare":     "Health Dept",
    "Utilities":      "Jal Board",
    "Education":      "Education Dept",
    "Law and Order":  "Delhi Police",
    "Environment":    "CPCB",
}

# City-aware overrides — if location contains city name, use city-specific dept
CITY_OVERRIDES = {
    "mumbai": {
        "Infrastructure": "MCGM",
        "Sanitation":     "MCGM",
    },
    "bangalore": {
        "Infrastructure": "BBMP",
        "Sanitation":     "BBMP",
        "Utilities":      "BESCOM",
    },
    "noida": {
        "Utilities":      "Noida Authority",
    }
}

def route_department(category: str, location: str = "") -> str:
    """
    Maps category + location → responsible department.
    Example: ("Infrastructure", "Mumbai") → "MCGM"
    """
    location_lower = (location or "").lower()

    for city, overrides in CITY_OVERRIDES.items():
        if city in location_lower and category in overrides:
            return overrides[category]

    return CATEGORY_TO_DEPARTMENT.get(category, "Municipal Corporation")