from celery import shared_task
from .utils import write_login_log


@shared_task
def write_login_log_async(*args, **kwargs):
    '''异步写入日志'''
    write_login_log(*args, **kwargs)

