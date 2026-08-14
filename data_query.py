import re

from data_analyzer import (
    load_data,
    filter_rows,
    aggregate_rows
)


def parse_number(text):

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(tỷ|triệu|tr|nghìn|k)?",
        text.lower()
    )

    if not match:
        return None

    number_text = match.group(1)
    unit = match.group(2)

    if "," in number_text and "." not in number_text:

        number = float(
            number_text.replace(",", ".")
        )

    else:

        number = float(
            number_text.replace(",", "")
        )

    if unit == "tỷ":

        number *= 1_000_000_000

    elif unit in ["triệu", "tr"]:

        number *= 1_000_000

    elif unit in ["nghìn", "k"]:

        number *= 1_000

    return number


def query_file(file_path, question):

    data = load_data(file_path)

    question_lower = question.lower()

    if "doanh thu" not in question_lower:

        return None

    if (
        "trên" in question_lower
        or "hơn" in question_lower
    ):

        match = re.search(
            r"(?:trên|hơn)\s*"
            r"(\d+(?:[.,]\d+)?)\s*"
            r"(tỷ|triệu|tr|nghìn|k)?",
            question_lower
        )

        if not match:

            return None

        value = parse_number(
            match.group(0)
        )

        if value is None:

            return None

        sheet = (
            data["Doanh thu"]
            if isinstance(data, dict)
            and "Doanh thu" in data
            else data
        )

        filtered = filter_rows(
            sheet,
            "Doanh thu",
            ">",
            value
        )

        return {
            "type": "filtered_aggregate",
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                "Doanh thu"
            )
        }

    return None
