class LeadScoring:
    @staticmethod
    def score(experience, location):
        score = experience * 10
        if location.lower() in ['mumbai', 'delhi', 'bangalore']:
            score += 20
            category = 'Hot'
        elif experience > 5:
            category = 'Experienced'
        else:
            category = 'Normal'
        return score, category
