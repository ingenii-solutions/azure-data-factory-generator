# Ingenii Azure Data Factory Generator Triggers

As well as defining the pipeline itself, we need to define when it runs. At the moment only the 'Schedule' type of trigger has been implemented [out of the types available.](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipeline-execution-triggers)

All times are UTC. The option to change timezone has not yet been implemented.

## Recurrence

The most simple schedule is recurringly calling the pipeline after a fixed interval. The different approaches are:

```
    # Runs every 15 minutes
    "schedule": {
        "frequency": "Minute",
        "interval": "15"
    }

    # Runs every 3 hours
    "schedule": {
        "frequency": "Hour",
        "interval": "3"
    }

    # Runs every day at 6:00 AM
    "schedule": {
        "frequency": "Day",
        "time": "06:00"
    }

    # Daily frequency is assumed, so runs every day at 3:00 PM
    "schedule": {
        "time": "15:00"
    }

    # Daily frequency is assumed, so runs every day at 6:00 AM and 5:00 PM
    "schedule": {
        "hours": [6, 17]
    }
```

## Days of the week

Another approach is to set the days of the week the pipeline will run, and at which time. Times follow a cron-like approach where hours and minutes are set separately, and all combinations are run.

```
    # Runs every Tuesday, Thursday, and Sunday at 6:00 AM
    "schedule": {
        "hours": [6],
        "weekDays": [
            "Tuesday",
            "Thursday",
            "Sunday"
        ]
    }

    # Runs every Monday and Thursday, at 6:15, 6:30, 12:15, 12:30
    "schedule": {
        "hours": [6, 12],
        "minutes": [15, 30],
        "weekDays": [
            "Monday",
            "Thursday"
        ]
    }
```

## Days of the month

This approach runs the pipeline on certain days e.g. the third of the month. Similarly to the days fo the week, thhe hours and minutes are specified separately and follow a crom-like approach of combining all the permutations.

```
    # Runs on the 1st, 3rd, and 5th of each month at 6:00 AM
    "schedule": {
        "hours": [6],
        "monthDays": [1, 3, 5]
    }

    # Runs on the 10th, 13th, and 15th of each month at 6:15 AM and 7:15 AM
    "schedule": {
        "hours": [6, 7],
        "minutes": [15],
        "monthDays": [10, 13, 15]
    }
```

## Position in the month

This is the final option, where we can combine days of the week and month, for example 'The third Monday of each month'. This has not yet been implemented.
