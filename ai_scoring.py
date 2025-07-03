def calculate_score(category, priority):
    base_score = {'cold': 10, 'warm': 30, 'hot': 50}
    bonus = {'low': 0, 'medium': 10, 'high': 20}
    return base_score.get(category, 0) + bonus.get(priority, 0)
