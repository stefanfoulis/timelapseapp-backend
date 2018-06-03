import uuid

import eliot
import eliot._action


def extract_sender(sender):
    if isinstance(sender, str):
        return sender
    else:
        return sender.name


CelerySignalSenderField = eliot.Field("sender", extract_sender)


def extract_action(action):
    if isinstance(action, str):
        return action
    elif action is None:
        return None
    else:
        return action.serialize_task_id().decode("ascii")


CelerySignalParentActionField = eliot.Field("parent_action_uuid", extract_action)


def extract_celery_info(celery_info):
    return {
        key: value
        for key, value in celery_info.items()
        if key
        in (
            "body",
            "exchange",
            "routing_key",
            # 'declare',
            "headers",
            "properties",
            "retry_policy",
        )
    }


CelerySignalTaskInfoField = eliot.Field("celery_info", extract_celery_info)


CeleryPreQueuedSignalAction = eliot.ActionType(
    "celery:task",
    startFields=[
        CelerySignalSenderField,
        CelerySignalParentActionField,
        CelerySignalTaskInfoField,
    ],
    successFields=[],
)


def start_celery_task(**kwargs):
    eliot_task_uuid = str(uuid.uuid4())
    task_kwargs = kwargs["body"][1]
    action_type = "celery:task"

    local_action = eliot.current_action()
    if local_action:
        task_kwargs["eliot_parent_uuid"] = local_action.serialize_task_id().decode(
            "ascii"
        )

    action = eliot.Action(
        logger=None,
        task_uuid=eliot_task_uuid,
        task_level=eliot._action.TaskLevel(level=[]),
        action_type=action_type,
    )
    action._start(extract_celery_info(kwargs))
    task_kwargs["eliot_celery_task_uuid"] = action.serialize_task_id().decode("ascii")
    return action


CeleryQueuedSignal = eliot.MessageType("celery:task:started", [])


CeleryStartedSignal = eliot.MessageType("celery:task:started", [])


CeleryCompletedSignal = eliot.MessageType("celery:task:completed", [])


CeleryFailedSignal = eliot.MessageType("celery:task:failed", [])
