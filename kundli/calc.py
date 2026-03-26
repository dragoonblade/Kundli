"""Re-export facade. All existing imports from kundli.calc continue to work."""

# Core constants and helpers
from kundli.core import (  # noqa: F401
    PLANETS, SIGNS, NAKSHATRAS, NAKSHATRA_LORDS, ASPECTS,
    EXALTATION, OWN_SIGNS, SIGN_LORDS_CALC,
    get_sign, get_nakshatra, to_julian, _get, _sign_index,
)

# Planetary positions, houses, aspects
from kundli.planets import (  # noqa: F401
    compute_planets, compute_houses, build_planet_house_map,
    compute_aspects, get_aspecting_planets,
)

# Dasha calculations
from kundli.dasha import (  # noqa: F401
    DASHA_YEARS, DASHA_ORDER, DASHA_TOTAL_YEARS,
    YOGINI_NAMES, YOGINI_YEARS, YOGINI_TOTAL,
    compute_dasha, compute_antardasha, compute_pratyantar,
    compute_yogini_dasha,
)

# Yoga detection
from kundli.yogas import YOGAS, check_yogas  # noqa: F401

# Dosha detection
from kundli.doshas import check_doshas  # noqa: F401

# Planetary strength
from kundli.strength import compute_shadbala  # noqa: F401

# Divisional charts
from kundli.varga import DIVISIONAL_CHARTS, compute_divisional_chart  # noqa: F401
