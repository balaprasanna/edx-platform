u"""
Testing persistent tasks
"""

from __future__ import print_function

from celery import task
from django.test import TestCase

from ..models import FailedTask
from ..task import PersistOnFailureTask


class PersistOnFailureTaskTestCase(TestCase):
    """
    Test that persistent tasks save the appropriate values when needed.
    """

    def setUp(self):
        @task(base=PersistOnFailureTask)
        def exampletask(exception=None):
            u"""
            A simple task for testing persistence
            """
            if exception:
                raise ValueError(exception)
            return
        self.exampletask = exampletask
        super(PersistOnFailureTaskTestCase, self).setUp()

    def test_exampletask_without_failure(self):
        result = self.exampletask.delay()
        result.wait()
        self.assertEqual(result.status, u'SUCCESS')
        self.assertFalse(FailedTask.objects.exists())

    def test_exampletask_with_failure(self):
        result = self.exampletask.delay(exception=u'The example task failed')
        with self.assertRaises(ValueError):
            result.wait()
        self.assertEqual(result.status, u'FAILURE')
        failed_task_object = FailedTask.objects.get()
        # Assert that we get the kind of data we expect
        self.assertEqual(
            failed_task_object.task_name,
            u'openedx.core.djangoapps.persistenttask.tests.test_task.exampletask'
        )
        self.assertEqual(failed_task_object.argstring, u'[]')
        self.assertEqual(failed_task_object.args, [])
        self.assertEqual(failed_task_object.kwargstring, u'{"exception": "The example task failed"}')
        self.assertEqual(failed_task_object.kwargs, {u'exception': u'The example task failed'})
        self.assertEqual(failed_task_object.exc, u"ValueError(u'The example task failed',)")
        self.assertIsNone(failed_task_object.datetime_resolved)

    def test_persists_when_called_with_wrong_args(self):
        result = self.exampletask.delay(err=True)
        with self.assertRaises(TypeError):
            result.wait()
        self.assertEqual(result.status, u'FAILURE')
        failed_task_object = FailedTask.objects.get()
        self.assertEqual(failed_task_object.kwargs, {u'err': True})

    def test_persists_with_overlength_field(self):
        overlong_message = u'A' * 5000
        result = self.exampletask.delay(exception=overlong_message)
        with self.assertRaises(ValueError):
            result.wait()
        failed_task_object = FailedTask.objects.get()
        self.assertEqual(len(failed_task_object.exc), 255)
