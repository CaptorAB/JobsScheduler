import datetime
import copy

import flask
from flask_restplus import Resource, Api
from flask import current_app
from croniter import croniter

from app.jwt_decorators import jwt_required
from app.utils import validate_input
from app.utils import validate_output
from app.schemas import JOB_SCHEMA
from app.schemas import JOBS_SCHEMA
from app.schemas import JOB_INFO_SCHEMA
from app.schemas import JOBS_INFO_SCHEMA
from app.job_runner import run_job
from app.cron_utils import schedule_to_string
from app import cron_job

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api_bp = flask.Blueprint('api', __name__, None)
api = Api(api_bp,
          title='JobsScheduler API',
          version='0.1',
          description='JobsScheduler',
          security='apikey', doc='/swagger/', authorizations=authorizations)

JOB_MODEL = api.schema_model('job', JOB_SCHEMA)
JOBS_MODEL = api.schema_model('jobs', JOBS_SCHEMA)

JOB_INFO_MODEL = api.schema_model('job_info', JOB_INFO_SCHEMA)
JOBS_INFO_MODEL = api.schema_model('jobs_info', JOBS_INFO_SCHEMA)

JOB_PATCH_SCHEMA = copy.deepcopy(JOB_SCHEMA)
JOB_PATCH_SCHEMA['required'] = []


@api.route('/ping')
class Ping(Resource):
    @api.doc(security=[])
    def get(self):
        return {'pong': True}


@api.route('/jobs')
class Jobs(Resource):

    @jwt_required
    @api.response(201, 'Created')
    @api.expect(JOBS_MODEL)
    @validate_input(JOBS_SCHEMA)
    @validate_output(JOBS_SCHEMA)
    def post(self):
        jobs = api.payload

        result = []

        names = {}

        for job in jobs:
            if job['name'] in names:
                api.abort(400, 'job {} is declared multiple times. Aborting'.format(job['name']))

            names[job['name']] = True

            schedule = job['cron_schedule']
            schedule_string = schedule_to_string(schedule['minute'],
                                                 schedule['hour'],
                                                 schedule['day'],
                                                 schedule['month'],
                                                 schedule['day_of_the_week'])
            if not croniter.is_valid(schedule_string):
                api.abort(400, 'schedule {} for job {} is not valid. Aborting'.format(schedule_string, job['name']))

            if current_app.db.job_exist(job['name']):
                api.abort(400, 'job with name {} already exist. Aborting'.format(job['name']))

        for job in jobs:
            new_job = current_app.db.create_job(job)
            if not current_app.testing:
                if job['enabled']:
                    cron_job.add_job(job)

            result.append(new_job)
        return result, 201

    @jwt_required
    @validate_output(JOBS_SCHEMA)
    def get(self):
        jobs = current_app.db.get_all_jobs()
        for job in jobs:
            if 'basic_auth' in job:
                job['basic_auth']['password'] = 'CENSORED'

        return jobs, 200

    @jwt_required
    @validate_output(JOBS_SCHEMA)
    def delete(self):
        jobs = current_app.db.get_all_jobs()
        for job in jobs:
            current_app.db.delete_job(job['name'])

        if not current_app.testing:
            cron_job.delete_all_jobs()

        for job in jobs:
            if 'basic_auth' in job:
                job['basic_auth']['password'] = 'CENSORED'

        return jobs, 200


@api.route('/jobs/<string:name>')
class Job(Resource):

    @jwt_required
    @validate_output(JOB_SCHEMA)
    def get(self, name):
        if not current_app.db.job_exist(name):
            api.abort(404, "job {} doesn't exist".format(name))

        job = current_app.db.get_job(name)
        if 'basic_auth' in job:
            job['basic_auth']['password'] = 'CENSORED'

        return job, 200

    @jwt_required
    @api.expect(JOB_MODEL)
    @validate_input(JOB_SCHEMA)
    @validate_output(JOB_SCHEMA)
    def put(self, name):
        if not current_app.db.job_exist(name):
            api.abort(404, "job {} doesn't exist".format(name))

        job = current_app.db.put_job(api.payload)
        if not current_app.testing:
            if cron_job.exist(job['name']):
                cron_job.remove_job(job['name'])
            if job['enabled']:
                cron_job.add_job(job)

        return job, 200

    @jwt_required
    @validate_output(JOB_SCHEMA)
    def delete(self, name):
        if not current_app.db.job_exist(name):
            api.abort(404, "job {} doesn't exist".format(name))

        job = current_app.db.get_job(name)
        current_app.db.delete_job(name)

        if not current_app.testing:
            cron_job.remove_job(job['name'])

        if 'basic_auth' in job:
            job['basic_auth']['password'] = 'CENSORED'

        return job, 200

    @jwt_required
    @api.expect(JOB_MODEL)
    @validate_input(JOB_PATCH_SCHEMA)
    @validate_output(JOB_SCHEMA)
    def patch(self, name):
        """Updates a job with one or more keys of a job. Does NOT follow http://jsonpatch.com specification of PATCH """
        if not current_app.db.job_exist(name):
            api.abort(404, "job {} doesn't exist".format(name))

        job = current_app.db.get_job(name)
        job.update(api.payload)
        job = current_app.db.put_job(job)

        if not current_app.testing:
            if cron_job.exist(job['name']):
                cron_job.remove_job(job['name'])
            if job['enabled']:
                cron_job.add_job(job)

        return job, 200


@api.route('/jobs/<string:name>/run')
class RunJob(Resource):

    @jwt_required
    @api.response(200, 'Ok')
    def post(self, name):
        if not current_app.db.job_exist(name):
            api.abort(404, "job {} doesn't exist".format(name))

        result = run_job(current_app.db, job_name=name)

        return result, 200


@api.route('/jobs/info')
class RunJob(Resource):

    @jwt_required
    @api.response(200, 'Ok')
    @validate_output(JOBS_INFO_SCHEMA)
    def get(self):
        jobs = current_app.db.get_all_jobs()

        result = []
        for job in jobs:
            history = current_app.db.get_job_history(job_name=job['name'])
            successes = [run for run in history if 'status_code' in run and (run['status_code'] // 100 == 2)]

            schedule = schedule_to_string(job['cron_schedule']['minute'],
                                          job['cron_schedule']['hour'],
                                          job['cron_schedule']['day'],
                                          job['cron_schedule']['month'],
                                          job['cron_schedule']['day_of_the_week'])

            if job['enabled']:
                state = 'enabled'
                now = datetime.datetime.now()
                iterator = croniter(schedule, now)
                next_execution_time = iterator.get_next(
                    datetime.datetime).astimezone().isoformat()
            else:
                state = 'disabled'
                next_execution_time = None

            if len(history) == 0:
                last_execution_time = None
                lastJsonResponse = None
                lastTextResponse = None
                lastStatusCode = None
            else:
                last_execution_time = history[-1]['lastExecutionTime']
                lastJsonResponse = history[-1]['json']
                if not history[-1]['json']:
                    lastTextResponse = history[-1]['text']
                else:
                    lastTextResponse = None
                lastStatusCode = history[-1]['status_code']

            item = {
                "name": job['name'],
                "properties": {
                    "state": state,
                    "status": {
                        "executionCount": len(history),
                        "failureCount": len(history) - len(successes),
                        "faultedCount": len(history) - len(successes),
                        "lastExecutionTime": last_execution_time,
                        "nextExecutionTime": next_execution_time,
                        "lastJsonResponse": lastJsonResponse,
                        "lastTextResponse": lastTextResponse,
                        "lastStatusCode": lastStatusCode
                    }
                }
            }

            result.append(item)

        return result, 200
