"""Utilities for working with lookup tables"""


from bisect import bisect
from operator import itemgetter


def lerp_from_table(table: list[tuple[float, float]], value: float) -> float:
    """
    Linearly interpolate an output for the input `value` based on entries in the `table`
    """

    if len(table) < 2:
        raise ValueError(
            f"{table} does not have enough entries for it to be interpolatable"
        )

    # Binary search to find what this falls between
    upper_index = bisect(
        table,
        value,
        key=itemgetter(0),
    )

    if upper_index <= 0:
        lowest_value, lowest_output = table[0]

        if value == lowest_value:
            return lowest_output

        raise ValueError(
            f"{value} could not be linearly interpreted from the table "
            f"because it is less than {table[0][0]} (the smallest entry in the table)"
        )
    if upper_index >= len(table):
        highest_value, highest_output = table[-1]

        if value == highest_value:
            return highest_output

        raise ValueError(
            f"{value} could not be linearly interpreted from the table "
            f"because it is greater than {table[len(table)-1][0]} (the largest entry in the table)"
        )

    lower_index = upper_index - 1

    # Retrieve values from the table
    (upper_value, upper_output) = table[upper_index]
    (lower_value, lower_output) = table[lower_index]

    # Start of the linear interpolation algorithm
    range_ = upper_value - lower_value
    # t is a value between 0 and 1
    t = (value - lower_value) / range_
    # Linearly interpolate to find the approximate value
    output_w = upper_output * t + lower_output * (1 - t)

    return output_w
