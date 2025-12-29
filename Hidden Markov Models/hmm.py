import math


def load_corpus(path):
    sentences = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            pairs = []
            for token_tag in line.split():
                token, tag = token_tag.split('=')
                pairs.append((token, tag))
            sentences.append(pairs)
    return sentences

class Tagger(object):

    def __init__(self, sentences):
        alpha = 1.0
        tags = set()
        vocab = set()
        for s in sentences:
            for w, t in s:
                tags.add(t)
                vocab.add(w)
        
        self.tags = sorted(tags)
        self.tag_idx = {t: i for i, t in enumerate(self.tags)}
        self.vocab = vocab
        self.V = len(self.vocab)
        self.N = len(self.tags)

        init_counts = {t: 0 for t in self.tags}
        trans_counts = {t: {u: 0 for u in self.tags} for t in self.tags}
        emit_counts = {t: {} for t in self.tags}
        trans_totals = {t: 0 for t in self.tags}
        emit_totals = {t: 0 for t in self.tags}
        
        for s in sentences:
            init_tag = s[0][1]
            init_counts[init_tag] += 1
            for i, (w, t) in enumerate(s):
                emit_totals[t] += 1
                emit_counts[t][w] = emit_counts[t].get(w, 0) + 1
                if i > 0:
                    prev = s[i - 1][1]
                    trans_counts[prev][t] += 1
                    trans_totals[prev] += 1
        
        ssum = sum(init_counts.values())
        self.pi = {}
        for t in self.tags:
            self.pi[t] = (init_counts[t] + alpha) / (ssum + alpha * self.N)
            
        self.a = {}
        for t in self.tags:
            self.a[t] = {}
            for u in self.tags:
                self.a[t][u] = (trans_counts[t][u] + alpha) / (trans_totals[t] + alpha * self.N)
        
        self.b = {}
        for t in self.tags:
            self.b[t] = {}
            total = emit_totals[t]
            for w, c in emit_counts[t].items():
                self.b[t][w] = (c + alpha) / (total + alpha * (self.V + 1))
            self.b[t]["<UNK>"] = alpha / (total + alpha * (self.V + 1))

    def most_probable_tags(self, tokens):
        tags = []
        for w in tokens:
            most = -1000000000
            for t in self.tags:
                prob = self.b[t].get(w, self.b[t]["<UNK>"])
                if prob > most:
                    most = prob
                    taken = t
            tags.append(taken)
        return tags

    def viterbi_tags(self, tokens):
        T = len(tokens)
        
        v = [{t: -1000000000 for t in self.tags} for i in range(T) ]
        bt = [{t: None for t in self.tags} for i in range(T) ]
        
        for t in self.tags:
            emit = self.b[t].get(tokens[0], self.b[t]["<UNK>"])
            v[0][t] = math.log(self.pi[t]) + emit
        
        for i in range(1, T):
            w = tokens[i]
            for t in self.tags:
                emit = self.b[t].get(w, self.b[t]["<UNK>"])
                maxp = -1000000000
                for prev in self.tags:
                    p = v[i - 1][prev] + math.log(self.a[prev][t]) + math.log(emit)
                    if p > maxp:
                        maxp = p
                        taken = prev
                v[i][t] = maxp
                bt[i][t] = taken
        
        term = max(self.tags, key=v[T - 1].get)
        seq = [None for i in range(T)]
        seq[T - 1] = term
        for i in range(T - 1, 0, -1):
            seq[i - 1] = bt[i][seq[i]]
        return seq

# c = load_corpus("brown_corpus.txt")
# print(c[1402])
# t = Tagger(c)
# print(t.most_probable_tags(["The", "man", "walks", "."]))
# s = "I am waiting to reply".split()
# print(t.most_probable_tags(s))
# print(t.viterbi_tags(s))
# s = "I saw the play".split()
# print(t.most_probable_tags(s))
# print(t.viterbi_tags(s))
