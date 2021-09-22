from datetime import datetime
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
            "interval": 3
        },
        {
            "frequency": "Day",
            "time": "06:00"
        },
        {
            "time": "15:00"
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
            "hours": [6, 12],
            "minutes": [15, 30],
            "weekDays": [
                "Monday",
                "Thursday"
            ]
        },
        {
            "hours": [6],
            "monthDays": [1, 3, 5]},
        {
            "hours": [6, 7],
            "minutes": [15],
            "monthDays": [10, 13, 15]
        }
    ]

    def test_trigger_id(self):
        ids = [
            ("Minute", 15, None, None, None, None, None),
            ("Hour", 3, None, None, None, None, None),
            ("Day", None, "06:00", None, None, None, None),
            ("Day", None, "15:00", None, None, None, None),
            (None, None, None,
             ("Sunday", "Tuesday", "Thursday"),
             None, (6,), (0,)),
            (None, None, None,
             ("Monday", "Thursday"),
             None, (6, 12), (15, 30)),
            (None, None, None, None, (1, 3, 5), (6,), (0,)),
            (None, None, None, None, (10, 13, 15), (6, 7), (15,)),
        ]
        for config, id in zip(self.configs, ids):
            self.assertTupleEqual(create_schedule_id(config), id)

    def test_trigger_name(self):
        names = [
            "Every 15 Minutes",
            "Every 3 Hours",
            "Daily - 0600",
            "Daily - 1500",
            "Each Week - Sun Tue Thur - 0600",
            "Each Week - Mon Thur - 0615 0630 1215 1230",
            "Each Month - Days 1 3 5 - 0600",
            "Each Month - Days 10 13 15 - 0615 0715"
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
                "interval": 3,
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
                "frequency": "Day",
                "interval": 1,
                "startTime": "2021-01-01T15:00:00Z",
                "timeZone": "UTC"
            },
            {
                "frequency": "Week",
                "interval": 1,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC",
                "schedule": {
                    "hours": [6],
                    "minutes": [0],
                    "weekDays": [
                        "Sunday",
                        "Tuesday",
                        "Thursday"
                    ]
                }
            },
            {
                "frequency": "Week",
                "interval": 1,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC",
                "schedule": {
                    "hours": [6, 12],
                    "minutes": [15, 30],
                    "weekDays": [
                        "Monday",
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
                    "hours": [6],
                    "minutes": [0],
                    "monthDays": [
                        1,
                        3,
                        5
                    ]
                }
            },
            {
                "frequency": "Month",
                "interval": 1,
                "startTime": "2021-01-01T00:00:00Z",
                "timeZone": "UTC",
                "schedule": {
                    "hours": [6, 7],
                    "minutes": [15],
                    "monthDays": [
                        10,
                        13,
                        15
                    ]
                }
            }
        ]
        for config, result in zip(self.configs, recurrence_objs):
            self.assertDictEqual(
                create_recurrence_object(*create_schedule_id(config)),
                result)
