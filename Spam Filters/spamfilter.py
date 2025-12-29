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

# ham_dir = "data/train/ham/"
# spam_dir = "data/train/spam/"
# print(load_tokens(ham_dir+"ham2")[110:114])
# print(load_tokens(spam_dir+"spam2")[:4])
# paths = ["data/train/ham/ham%d" % i for i in range(1,11)]
# p = log_probs(paths, 1e-5)
# print(p["the"])
# print(p["line"])
# paths2 = ["data/train/spam/spam%d" % i for i in range(1,11)]
# p2 = log_probs(paths2, 1e-5)
# print(p2["Credit"])
# print(p2["<UNK>"])
# sf = SpamFilter("data/train/spam", "data/train/ham", 1e-5)
# print(sf.is_spam("data/train/spam/spam1"))
# print(sf.is_spam("data/train/spam/spam2"))
# print(sf.is_spam("data/train/ham/ham1"))
# print(sf.is_spam("data/train/ham/ham2"))
# print(sf.most_indicative_spam(5))
# print(sf.most_indicative_ham(5))