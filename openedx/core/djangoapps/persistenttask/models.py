"""
Models to support persistent tasks.
"""

import json

from django.db import models


class JSONProperty(property):
    """
    Reusable property to facade a json string with the deserialized
    python value it represents.
    """
    def __init__(self, attrib, allowed_types=frozenset({list, tuple, dict})):
        self.attrib = attrib
        self.allowed_types = allowed_types
        super(JSONProperty, self).__init__(fget=self.fget, fset=self.fset, fdel=self.fdel, doc=self.__doc__)

    def fget(self, obj):
        """
        Get a python value from the JSON-serialized representation.
        """
        return json.loads(getattr(obj, self.attrib))

    def fset(self, obj, value):
        """
        Create a JSON-serialized representation of the passed value.

        Raises a TypeError if the value cannot be JSON-serialized or is not
        of the allowed types.
        """
        if value not in self.allowed_types:
            sorted_types = sorted(str(allowed) for allowed in self.allowed_types)
            allowed_type_names = ' or '.join(sorted_types)
            raise TypeError(u'Value must be a JSON-serializable {}'.format(allowed_type_names))
        setattr(obj, self.attrib, json.dumps(value))

    def fdel(self, obj):
        """
        Delete the JSON value.
        """
        delattr(obj, self.attrib)


class FailedTask(models.Model):
    """
    Representation of tasks that have failed
    """
    task_name = models.CharField(max_length=255, db_index=True)
    task_id = models.CharField(max_length=255)
    argstring = models.CharField(max_length=4096, blank=True)
    kwargstring = models.CharField(max_length=4096, blank=True)
    exc = models.CharField(max_length=4096)
    einfo = models.TextField()
    datetime_failed = models.DateTimeField()
    datetime_resolved = models.DateTimeField(blank=True, null=True, default=None, db_index=True)

    args = JSONProperty('argstring', allowed_types={list, tuple})
    kwargs = JSONProperty('kwargstring', allowed_types={dict})

    def __unicode__(self):
        return u'FailedTask: {task_name}, args={args}, kwargs={kwargs} ({resolution})'.format(
            task_name=self.task_name,
            args=self.args,
            kwargs=self.kwargs,
            resolution=u"not resolved" if self.datetime_resolved is None else "resolved"
        )
