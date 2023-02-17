from asyncio import create_task

from bounded_channel import bounded_channel

import pytest

from microcontroller_application.interfaces.message_types import (
    FromActivityRecognitionToControl,
    FromPersonIdentificationToControl,
    FromEnvironmentToControl,
    FromPreferencesToControl,
    FromControlToAggregation,
)
from microcontroller_application.modules import m06_control


@pytest.mark.asyncio
async def test_integration_1():
    i05_sender, i05_receiver = bounded_channel(32)
    i06_sender, i06_receiver = bounded_channel(32)
    i07_sender, i07_receiver = bounded_channel(32)
    i11_sender, i11_receiver = bounded_channel(32)
    i13_sender, i13_receiver = bounded_channel(32)

    m06_control_task = m06_control.run(
        from_activity_recognition=i05_receiver,
        from_person_identification=i06_receiver,
        from_environment=i13_receiver,
        from_preferences=i07_receiver,
        to_aggregation=i11_sender,
    )

    create_task(m06_control_task)

    # Start funneling in example data

    # Unwrap means to fail the test if an error is returned
    (
        await i05_sender.send(FromActivityRecognitionToControl(activities_of_humans=[]))
    ).unwrap()

    (
        await i06_sender.send(
            FromPersonIdentificationToControl(
                identified_people=[],
            )
        )
    ).unwrap()

    # (
    #     await
    # )
