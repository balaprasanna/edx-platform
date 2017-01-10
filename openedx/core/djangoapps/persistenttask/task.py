"""
Celery utility code for persistent tasks.
"""

from datetime import datetime
import json

from celery import Task
import pytz

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
        def truncate_to_field(model, field_name, value):
            """
            If data is too big for the field, it would cause a failure to
            insert, so we shorten it, truncating in the middle (because
            valuable information often shows up at the end.
            """
            field = model._meta.get_field(field_name)  # pylint: disable=protected-access
            if len(value) > field.max_length:
                first = value[:(field.max_length // 2)]
                last = value[(field.max_length // 2) + 3:field.max_length]
                value = u'...'.join([first, last])
            return value

        FailedTask.objects.create(
            task_name=truncate_to_field(FailedTask, 'task_name', self.name),
            task_id=task_id,  # UUID: No need to truncate
            argstring=_serialize_args(args),
            kwargstring=_serialize_kwargs(kwargs),
            exc=truncate_to_field(FailedTask, 'exc', repr(exc)),
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
