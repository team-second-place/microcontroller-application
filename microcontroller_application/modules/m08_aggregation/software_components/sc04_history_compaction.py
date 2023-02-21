"""
Module: 08. Aggregation
Component: 04. History compaction
"""

import csv
from datetime import datetime
from enum import Enum
from pathlib import Path

import bounded_channel
from option_and_result import NONE, Option, Some

from microcontroller_application.interfaces.message_types import (
    FromControlToAggregationDutyCycle,
)


async def run(
    *,
    from_control: bounded_channel.Receiver[FromControlToAggregationDutyCycle],
    history_folder: Path,
):
    last_bucket: Option[LightBucket] = NONE()
    async for message in from_control:
        this_bucket = bucket(message.duty_cycle)

        if this_bucket != last_bucket:
            now = datetime.now()
            year = now.year
            month = now.month
            day = now.day
            # Deeply nested folders
            # HISTORY_FOLDER is a constant along the lines of “/home/pi/system_history”
            today_s_history_file_path = (
                history_folder / str(year) / str(month) / str(day) / "brightness.csv"
            )
            # Open the file in append mode
            with open(today_s_history_file_path, "a", encoding="utf8") as history_file:

                writer = csv.writer(history_file)

                writer.writerow(
                    [
                        # The hour, minute, second, this occurred in a standard format (string)
                        now.time().isoformat(),
                        # The numerical code of the bucket this falls into (defined above)
                        this_bucket.value,
                    ],
                )
            # Reference: https://stackoverflow.com/a/37654233

        last_bucket = Some(this_bucket)


class LightBucket(Enum):
    """
    What “bucket” (large ranges of brightness, like in a histogram) the amount of light
    being emitted falls into. This is a reduced resolution of its actual value.

    This is represented as a percentage of the maximum brightness the system can emit.
    """

    # enum variants just need to be assigned a distinct value
    P_0 = 0
    P_0_TO_25 = 1
    P_25_TO_50 = 2
    P_50_TO_75 = 3
    P_75_TO_100 = 4
    P_100 = 5


def bucket(duty_cycle: float) -> LightBucket:
    if duty_cycle == 1:
        return LightBucket.P_100
    if duty_cycle >= 0.75:
        return LightBucket.P_75_TO_100
    if duty_cycle >= 0.50:
        return LightBucket.P_50_TO_75
    if duty_cycle >= 0.25:
        return LightBucket.P_25_TO_50
    if duty_cycle > 0:
        return LightBucket.P_0_TO_25
    if duty_cycle == 0:
        return LightBucket.P_0

    raise ValueError(f"{duty_cycle} is not in the range 0 to 1 (inclusive)")
