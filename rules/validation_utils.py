import math

ANY = "ANY"


def is_invalid(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def matches_one(when: dict, row: dict) -> bool:
    col = when["column"]
    row_value = row.get(col)
    if "equals" in when:
        expected = when["equals"]
        return expected == ANY or row_value == expected
    if "not_equals" in when:
        return row_value != when["not_equals"]
    return False


def matches(when, row: dict) -> bool:
    """
    Evaluates a when condition against a row.
    when can be:
      - a single dict:  {column: X, equals: Y}
      - a list of dicts: [{column: X, equals: Y}, {column: A, not_equals: B}]
        all conditions must match (AND logic)
    """
    if isinstance(when, list):
        return all(matches_one(w, row) for w in when)
    return matches_one(when, row)
