"""North and South Indian chart rendering in terminal."""
from kundli.calc import SIGNS
from kundli.names import PLANET_ABBR

_ABBR = PLANET_ABBR["hindu"]


def _sign_planets(planets, sign):
    return " ".join(_ABBR.get(p["planet"], p["planet"][:2]) for p in planets if p["sign"] == sign)


def draw_north_indian(planets, houses):
    asc_sign = houses[0]["sign"]
    asc_idx = SIGNS.index(asc_sign)
    sign_planets = {}
    for i in range(12):
        sign = SIGNS[(asc_idx + i) % 12]
        sign_planets[i + 1] = (sign, _sign_planets(planets, sign))

    def cell(house, width=18):
        sign, pls = sign_planets[house]
        content = f"{sign[:3]} {pls}" if pls else sign[:3]
        return content.center(width)

    w = 18
    lines = [
        "┌" + "─" * w + "┬" + "─" * w + "┬" + "─" * w + "┐",
        "│" + cell(12) + "│" + cell(1) + "│" + cell(2) + "│",
        "├" + "─" * w + "┼" + "─" * w + "┼" + "─" * w + "┤",
        "│" + cell(11) + "│" + "  LAGNA".center(w) + "│" + cell(3) + "│",
        "├" + "─" * w + "┼" + "─" * w + "┼" + "─" * w + "┤",
        "│" + cell(10) + "│" + cell(7) + "│" + cell(4) + "│",
        "├" + "─" * w + "┼" + "─" * w + "┼" + "─" * w + "┤",
        "│" + cell(9) + "│" + cell(8) + "│" + cell(5) + "│",
        "├" + "─" * w + "┴" + "─" * w + "┴" + "─" * w + "┤",
        "│" + cell(6, w * 3 + 2) + "│",
        "└" + "─" * (w * 3 + 2) + "┘",
    ]
    return "\n".join(lines)


def draw_south_indian(planets):
    grid = [
        [11, 0, 1, 2],
        [10, -1, -1, 3],
        [9, -1, -1, 4],
        [8, 7, 6, 5],
    ]
    w = 16

    def cell(sign_idx):
        if sign_idx == -1:
            return "".center(w)
        sign = SIGNS[sign_idx]
        pls = _sign_planets(planets, sign)
        content = f"{sign[:3]} {pls}" if pls else sign[:3]
        return content.center(w)

    lines = ["┌" + ("─" * w + "┬") * 3 + "─" * w + "┐"]
    for r, row in enumerate(grid):
        lines.append("│" + "│".join(cell(s) for s in row) + "│")
        if r < 3:
            lines.append("├" + ("─" * w + "┼") * 3 + "─" * w + "┤")
    lines.append("└" + ("─" * w + "┴") * 3 + "─" * w + "┘")
    return "\n".join(lines)
