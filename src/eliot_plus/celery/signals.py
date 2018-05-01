from celery.signals import (
    before_task_publish,
    after_task_publish,
    task_prerun,
    task_postrun,
    task_failure,
)
from celery.states import SUCCESS

import eliot

from . import messages


@before_task_publish.connect
def task_pre_queued(sender, signal, **kwargs):
    # FIXME: extract eliot_action_uuid from task_kwargs and use it as a context
    #        for the celery action, if it is given. Otherwise start a new
    #        context.

    # eliot_parent_uuid = kwargs['body'][1].get('eliot_parent_uuid')
    # kwargs['eliot_parent_uuid'] = eliot_parent_uuid
    action = messages.start_celery_task(**kwargs)

    # Start a new action but don't finish it.
    # Later signals will do that.
    # action = messages.CeleryPreQueuedSignalAction(
    #     sender=sender,
    #     celery_info=kwargs,
    #     parent_action_uuid=None,
    # )
    # # store the action uuid in celery so later signals can retrieve it.
    # action_uuid = action.serialize_task_id().decode('ascii')
    # task_kwargs = kwargs['body'][1]
    # task_kwargs['eliot_action_uuid'] = action_uuid


@after_task_publish.connect
def task_queued(sender, signal, **kwargs):
    task_kwargs = kwargs['body'][1]
    eliot_celery_task_uuid = task_kwargs['eliot_celery_task_uuid']
    action = eliot.Action.continue_task(task_id=eliot_celery_task_uuid)
    messages.CeleryQueuedSignal.log()
    task_kwargs['eliot_celery_task_uuid'] = action.serialize_task_id().decode('ascii')


@task_prerun.connect
def task_start(sender, signal, **kwargs):
    task_kwargs = kwargs['kwargs']
    eliot_celery_task_uuid = task_kwargs['eliot_celery_task_uuid']
    action = eliot.Action.continue_task(task_id=eliot_celery_task_uuid)
    messages.CeleryStartedSignal.log(hi='there')
    task_kwargs['eliot_celery_task_uuid'] = action.serialize_task_id().decode('ascii')


@task_postrun.connect
def task_complete(sender, signal, **kwargs):
    from pprint import pprint as pp
    pp(kwargs)
    task_kwargs = kwargs['kwargs']
    eliot_celery_task_uuid = task_kwargs['eliot_celery_task_uuid']
    action = eliot.Action.continue_task(task_id=eliot_celery_task_uuid)
    task_kwargs['eliot_celery_task_uuid'] = action.serialize_task_id().decode('ascii')

    # FIXME: check return state from celery if the finish was sucessful
    action.finish()


@task_failure.connect
def task_failure(sender=None, signal=None, **kwargs):
    from pprint import pprint as pp
    pp(kwargs)
    task_kwargs = kwargs['kwargs']
    eliot_celery_task_uuid = task_kwargs['eliot_celery_task_uuid']
    action = eliot.Action.continue_task(task_id=eliot_celery_task_uuid)
    messages.CeleryStartedSignal.log()
    task_kwargs['eliot_celery_task_uuid'] = action.serialize_task_id().decode('ascii')

    # FIXME: return error state from celery
    action.finish('something fucked up')


# FIXME: add task_revoked, task_unknown, task_rejected and possibly more from
#        http://docs.celeryproject.org/en/latest/userguide/signals.html
