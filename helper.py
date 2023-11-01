import json
import datetime

class User:
    """This class describes a generic user object"""

    def __init__(self, name, user_id, **kwargs):
        self.id = user_id
        self.name = name
        self.school_worker = False


class Event:
    """ This class describes event"""

    def __init__(self, event):
        self.event_title = event['title']
        self.date = event['date']
        self.decision_point = event['decision_point']


def json_append_user(user):
    data = json.load(open('users.json', 'r', encoding='utf-8'))
    data['users'].append({
        'name': user.name,
        'id': user.id,
        'school_worker': user.school_worker
    })
    with open('users.json', 'w', encoding='utf-8') as users_data:
        json.dump(data, users_data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))


def json_append_event(event):
    json_event = json.load(open('events.json', 'r', encoding='utf-8'))
    json_event['events'][event.event_title] = {}
    json_event['events'][event.event_title]['date'] = event.date
    json_event['events'][event.event_title]['decision_point'] = event.decision_point
    with open('events.json', 'w', encoding='utf-8') as event_data:
        json.dump(json_event, event_data, sort_keys=False, indent=4, ensure_ascii=False, separators=(',', ': '))


def json_append_task_list(event, task_list):
    task_list = list(map(lambda x: x.lower().strip(), task_list))
    json_event = json.load(open('events.json', 'r', encoding='utf-8'))
    if event.__class__ == Event:
        current_event = event.event_title
    else:
        current_event = event

    try:
        a = json_event['events'][current_event]['task_list']
    except KeyError:
        json_event['events'][current_event]['task_list'] = {}

    for task in task_list:
        json_event['events'][current_event]['task_list'][task] = {}
        json_event['events'][current_event]['task_list'][task]['task_completion'] = False
        json_event['events'][current_event]['task_list'][task]['ID'] = 0
        json_event['events'][current_event]['task_list'][task]['date'] = None

    json.dump(json_event, open('events.json', "w", encoding='utf-8'), sort_keys=False, indent=4, ensure_ascii=False,
              separators=(',', ': '))


def check_user_registered(message):
    users = json.load(open('users.json', 'r', encoding='utf-8'))
    for user in users['users']:
        if user['id'] == message.chat.id:
            return True
    else:
        return False


def request_event_list():
    events = list()
    json_events = json.load(open('events.json', 'r', encoding='utf-8'))
    for ev in json_events['events']:
        events.append(ev)
    return events


def json_display_event_tasks(event):
    json_event = json.load(open('events.json', 'r', encoding='utf-8'))
    try:
        data = json_event['events'][event]["task_list"]
    except KeyError:
        return False
    event_tasks = []
    for task in data:
        if data[task]['task_completion'] == False:
            event_tasks.append(task)
    return event_tasks


def json_change_task_status(current_event, changed_task, user_id):
    json_event = json.load(open('events.json', 'r', encoding='utf-8'))
    json_event['events'][current_event]["task_list"][changed_task]['task_completion'] = True
    json_event['events'][current_event]["task_list"][changed_task]['ID'] = user_id
    json_event['events'][current_event]["task_list"][changed_task]['date'] = datetime.date.today().strftime('%d:%m:%Y')
    json.dump(json_event, open('events.json', "w", encoding='utf-8'), sort_keys=False, indent=4, ensure_ascii=False,
              separators=(',', ': '))


def correctness_date(event):
    try:
        date = datetime.datetime.strptime(event['date'], '%d:%m:%Y')
        decision_point = datetime.datetime.strptime(event['decision_point'], '%d:%m:%Y')
        correctness = datetime.datetime.today() < decision_point < date
        return [1, 0][correctness]
    except ValueError:
        return 3


def json_task_list():
    json_events = json.load(open('events.json', 'r', encoding='utf-8'))
    events_dict = {}
    for event in json_events['events']:
        events_dict[event] = {}
        events_dict[event]['task_list'] = []
        events_dict[event]['date'] = json_events['events'][event]['date']
        events_dict[event]['decision_point'] = json_events['events'][event]['decision_point']
        for task in json_events['events'][event]['task_list']:
            events_dict[event]['task_list'].append(
                {task: json_events['events'][event]['task_list'][task]['task_completion']})
    return events_dict


