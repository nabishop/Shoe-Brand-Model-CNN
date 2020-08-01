class AnalyzedTweets:
    def __init__(self, num_pos, num_neut, num_neg):
        self.num_pos = num_pos
        self.num_neut = num_neut
        self.num_neg = num_neg

    def __str__(self):
        return "Num Positive: " + str(self.num_pos) + " Num Neutral: " + \
               str(self.num_neut) + " Num Negative: " + str(self.num_neg)
