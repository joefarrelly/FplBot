

def format_identifier(identifier):
    # identifier = (identifier.replace('_', ' ')).title()
    if identifier == 'goals_scored':
        result = 'Goal!'
    elif identifier == 'assists':
        result = 'Assist!'
    elif identifier == 'own_goals':
        result = 'Own Goal!'
    elif identifier == 'penalties_saved':
        result = 'Penalty Saved!'
    elif identifier == 'penalties_missed':
        result = 'Penalty Miss!'
    elif identifier == 'yellow_cards':
        result = 'Yellow Card!'
    elif identifier == 'red_cards':
        result = 'Red Card!'
    elif identifier == 'saves':
        result = 'Save!'
    elif identifier == 'bonus':
        result = 'Bonus Points'
    else:
        result = identifier
    return result
