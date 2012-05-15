import logging

from celery.task import task

from lizard_task.handler import get_handler

@task
def test_task(username=None, db_name=None, taskname=None):
    """
    Test task
    """
    handler = get_handler(username=username, taskname=taskname)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(20)

    logger.info('I did my job')
    return 'OK'
