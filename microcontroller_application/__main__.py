"""The microcontroller application all coming together"""

from asyncio import gather

from bounded_channel import bounded_channel

from .modules import (
    m01_environment,
    m02_human_detection,
    m03_activity_recognition,
    m04_person_identification,
    m05_preferences,
    m06_control,
    m08_aggregation,
)


async def main():
    "Run the whole microcontroller part of the system"

    # Start of creating interfaces

    # From the preferences module to the proxy module
    i01_1_sender, i01_1_receiver = bounded_channel(32)
    # From the proxy module to the preferences module
    i01_2_sender, i01_2_receiver = bounded_channel(32)
    # From the aggregation module to the proxy module
    i02_duty_cycle_sender, i02_duty_cycle_receiver = bounded_channel(32)
    i02_camera_frame_sender, i02_camera_frame_receiver = bounded_channel(32)
    # From the human detection module to the activity recognition module
    i03_sender, i03_receiver = bounded_channel(32)
    # From the human detection module to the person identification module
    i04_sender, i04_receiver = bounded_channel(32)
    # From the activity recognition module to the control module
    i05_sender, i05_receiver = bounded_channel(32)
    # From the person identification module to the control module
    i06_sender, i06_receiver = bounded_channel(32)
    # From the preferences module to the control module
    i07_sender, i07_receiver = bounded_channel(32)
    # From the proxy module to the person identification module
    i08_sender, i08_receiver = bounded_channel(32)
    # From the person identification module to the proxy module
    i09_sender, i09_receiver = bounded_channel(32)
    # From the person identification module to the aggregation module
    i10_sender, i10_receiver = bounded_channel(32)
    # From the control module to the aggregation module
    i11_duty_cycle_sender, i11_duty_cycle_receiver = bounded_channel(32)
    i11_power_sender, i11_power_receiver = bounded_channel(32)
    # From the environment module to the human detection module
    i13_motion_sender, i13_motion_receiver = bounded_channel(32)
    i13_occupancy_sender, i13_occupancy_receiver = bounded_channel(32)
    i13_camera_frame_sender, i13_camera_frame_receiver = bounded_channel(32)
    # From the environment module to the control module
    i14_sender, i14_receiver = bounded_channel(32)
    # From the environment module to the aggregation module
    i15_sender, i15_receiver = bounded_channel(32)
    # From the proxy module to the aggregation module
    i16_duty_cycle_sender, i16_duty_cycle_receiver = bounded_channel(32)
    (
        i16_camera_feed_interest_sender,
        i16_camera_feed_interest_receiver,
    ) = bounded_channel(32)

    # End of creating interfaces

    # Start of creating module tasks

    m01_environment_task = m01_environment.run(
        to_human_detection_motion=i13_motion_sender,
        to_human_detection_occupancy=i13_occupancy_sender,
        to_human_detection_camera_frame=i13_camera_frame_sender,
        to_control=i14_sender,
        to_aggregation=i15_sender,
    )

    m02_human_detection_task = m02_human_detection.run(
        from_environment_motion=i13_motion_receiver,
        from_environment_occupancy=i13_motion_receiver,
        from_environment_camera_frame=i13_motion_receiver,
        to_activity_recognition=i03_sender,
        to_person_identification=i04_sender,
    )

    m03_activity_recognition_task = m03_activity_recognition.run(
        from_human_detection=i03_receiver,
        to_control=i05_sender,
    )

    m04_person_identification_task = m04_person_identification.run(
        from_human_detection=i04_receiver,
        from_proxy=i08_receiver,
        to_aggregation=i10_sender,
        to_proxy=i09_sender,
        to_control=i06_sender,
    )

    m05_preferences_task = m05_preferences.run(
        from_proxy_module=i01_2_receiver,
        to_proxy_module=i01_1_sender,
        to_control_module=i07_sender,
    )

    m06_control_task = m06_control.run(
        from_activity_recognition=i05_receiver,
        from_person_identification=i06_receiver,
        from_environment=i14_receiver,
        from_preferences=i07_receiver,
        to_aggregation_duty_cycle=i11_duty_cycle_sender,
        to_aggregation_power=i11_power_sender,
    )

    m08_aggregation_task = m08_aggregation.run(
        from_person_identification=i10_receiver,
        from_control_duty_cycle=i11_duty_cycle_receiver,
        from_environment=i15_receiver,
        from_proxy_request_duty_cycle=i16_duty_cycle_receiver,
        from_proxy_camera_feed_interest=i16_camera_feed_interest_receiver,
        to_proxy_camera_frame=i02_camera_frame_sender,
        to_proxy_duty_cycle=i02_duty_cycle_sender,
    )

    # End of creating module tasks

    # Extra references to the channels need to dropped from this function
    # so that their automatic cleanup behavior behaves correctly
    # (Probably not actually important for this system's purpose)
    # Start of dropping extra references

    del i01_1_receiver, i01_1_sender
    del i01_2_receiver, i01_2_sender
    del i02_duty_cycle_sender, i02_duty_cycle_receiver
    del i02_camera_frame_sender, i02_camera_frame_receiver
    del i03_sender, i03_receiver
    del i04_sender, i04_receiver
    del i05_sender, i05_receiver
    del i06_sender, i06_receiver
    del i07_sender, i07_receiver
    del i08_sender, i08_receiver
    del i09_sender, i09_receiver
    del i10_sender, i10_receiver
    del i11_duty_cycle_sender, i11_duty_cycle_receiver
    del i11_power_sender, i11_power_receiver
    del i13_motion_sender, i13_motion_receiver
    del i13_occupancy_sender, i13_occupancy_receiver
    del i13_camera_frame_sender, i13_camera_frame_receiver
    del i14_sender, i14_receiver
    del i15_sender, i15_receiver
    del i16_duty_cycle_sender, i16_duty_cycle_receiver
    del i16_camera_feed_interest_sender, i16_camera_feed_interest_receiver

    # End of dropping extra references

    # Run all tasks in parallel.
    # If any of them encounter an unexpected exception,
    # the whole system will shut down (and automatically restart)
    # (on the real system, when properly set up, at least)
    await gather(
        m01_environment_task,
        m02_human_detection_task,
        m03_activity_recognition_task,
        m04_person_identification_task,
        m05_preferences_task,
        m06_control_task,
        m08_aggregation_task,
    )


if __name__ == "__main__":
    from asyncio import run

    run(main())
