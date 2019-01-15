import datetime
# print('IMPORTED at {}'.format(datetime.datetime.now().isoformat()))
import argparse
from pprint import pprint
import requests
from requests.auth import HTTPBasicAuth
from pymongo import MongoClient

from app.db import DB


def run_job(db, job_name):
    result = {'text': '', 'status_code': 1, 'json': None, 'exception': '',
              'lastExecutionTime': datetime.datetime.now().astimezone().isoformat()}

    try:
        if db.job_exist(job_name):
            job = db.get_job(job_name)
            kwargs = {}
            if 'basic_auth' in job:
                basic_auth = job['basic_auth']
                kwargs['auth'] = HTTPBasicAuth(basic_auth['username'], basic_auth['password'])

            resp = requests.request(method=job['method'],
                                    url=job['url'],
                                    json=job.get('body_json', None),
                                    headers=job.get('headers', None),
                                    verify=False,
                                    **kwargs)
            result['status_code'] = resp.status_code
            try:
                result['json'] = resp.json()
                result['text'] = None
            except Exception:
                result['json'] = None
                result['text'] = resp.text.ljust(1000)[:1000].strip()
        else:
            result['text'] = 'no job with name {} in db'.format(job_name)

    except Exception as e:
        result['status_code'] = 2
        result['exception'] = str(e)

    db.append_job_history(job_name=job_name, data=result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser('job_runner')
    parser.add_argument('--job_name', help='job_name', required=True)
    args, unknown_args = parser.parse_known_args()

    client = MongoClient()
    db = client.local
    db = DB(db=db)
    print('START {}'.format(datetime.datetime.now().isoformat()))
    print('job_runner --job_name: {}'.format(args.job_name))
    result = run_job(db, args.job_name)
    pprint(result)
    print('DONE {}'.format(datetime.datetime.now().isoformat()))
