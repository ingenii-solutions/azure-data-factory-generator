from datetime import datetime, timedelta
from unittest import TestCase

from azure_data_factory_generator.schedule import create_schedule_id, \
    create_recurrence_object, trigger_name


class ScheduleGeneratorTestCase(TestCase):

    base_date = datetime(1900, 1, 1)
    curr_year = str(datetime.utcnow().year)

    configs = [
        {
            "frequency": "Minute",
            "interval": 15
        },
        {
            "frequency": "Hour",
            "interval": 15
        },
        {
            "frequency": "Day",
            "time": "06:00"
        },
        {
            "hours": [6],
            "weekDays": [
                "Tuesday",
                "Thursday",
                "Sunday"
            ]
        },
        {
            "hours": [6],
            "monthDays": [1, 3, 5]
        }
    ]

    def test_trigger_id(self):
        ids = [
            ("Minute", 15, None, None, None, None, None),
            ("Hour", 15, None, None, None, None, None),
            ("Day", None, "06:00", None, None, None, None),
            (None, None, None, ["Sunday", "Tuesday", "Thursday"], None, (6,), (0,)),
            (None, None, None, None, [1, 3, 5], (6,), (0,)),
        ]
        for config, id in zip(self.configs, ids):
            self.assertTupleEqual(create_schedule_id(config), id)
    
    def test_trigger_name(self):
        names = [
            "Every 15 Minutes",
            "Every 15 Hours",
            "Daily - 0600",
            "Each Week - Sun Tue Thur - 0600",
            "Each Month - Days 1 3 5 - 0600"
        ]
        for config, result in zip(self.configs, names):
            self.assertEqual(
                trigger_name(*create_schedule_id(config)),
                result)

    def test_recurrence_object(self):
        recurrence_objs = [
            {
                "frequency": "Minute",
                "interval": 15,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC"
            },
            {
                "frequency": "Hour",
                "interval": 15,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC"
            },
            {
                "frequency": "Day",
                "interval": 1,
                "startTime": "2021-01-01T06:00:00Z",
                "timeZone": "UTC"
            },
            {
                "frequency": "Week",
                "interval": 1,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC",
                "schedule": {
                    "minutes": [
                        0
                    ],
                    "hours": [
                        6
                    ],
                    "weekDays": [
                        "Sunday",
                        "Tuesday",
                        "Thursday"
                    ]
                }
            },
            {
                "frequency": "Month",
                "interval": 1,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC",
                "schedule": {
                    "minutes": [
                        0
                    ],
                    "hours": [
                        6
                    ],
                    "monthDays": [
                        1,
                        3,
                        5
                    ]
                }
            }
        ]
        for config, result in zip(self.configs, recurrence_objs):
            self.assertDictEqual(
                create_recurrence_object(*create_schedule_id(config)), 
                result)

