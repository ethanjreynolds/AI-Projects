############################################################
# CMPSC/DS 442: Homework 5 
############################################################

student_name = "Ethan Reynolds"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import os
import math
import email

############################################################
# Section 1: Spam Filter ( 50 points )
############################################################

def load_tokens(email_path):
    with open(email_path, 'r', encoding='utf-8') as file:
        message = email.message_from_file(file)
        tokens = []
        for line in email.iterators.body_line_iterator(message):
            tokens.extend(line.strip().split())
        return tokens

def log_probs(email_paths, smoothing):
    word_counts = {}
    total_count = 0
    
    for path in email_paths:
        tokens = load_tokens(path)
        for token in tokens:
            if token in word_counts:
                word_counts[token] += 1
            else:
                word_counts[token] = 1
        total_count += len(tokens)
    
    V = len(set(word_counts.keys()))
    probs = {}
    for word in set(word_counts.keys()):
        probs[word] = math.log((word_counts[word] + smoothing) / (total_count + smoothing * (V + 1)))
    
    probs["<UNK>"] = math.log(smoothing / (total_count + smoothing * (V + 1)))
    
    return probs

class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):
        spam_paths = []
        for filename in os.listdir(spam_dir):
            full_path = os.path.join(spam_dir, filename)
            spam_paths.append(full_path)
        
        ham_paths = []
        for filename in os.listdir(ham_dir):
            full_path = os.path.join(ham_dir, filename)
            ham_paths.append(full_path)
            
        self.spam_log_probs = log_probs(spam_paths, smoothing)
        self.ham_log_probs = log_probs(ham_paths, smoothing)
        
        self.spam_vocab = set(self.spam_log_probs.keys())
        self.ham_vocab = set(self.ham_log_probs.keys())

        spams = len(spam_paths)
        hams = len(ham_paths)
        combo = spams + hams
        self.p_spam = spams / combo
        self.p_ham = hams / combo
            
    def is_spam(self, email_path):
        tokens = load_tokens(email_path)

        word_counts = {}
        for token in tokens:
            word_counts[token] = word_counts.get(token, 0) + 1
        
        log_spam = math.log(self.p_spam)
        log_ham = math.log(self.p_ham)
        
        for word, count in word_counts.items():
            log_spam += count * self.spam_log_probs.get(word, self.spam_log_probs["<UNK>"])
            log_ham += count * self.ham_log_probs.get(word, self.ham_log_probs["<UNK>"])
        
        return log_spam > log_ham

    def most_indicative_spam(self, n):
        indicate_vals = {}
        for w in self.spam_vocab & self.ham_vocab:
            indicate_vals[w] = self.spam_log_probs[w] - math.log(math.exp(self.spam_log_probs[w] + math.log(self.p_spam)) + math.exp(self.ham_log_probs[w] + math.log(self.p_ham)))
        return sorted(indicate_vals, key=indicate_vals.get, reverse=True)[:n]

    def most_indicative_ham(self, n):
        indicate_vals = {}
        for w in self.spam_vocab & self.ham_vocab:
            indicate_vals[w] = self.ham_log_probs[w] - math.log(math.exp(self.spam_log_probs[w] + math.log(self.p_spam)) + math.exp(self.ham_log_probs[w] + math.log(self.p_ham)))
        return sorted(indicate_vals, key=indicate_vals.get, reverse=True)[:n]

# ham_dir = "homework5_data/train/ham/"
# spam_dir = "homework5_data/train/spam/"
# print(load_tokens(ham_dir+"ham2")[110:114])
# print(load_tokens(spam_dir+"spam2")[:4])
# paths = ["homework5_data/train/ham/ham%d" % i for i in range(1,11)]
# p = log_probs(paths, 1e-5)
# print(p["the"])
# print(p["line"])
# paths2 = ["homework5_data/train/spam/spam%d" % i for i in range(1,11)]
# p2 = log_probs(paths2, 1e-5)
# print(p2["Credit"])
# print(p2["<UNK>"])
# sf = SpamFilter("homework5_data/train/spam", "homework5_data/train/ham", 1e-5)
# print(sf.is_spam("homework5_data/train/spam/spam1"))
# print(sf.is_spam("homework5_data/train/spam/spam2"))
# print(sf.is_spam("homework5_data/train/ham/ham1"))
# print(sf.is_spam("homework5_data/train/ham/ham2"))
# print(sf.most_indicative_spam(5))
# print(sf.most_indicative_ham(5))

############################################################
# Section 2: Hidden Markov Models ( 50 points )
############################################################

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


