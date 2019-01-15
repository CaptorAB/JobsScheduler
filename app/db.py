import json
from bson import json_util


def convert(data):
    result = json.loads(json.dumps(data, default=json_util.default))

    if "_id" in result:
        del result["_id"]
    return result


class DB(object):
    def __init__(self, db):
        self.db = db

    def get_job(self, job_name):
        job = self.db.job_collection.find_one({"name": job_name})
        return convert(job)

    def job_exist(self, job_name):
        job = self.db.job_collection.find_one({"name": job_name})
        if job:
            return True
        else:
            return False

    def create_job(self, job):
        r = self.db.job_collection.insert_one(job)
        job = self.db.job_collection.find_one({"_id": r.inserted_id})
        return convert(job)

    def put_job(self, job):
        filter = {"name": job["name"]}
        self.db.job_collection.replace_one(filter, job)
        job = self.db.job_collection.find_one(filter)
        return convert(job)

    def get_all_jobs(self):
        jobs = list(self.db.job_collection.find())
        result = [convert(job) for job in jobs]
        return result

    def append_job_history(self, job_name, data):
        filter = {"name": job_name}
        job_history = self.db.job_history_collection.find_one(filter=filter)
        if not job_history:
            job_history = {'name': job_name,
                           'history': [data]}
        else:
            history = job_history['history']
            history.append(data)
            job_history['history'] = history
        self.db.job_history_collection.replace_one(filter, job_history, upsert=True)

    def get_job_history(self, job_name):
        job_history = self.db.job_history_collection.find_one({"name": job_name})
        if not job_history:
            return []
        else:
            return job_history['history']

    def delete_job(self, job_name):
        job = self.db.job_collection.find_one({"name": job_name})
        self.db.job_collection.delete_one({"name": job_name})
        self.db.job_history_collection.delete_one({"name": job_name})
        return convert(job)

    def delete_db(self):
        pass
