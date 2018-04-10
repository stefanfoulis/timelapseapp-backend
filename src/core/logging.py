import json, sys, os
from eliot import add_destinations, add_global_fields, start_action, Message


def stdout(message):
    print(message)


with start_action(action_type='logging-init'):
    Message.log(message_type='info', message='adding global fields')
    add_global_fields(
        process_id='{}:{}'.format(sys.argv[0], os.getpid()),
    )
    Message.log(message_type='info', message='adding stdout destination')
    add_destinations(stdout)
