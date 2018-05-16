def to_sent(abbrv_string):
    '''to_sent: input: a comma seperate string of day abbreviations
                output: an english sentence enumerating those days'''
    abbrv_dict = {'MO': 'Monday', 'TU': 'Tuesday', 'WE': 'Wednesday',
                  'TH': 'Thursday', 'FR': 'Friday', 'SA': 'Saturday', 'SU': 'Sunday'}

    abbrv_list = abbrv_string.split(',')

    length = len(abbrv_list)-1

    sent = ' '

    for i in range(length):
        sent += abbrv_dict[abbrv_list[i]]

    sent += ("and " + abbrv_dict[length+1])

    return sent
