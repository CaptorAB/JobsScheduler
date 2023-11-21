import jsonschema
import unittest
from copy import deepcopy
from app.schemas import JOB_SCHEMA
from app.schemas import JOBS_SCHEMA
from app.schemas import JOB_INFO_SCHEMA
from app.schemas import JOBS_INFO_SCHEMA

EXAMPLE_JOB = {
    "name": "example_watch_dog",
    "description": "description example job",
    "enabled": True,
    "cron_schedule": {
        "minute": '1',
        "hour": "*",
        "day": "*",
        "month": "*",
        "day_of_the_week": "*"
    },
    "url": 'https://example.com',
    "method": "GET",
    "type": "JOB",
    "headers": {
        "Content-Type": "application/json"
    }
}

EXAMPLE_JOB_INFO = {
    "name": "example_watch_dog_history",
    "properties": {
        "state": "enabled",
        "status": {
            "executionCount": 0,
            "failureCount": 0,
            "faultedCount": 0,
            "lastExecutionTime": "2018-09-14T16:50:01Z",
            "nextExecutionTime": "2018-09-14T16:50:01Z",
            "lastStatusCode": 200
        }
    }
}


class TestSchemas(unittest.TestCase):
    def test_job_schema(self):
        job = deepcopy(EXAMPLE_JOB)
        jsonschema.validate(job, schema=JOB_SCHEMA)

        with self.assertRaises(jsonschema.exceptions.ValidationError):
            job['wrong_field'] = 'Duck'
            jsonschema.validate(job, schema=JOB_SCHEMA)

        job = deepcopy(EXAMPLE_JOB)
        jobs = [job, job]
        jsonschema.validate(jobs, schema=JOBS_SCHEMA)

    def test_job_info_schema(self):
        history = deepcopy(EXAMPLE_JOB_INFO)
        jsonschema.validate(history, schema=JOB_INFO_SCHEMA)

        jsonschema.validate([history], schema=JOBS_INFO_SCHEMA)
