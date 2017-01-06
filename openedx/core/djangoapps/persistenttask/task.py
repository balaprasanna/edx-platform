"""
Celery utility code for persistent tasks.
"""

from datetime import datetime
import json

from celery import Task
import pytz
import six

from .models import FailedTask


# pylint: disable=abstract-method
class PersistOnFailureTask(Task):
    """
    Custom Celery Task base class that persists task data on failure.
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        If the task fails, persist a record of the task.
        """
        FailedTask.objects.create(
            task_name=self.name,
            task_id=task_id,
            argstring=_serialize_args(args),
            kwargstring=_serialize_kwargs(kwargs),
            exc=repr(exc),
            einfo=six.text_type(einfo),
            datetime_failed=pytz.utc.localize(datetime.utcnow()),
        )
        super(PersistOnFailureTask, self).on_failure(exc, task_id, args, kwargs, einfo)


def _serialize_args(args):
    """
    Combine arglist into a json string.
    """
    if not isinstance(args, (tuple, list)):
        raise TypeError(u'Args must be a tuple or list')
    return json.dumps(args)


def _serialize_kwargs(kwargs):
    """
    Combine kwarg dict into a json string
    """
    if not isinstance(kwargs, dict):
        raise TypeError(u'Kwargs must be a dict')
    return json.dumps(kwargs)
