# options
NO = 0
YES = 1


def translate_option(options):
    option_list = []
    for option in options:
        option_list.append((option[0], option[1]))
    return option_list


yes_no_options = translate_option([("No", NO), ("Yes", YES)])
