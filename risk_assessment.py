"""
Section G - Risk Assessment
MINN2020A: Computer Programming for Mining

RiskScore = Likelihood x Consequence  (both on a 1-5 scale)

    1  - 4   -> Low
    5  - 9   -> Medium
    10 - 16  -> High
    17 - 25  -> Critical
"""

MIN_SCALE = 1
MAX_SCALE = 5

LIKELIHOOD_LABELS = {
    1: "Rare",
    2: "Unlikely",
    3: "Possible",
    4: "Likely",
    5: "Almost certain",
}

CONSEQUENCE_LABELS = {
    1: "Insignificant",
    2: "Minor",
    3: "Moderate",
    4: "Major",
    5: "Catastrophic",
}


def validate_rating(value, name):
    """Return value as an int in 1-5, or raise ValueError with a clear message."""
    # bool is a subclass of int in Python, so reject it explicitly
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a whole number from {MIN_SCALE} to {MAX_SCALE}.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a whole number from {MIN_SCALE} to {MAX_SCALE}.")
    if number != int(number):
        raise ValueError(f"{name} must be a whole number from {MIN_SCALE} to {MAX_SCALE}.")
    number = int(number)
    if number < MIN_SCALE or number > MAX_SCALE:
        raise ValueError(f"{name} must be between {MIN_SCALE} and {MAX_SCALE}, got {number}.")
    return number


def calculate_risk_score(likelihood, consequence):
    """RiskScore = Likelihood x Consequence."""
    likelihood = validate_rating(likelihood, "Likelihood")
    consequence = validate_rating(consequence, "Consequence")
    return likelihood * consequence


def classify_risk(score):
    """Convert a risk score (1-25) into Low / Medium / High / Critical."""
    if score < 1 or score > 25:
        raise ValueError(f"Risk score must be between 1 and 25, got {score}.")
    if score <= 4:
        return "Low"
    if score <= 9:
        return "Medium"
    if score <= 16:
        return "High"
    return "Critical"


def risk_warning(classification):
    """Return a warning message for High/Critical risks, otherwise None."""
    if classification == "Critical":
        return ("CRITICAL RISK: Stop the activity, notify the Safety Officer and Manager "
                "immediately, and put controls in place before work continues.")
    if classification == "High":
        return ("HIGH RISK: Urgent attention required. Review existing controls and "
                "implement additional control measures.")
    return None


def assess_risk(likelihood, consequence):
    """
    Full risk assessment for one hazard/observation.
    Returns a dictionary so the GUI can display or store every part.
    """
    likelihood = validate_rating(likelihood, "Likelihood")
    consequence = validate_rating(consequence, "Consequence")
    score = likelihood * consequence
    classification = classify_risk(score)
    return {
        "likelihood": likelihood,
        "likelihood_label": LIKELIHOOD_LABELS[likelihood],
        "consequence": consequence,
        "consequence_label": CONSEQUENCE_LABELS[consequence],
        "risk_score": score,
        "classification": classification,
        "warning": risk_warning(classification),
        "is_high_or_critical": classification in ("High", "Critical"),
    }


def assess_dataframe(df, likelihood_col="Likelihood", consequence_col="Consequence"):
    """
    Add risk columns to a pandas DataFrame (for many observations at once).
    Rows with invalid ratings get 'Invalid' instead of crashing the app.
    """
    scores, classes, warnings = [], [], []
    for _, row in df.iterrows():
        try:
            result = assess_risk(row[likelihood_col], row[consequence_col])
            scores.append(result["risk_score"])
            classes.append(result["classification"])
            warnings.append(result["warning"] or "")
        except ValueError:
            scores.append(None)
            classes.append("Invalid")
            warnings.append("Invalid likelihood/consequence rating")
    out = df.copy()
    out["Risk Score"] = scores
    out["Risk Class"] = classes
    out["Risk Warning"] = warnings
    return out


def risk_matrix():
    """5x5 matrix of scores and classifications (useful for a heat-map in the GUI)."""
    return [[(l, c, l * c, classify_risk(l * c))
             for c in range(MIN_SCALE, MAX_SCALE + 1)]
            for l in range(MIN_SCALE, MAX_SCALE + 1)]


if __name__ == "__main__":
    # Simple console demo
    for l, c in [(2, 2), (3, 3), (4, 4), (5, 4), (5, 5)]:
        r = assess_risk(l, c)
        print(f"L={l} C={c} -> score {r['risk_score']:>2} -> {r['classification']}")
        if r["warning"]:
            print("   ", r["warning"])
