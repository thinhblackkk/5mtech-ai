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


def find_column(rows, question):

    if not rows:
        return None

    question_lower = question.lower()

    for column in rows[0].keys():

        column_lower = column.lower()

        if (
            "phòng" in question_lower
            and "phòng" in column_lower
        ):

            return column

    for column in rows[0].keys():

        column_lower = column.lower()

        if column_lower in question_lower:

            return column

    if "doanh thu" in question_lower:

        for column in rows[0].keys():

            if "doanh thu" in column.lower():

                return column

    return None


def find_text_value(rows, column, question):

    question_lower = question.lower()

    for row in rows:

        value = row.get(column)

        if not isinstance(value, str):

            continue

        value_lower = value.lower().strip()

        if value_lower in question_lower:

            return value

    return None


def query_file(file_path, question):

    data = load_data(file_path)

    question_lower = question.lower()

    if isinstance(data, dict):

        selected_sheet = None
        rows = None
        column = None

        for sheet_name, sheet_rows in data.items():

            if not sheet_rows:

                continue

            found_column = find_column(
                sheet_rows,
                question_lower
            )

            if found_column is not None:

                selected_sheet = sheet_name
                rows = sheet_rows
                column = found_column

                break

        if rows is None:

            return None

    else:

        selected_sheet = None
        rows = data

        column = find_column(
            rows,
            question_lower
        )

        if column is None:

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

        filtered = filter_rows(
            rows,
            column,
            ">",
            value
        )

        return {
            "type": "filtered_aggregate",
            "sheet": selected_sheet,
            "column": column,
            "operator": ">",
            "value": value,
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                column
            )
        }

    text_value = find_text_value(
        rows,
        column,
        question_lower
    )

    if text_value is not None:

        filtered = filter_rows(
            rows,
            column,
            "==",
            text_value
        )

        return {
            "type": "filtered",
            "sheet": selected_sheet,
            "column": column,
            "operator": "==",
            "value": text_value,
            "rows": filtered,
            "statistics": {
                "count": len(filtered)
            }
        }

    return None