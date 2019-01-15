def schedule_to_string(minute, hour, day, month, day_of_the_week):
    return " ".join([minute, hour, day, month, day_of_the_week])


def job_to_string(job, command):
    s = schedule_to_string(job['cron_schedule']['minute'],
                           job['cron_schedule']['hour'],
                           job['cron_schedule']['day'],
                           job['cron_schedule']['month'],
                           job['cron_schedule']['day_of_the_week'])
    s += " " + command
    s += " # " + job['name']
    return s
