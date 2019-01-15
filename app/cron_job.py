import os
from crontab import CronTab, CronItem
import getpass
from app.cron_utils import job_to_string
import logging
from pprint import pprint

USERNAME = getpass.getuser()


def add_job(job):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    command = '. /etc/profile; cd {}; export PYTHONPATH=$PYTHONPATH:{}; python3 app/job_runner.py --job_name "{}" >> /tmp/schedule_jobs.log 2>&1'.format(
        root_path,
        root_path,
        job['name'])
    job_string = job_to_string(job=job, command=command)
    cron = CronTab(user=USERNAME)
    item = CronItem.from_line(job_string, cron=cron)
    cron.append(item)
    cron.write()


def exist(job_name):
    cron = CronTab(user=USERNAME)
    job_iter = cron.find_comment(job_name)
    jobs = []
    for job in job_iter:
        jobs.append(job)
    if len(jobs) == 0:
        return False
    elif len(jobs) > 1:
        logging.error('More then 1 job found matching {}'.format(job_name))
        raise Exception('More then 1 job found matching {}'.format(job_name))
    else:
        return True


def remove_job(job_name):
    cron = CronTab(user=USERNAME)
    job_iter = cron.find_comment(job_name)
    jobs = []
    for job in job_iter:
        jobs.append(job)

    job_iter = cron.find_comment(job_name)
    for job in job_iter:
        cron.remove(job)
    cron.write()

    if len(jobs) > 1:
        logging.error('More then 1 job found matching {}'.format(job_name))
        raise Exception('More then 1 job found matching {}'.format(job_name))


def delete_all_jobs():
    cron = CronTab(user=USERNAME)
    cron.remove_all()
    cron.write()
