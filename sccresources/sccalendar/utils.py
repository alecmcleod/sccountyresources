def to_sent(abbrv_string):
    '''to_sent: input: a comma seperate string of day abbreviations
                output: an english sentence enumerating those days'''
    abbrv_dict = {'MO': 'Monday', 'TU': 'Tuesday', 'WE': 'Wednesday',
                  'TH': 'Thursday', 'FR': 'Friday', 'SA': 'Saturday', 'SU': 'Sunday'}

    abbrv_list = abbrv_string.split(",")

    sent = [abbrv_dict[x] + ", " for x in abbrv_list[:-1]]
    sent.append("and " + abbrv_dict[abbrv_list[-1]])

    return "".join(sent)
