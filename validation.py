import re
import numbers

def collect_allowed_numbers(analysis_data):
    allowed_numbers = set()

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)

        elif isinstance(value, list):
            for item in value:
                walk(item)

        elif isinstance(value, numbers.Number) and not isinstance(value, bool):
            number = round(float(value), 2)

            allowed_numbers.add(number)
            allowed_numbers.add(abs(number))

    walk(analysis_data)

    return allowed_numbers


def extract_numbers_from_text(text):
    text = re.sub(r"\b\d+-inch\b", "", text, flags=re.IGNORECASE)

    matches = re.findall(r"-?\d+(?:,\d{3})*(?:\.\d+)?", text)

    numbers = []

    for match in matches:
        cleaned = match.replace(",", "")

        try:
            numbers.append(round(float(cleaned), 2))
        except ValueError:
            pass

    return numbers


def is_calendar_year(number):
    """Years are context, not financial or KPI claims."""
    return number.is_integer() and 1900 <= number <= 2100


def collect_derived_numbers(analysis_data):
    """Allow arithmetic claims that can be derived from supplied KPI values."""
    values = collect_allowed_numbers(analysis_data)
    derived = set()
    numeric = sorted({abs(value) for value in values if not is_calendar_year(value)})
    for left in numeric:
        for right in numeric:
            derived.add(round(left - right, 2))
            derived.add(round(right - left, 2))
    return derived

def mask_supplied_product_names(text, analysis_data):
    """Exclude exact supplied product labels, without allowing their numbers globally."""
    names = set()

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"product", "best_product"} and isinstance(item, str) and item:
                    names.add(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(analysis_data)
    if not names:
        return text
    pattern = r"(?<!\w)(?:" + "|".join(
        re.escape(name) for name in sorted(names, key=len, reverse=True)
    ) + r")(?!\w)"
    return re.sub(pattern, " ", text, flags=re.IGNORECASE)


def validate_numeric_claims(business_analysis, analysis_data):
    warnings = []

    analysis_text = " ".join([
        business_analysis.executive_summary,
        *business_analysis.key_insights,
        *business_analysis.risks,
        *business_analysis.recommendations
    ])

    allowed_numbers = collect_allowed_numbers(analysis_data)
    derived_numbers = collect_derived_numbers(analysis_data)
    mentioned_numbers = extract_numbers_from_text(
        mask_supplied_product_names(analysis_text, analysis_data)
    )

    for number in mentioned_numbers:
        if is_calendar_year(number):
            continue
        if number not in allowed_numbers and number not in derived_numbers:
            warnings.append(
                f"Number '{number}' was mentioned by the AI but was not found in the supplied analysis data."
            )

    return warnings

def validate_business_analysis(business_analysis, analysis_data):
    warnings = []

    analysis_text = " ".join([
        business_analysis.executive_summary,
        *business_analysis.key_insights,
        *business_analysis.risks,
        *business_analysis.recommendations
    ]).lower()

    # TIME PERIOD VALIDATION
    invalid_period_terms = [
        "year over year",
        "year-over-year",
        "yoy"
    ]

    for term in invalid_period_terms:
        if term in analysis_text:
            warnings.append(
                f"Invalid time-period reference detected: '{term}'. "
                "The supplied trend comparison is month-over-month."
            )

    # UNSUPPORTED DATA DIMENSIONS
    unsupported_dimensions = []

    for dimension in unsupported_dimensions:
        if dimension in analysis_text:
            warnings.append(
                f"Unsupported data dimension detected: '{dimension}'. "
                "This dimension is not present in the supplied dataset."
            )

    warnings.extend(
        validate_numeric_claims(
            business_analysis,
            analysis_data
        )
    )

    return warnings
