import calendar

import pytz


def to_sent(abbrv_string):
    '''to_sent: input: a comma seperate string of day abbreviations
                output: an english sentence enumerating those days'''
    abbrv_dict = {
        'MO': 'Monday',
        'TU': 'Tuesday',
        'WE': 'Wednesday',
        'TH': 'Thursday',
        'FR': 'Friday',
        'SA': 'Saturday',
        'SU': 'Sunday'
    }

    abbrv_list = abbrv_string.split(",")

    sent = [abbrv_dict[x] + ", " for x in abbrv_list[:-1]]
    sent.append("and " + abbrv_dict[abbrv_list[-1]])

    return "".join(sent)


def parse_recurrence(rec_list):
    '''arguments: standard google calendars list of recurrance strings'''
    '''output : an english string describing when an event recurrs'''
    keys = ['FREQ', 'COUNT', 'INTERVAL', 'BYDAY', 'UNTIL']
    parse = ''
    out_string = ''
    for rule in rec_list:
        for key in keys:
            if key in rule:
                parse = rule.split('=')
                if parse[0] is 'FREQ':
                    parse = parse[1].lower() + ', '
                elif parse[0] is 'COUNT':
                    parse = ''
                elif parse[0] is 'INTERVAL':
                    parse = ''
                elif parse[0] is 'BYDAY':
                    parse = 'on' + to_sent(parse[1])
                elif parse[0] is 'UNTIL':
                    parse = 'until' + \
                        calendar.month_name[int(
                            parse[1][5:6])] + ',' + parse[1][7:]
                else:
                    break
        out_string += ("this event occurs " + parse)
    return out_string


def to_standard(military_string):
    '''to_standard: converts military time to standard and adds meridean'''

    military_list = military_string.split(':')
    if int(military_list[0]) > 12:
        return str(int(military_list[0]) - 12) + \
            ':' + military_list[1] + " P.M."
    else:
        return str(int(military_list[0])) + ':' + military_list[1] + " A.M."


pacific_tz = pytz.timezone('US/Pacific')


def get_tz():
    """Return the pacific time timezone"""
    return pacific_tz


def format_event_data(event):
    event.location = shorten_location(event.location)
    event.time_text = trim_event_time(event.time_text)
    return event


def trim_event_time(time_str):
    # Remove leading zeros from any word in string
    return ' '.join([word[1:] if word.startswith('0') else word for word in time_str.split()])


def shorten_location(location):
    try:
        trim_from = location.index(', CA')
    except (ValueError, AttributeError):
        pass
    else:
        location = location[:trim_from]
    return location

