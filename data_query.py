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
def find_person_row(rows, question):

    question_lower = question.lower()

    for row in rows:

        name = row.get("Tên")

        if not isinstance(name, str):
            continue

        if re.search(
            rf"\b{re.escape(name.lower().strip())}\b",
            question_lower
        ):

            return row

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
        "cao nhất" in question_lower
        or "lớn nhất" in question_lower
        or "nhiều nhất" in question_lower
    ):

        values = [
            row.get(column)
            for row in rows
            if isinstance(
                row.get(column),
                (int, float)
            )
        ]

        if not values:

            return None

        max_value = max(values)

        filtered = [
            row
            for row in rows
            if row.get(column) == max_value
        ]

        return {
            "type": "max",
            "sheet": selected_sheet,
            "column": column,
            "value": max_value,
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                column
            )
        }
    if (
        "thấp nhất" in question_lower
        or "nhỏ nhất" in question_lower
        or "ít nhất" in question_lower
    ):

        values = [
            row.get(column)
            for row in rows
            if isinstance(
                row.get(column),
                (int, float)
            )
        ]

        if not values:

            return None

        min_value = min(values)

        filtered = [
            row
            for row in rows
            if row.get(column) == min_value
        ]

        return {
            "type": "min",
            "sheet": selected_sheet,
            "column": column,
            "value": min_value,
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                column
            )
        }
    if (
        "tổng" in question_lower
        or "tất cả" in question_lower
    ):

        operator = None

        if (
            "trở lên" in question_lower
            or ">=" in question_lower
        ):

            operator = ">="

        elif (
            "trên" in question_lower
            or "hơn" in question_lower
            or ">" in question_lower
        ):

            operator = ">"

        elif (
            "trở xuống" in question_lower
            or "không quá" in question_lower
            or "<=" in question_lower
        ):

            operator = "<="

        elif (
            "dưới" in question_lower
            or "ít hơn" in question_lower
            or "<" in question_lower
        ):

            operator = "<"

        if operator is not None:

            match = re.search(
                r"(?:trên|hơn|dưới|ít hơn|trở lên|trở xuống|không quá)\s*"
                r"(\d+(?:[.,]\d+)?)\s*"
                r"(tỷ|triệu|tr|nghìn|k)?",
                question_lower
            )

            if match:

                value = parse_number(
                    match.group(0)
                )

                filtered = filter_rows(
                    rows,
                    column,
                    operator,
                    value
                )

                statistics = aggregate_rows(
                    filtered,
                    column
                )

                return {
                    "type": "sum_filtered",
                    "sheet": selected_sheet,
                    "column": column,
                    "operator": operator,
                    "value": value,
                    "rows": filtered,
                    "statistics": statistics,
                    "sum": statistics["sum"]
                }

        statistics = aggregate_rows(
            rows,
            column
        )

        return {
            "type": "sum",
            "sheet": selected_sheet,
            "column": column,
            "value": statistics["sum"],
            "statistics": statistics
        }    
    operator = None
    
    range_match = re.search(
        r"từ\s*"
        r"(\d+(?:[.,]\d+)?)\s*"
        r"(tỷ|triệu|tr|nghìn|k)?\s*"
        r"(?:đến|-)\s*"
        r"(\d+(?:[.,]\d+)?)\s*"
        r"(tỷ|triệu|tr|nghìn|k)?",
        question_lower
    )

    if range_match:

        start_unit = (
            range_match.group(2)
            or range_match.group(4)
            or ""
        )

        end_unit = (
            range_match.group(4)
            or range_match.group(2)
            or ""
        )

        start_value = parse_number(
            range_match.group(1)
            + " "
            + start_unit
        )

        end_value = parse_number(
            range_match.group(3)
            + " "
            + end_unit
        )

        filtered = []

        for row in rows:

            row_value = row.get(column)

            if (
                isinstance(row_value, (int, float))
                and start_value <= row_value <= end_value
            ):

                filtered.append(row)

        return {
            "type": "filtered_range",
            "sheet": selected_sheet,
            "column": column,
            "min_value": start_value,
            "max_value": end_value,
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                column
            )
        }
    if (
        "trở lên" in question_lower
        or "từ" in question_lower
        and "trở lên" in question_lower
        or ">=" in question_lower
    ):

        operator = ">="

    elif (
        "trên" in question_lower
        or "hơn" in question_lower
        or ">" in question_lower
    ):

        operator = ">"

    elif (
        "trở xuống" in question_lower
        or "không quá" in question_lower
        or "<=" in question_lower
    ):

        operator = "<="

    elif (
        "dưới" in question_lower
        or "ít hơn" in question_lower
        or "<" in question_lower
    ):

        operator = "<"

    if operator is not None:

        match = re.search(
            r"(?:trên|hơn|dưới|ít hơn|từ|không quá|trở lên|trở xuống)\s*"
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
            operator,
            value
        )

        return {
            "type": "filtered_aggregate",
            "sheet": selected_sheet,
            "column": column,
            "operator": operator,
            "value": value,
            "rows": filtered,
            "statistics": aggregate_rows(
                filtered,
                column
            )
        }
    person_row = find_person_row(
        rows,
        question_lower
    )

    if person_row is not None:

        asked_column = None

        for key in person_row.keys():

            key_lower = key.lower()

            if key_lower in question_lower:
                asked_column = key
                break

        if asked_column is None:

            asked_column = "Tên"

        return {
            "type": "person",
            "sheet": selected_sheet,
            "column": asked_column,
            "value": person_row.get(asked_column),
            "row": person_row
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