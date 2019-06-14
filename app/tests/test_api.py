import http.client
from flask import json
import jsonschema
from copy import deepcopy
from pprint import pprint
from app.schemas import JOB_SCHEMA
from app.schemas import JOBS_SCHEMA
from app.schemas import JOBS_INFO_SCHEMA
import httpretty

from app.tests.base_test import BaseTest
from app.tests.test_schemas import EXAMPLE_JOB


class TestAPI(BaseTest):
    def test_ping(self):
        with self.test_client as c:
            resp = c.get(
                '/api/ping',
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            self.assertEqual({'pong': True}, json.loads(resp.data), msg=resp.data)

    def test_post_job(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.CREATED, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            jsonschema.validate(received_jobs[0], schema=JOB_SCHEMA)
            self.assertDictEqual(received_jobs[0], EXAMPLE_JOB)

    def test_post_same_job_multiple_times(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB), deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.BAD_REQUEST, resp.status_code, msg=resp.data)

    def test_put_job(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.CREATED, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            jsonschema.validate(received_jobs[0], schema=JOB_SCHEMA)
            self.assertDictEqual(received_jobs[0], EXAMPLE_JOB)

            updated_job = deepcopy(EXAMPLE_JOB)
            updated_job['enabled'] = not updated_job['enabled']
            resp = c.put(
                '/api/jobs/{}'.format(received_jobs[0]['name']),
                data=json.dumps(updated_job),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            self.assertEqual(updated_job, json.loads(resp.data), msg=resp.data)

    def test_patch_job(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.CREATED, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            jsonschema.validate(received_jobs[0], schema=JOB_SCHEMA)
            self.assertDictEqual(received_jobs[0], EXAMPLE_JOB)

            updated_job = deepcopy(EXAMPLE_JOB)
            updated_job['enabled'] = not updated_job['enabled']
            resp = c.patch(
                '/api/jobs/{}'.format(received_jobs[0]['name']),
                data=json.dumps({'enabled': updated_job['enabled']}),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            self.assertEqual(updated_job, json.loads(resp.data), msg=resp.data)

    def test_put_job_non_existing(self):
        token = self.create_token()
        with self.test_client as c:
            job = deepcopy(EXAMPLE_JOB)

            resp = c.get(
                '/api/jobs/{}'.format(job['name']),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.NOT_FOUND, resp.status_code, msg=resp.data)

            resp = c.put(
                '/api/jobs/{}'.format(job['name']),
                data=json.dumps(job),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.NOT_FOUND, resp.status_code, msg=resp.data)

    def test_delete_job(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.CREATED, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            jsonschema.validate(received_jobs[0], schema=JOB_SCHEMA)
            self.assertDictEqual(received_jobs[0], EXAMPLE_JOB)

            job = deepcopy(EXAMPLE_JOB)

            resp = c.delete(
                '/api/jobs/{}'.format(job['name']),
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)

            resp = c.get(
                '/api/jobs/{}'.format(job['name']),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.NOT_FOUND, resp.status_code, msg=resp.data)

    def test_get_jobs(self):
        token = self.create_token()
        with self.test_client as c:
            resp = c.get(
                '/api/jobs',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            self.assertListEqual(received_jobs, [])

    def test_post_job_malformed_schedule_fail(self):
        token = self.create_token()
        with self.test_client as c:
            jobs = [deepcopy(EXAMPLE_JOB)]
            jobs[0]["cron_schedule"]["minute"] = 'bananas'
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(400, resp.status_code, msg=resp.data)
            result = json.loads(resp.data)
            expected_result = {'message': 'schedule bananas * * * * for job example_watch_dog is not valid. Aborting'}
            self.assertDictEqual(expected_result, result)

    def test_bad_request(self):
        token = self.create_token()
        with self.test_client as c:
            data = {'wrong_field': 'whatever'}
            resp = c.post(
                '/api/jobs',
                data=json.dumps(data),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.BAD_REQUEST, resp.status_code, msg=resp.data)
            data = json.loads(resp.data)

    def test_unauthorized(self):
        with self.test_client as c:
            resp = c.get(
                '/api/jobs',
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            self.assertEqual(http.client.UNAUTHORIZED, resp.status_code, msg=resp.data)

    def test_authorized(self):
        token = self.create_token()
        with self.test_client as c:
            resp = c.get(
                '/api/jobs',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)

    def test_invalid_token(self):
        token = self.create_token()
        with self.test_client as c:
            resp = c.get(
                '/api/jobs',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}1'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.UNAUTHORIZED, resp.status_code, msg=resp.data)

    def test_jobs_info(self):
        token = self.create_token()
        with self.test_client as c:
            resp = c.get(
                '/api/jobs/info',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            received_info = json.loads(resp.data)
            jsonschema.validate(received_info, schema=JOBS_INFO_SCHEMA)

    @httpretty.activate
    def test_run_job(self):
        mocked_response_text = 'yada yada'

        httpretty.register_uri(httpretty.GET, EXAMPLE_JOB['url'],
                               body=mocked_response_text)

        token = self.create_token()
        with self.test_client as c:
            job = deepcopy(EXAMPLE_JOB)
            jobs = [deepcopy(EXAMPLE_JOB)]
            resp = c.post(
                '/api/jobs',
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.CREATED, resp.status_code, msg=resp.data)
            received_jobs = json.loads(resp.data)
            jsonschema.validate(received_jobs, schema=JOBS_SCHEMA)
            jsonschema.validate(received_jobs[0], schema=JOB_SCHEMA)
            self.assertDictEqual(received_jobs[0], EXAMPLE_JOB)

            resp = c.get(
                '/api/jobs/info',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            received_info = json.loads(resp.data)
            jsonschema.validate(received_info, schema=JOBS_INFO_SCHEMA)

            resp = c.post(
                '/api/jobs/{}/run'.format(job['name']),
                data=json.dumps(jobs),
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            result = json.loads(resp.data)

            self.assertTrue(mocked_response_text in result['text'])
            self.assertEqual(result['status_code'], 200)

            resp = c.get(
                '/api/jobs/info',
                headers={'Content-Type': 'application/json; charset=utf-8',
                         'Authorization': 'Bearer {}'.format(token.decode('utf-8'))}
            )
            self.assertEqual(http.client.OK, resp.status_code, msg=resp.data)
            received_info = json.loads(resp.data)
            jsonschema.validate(received_info, schema=JOBS_INFO_SCHEMA)
