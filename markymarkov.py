import sys
import collections
import random
import bisect


class MarkyMarkov(object):

    end = '\n'

    def __init__(self, order, allow_duplicates=True):
        self.order = order
        self.counts = collections.defaultdict(collections.Counter)
        self.dirty = {}
        self.cdf = {}
        self.cumulative_sum = {}
        self.state_list = {}
        self.words = set()
        self.allow_duplicates = allow_duplicates

    def add_word(self, word):
        if not self.allow_duplicates and word in self.words:
            return None
        else:
            padded = ' ' * self.order + word + self.end
            for index in range(self.order, len(padded)):
                key = padded[(index - self.order):index]
                value = padded[index]
                self.counts[key][value] += 1
                self.dirty[key] = True
            self.words.add(word)

    def _create_cdf(self, key):
        cumulative_sum = 0
        self.state_list[key] = []
        self.cdf[key] = []
        for state, count in self.counts[key].iteritems():
            cumulative_sum += count
            self.state_list[key].append(state)
            self.cdf[key].append(cumulative_sum)
        self.dirty[key] = False
        self.cumulative_sum[key] = cumulative_sum

    def choose(self, state):
        if self.dirty[state]:
            self._create_cdf(state)
        index = bisect.bisect(
            self.cdf[state],
            random.random() * self.cumulative_sum[state]
        )
        return self.state_list[state][index]

    def generate_word(self):
        word = ' ' * self.order
        while True:
            state = word[-self.order:]
            next_char = self.choose(state)
            if next_char == self.end:
                break
            else:
                word += next_char
        return word[self.order:]

    @classmethod
    def from_file(cls, filename, order=1, allow_duplicates=False):
        result = cls(order, allow_duplicates=allow_duplicates)
        with open(filename) as infile:
            for line in infile:
                stripped = line.strip().decode('utf8').lower()
                if stripped:
                    result.add_word(stripped)
        return result


def ikea():

    ikea = MarkyMarkov.from_file(sys.argv[1], order=4)
    swedish = MarkyMarkov.from_file(sys.argv[2], order=0)
    for i in range(1000000):
        word = ikea.generate_word()
        if not word in ikea.words and not word in swedish.words:
            print word.encode('utf8')


def generate():

    mc = MarkyMarkov.from_file(sys.argv[1], order=4)

    reference = MarkyMarkov(0)
    if len(sys.argv) > 2:
        reference = MarkyMarkov.from_file(sys.argv[2], order=0)

    n = 0
    while n < 10:
        word = mc.generate_word()
        if not word in mc.words and not word in reference.words:
            print word.encode('utf8')
            n += 1

if __name__ == '__main__':

    generate()
