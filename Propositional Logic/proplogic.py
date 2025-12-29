from copy import deepcopy


class Expr(object):
    def __hash__(self):
        return hash((type(self).__name__, self.hashable))

class Atom(Expr):
    def __init__(self, name):
        self.name = name
        self.hashable = name
    def __hash__(self):
        return hash(('Atom', self.name))
    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name
    def __repr__(self):
        return f"Atom({self.name})"
    def atom_names(self):
        return {self.name}
    def evaluate(self, assignment):
        if self.name in assignment:
            value = assignment[self.name]
        else:
            value = False
        return bool(value)
    def to_cnf(self):
        return self

class Not(Expr):
    def __init__(self, arg):
        self.arg = arg
        self.hashable = arg
    def __hash__(self):
        return hash(('Not', self.arg))
    def __eq__(self, other):
        return isinstance(other, Not) and self.arg == other.arg
    def __repr__(self):
        return f"Not({self.arg})"
    def atom_names(self):
        return self.arg.atom_names()
    def evaluate(self, assignment):
        return (not self.arg.evaluate(assignment))
    def to_cnf(self):
        return to_cnf(self)

class And(Expr):
    def __init__(self, *conjuncts):
        self.conjuncts = frozenset(conjuncts)
        self.hashable = self.conjuncts
    def __hash__(self):
        return hash(('And', self.conjuncts))
    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts
    def __repr__(self):
        reprs = []
        for c in self.conjuncts:
            r = repr(c)
            reprs.append(r)
        a = ", ".join(reprs)
        return f"And({a})"
    def atom_names(self):
        names = set()
        for c in self.conjuncts:
            names = names | c.atom_names()
        return names
    def evaluate(self, assignment):
        return all(c.evaluate(assignment) for c in self.conjuncts)
    def to_cnf(self):
        return to_cnf(self)

class Or(Expr):
    def __init__(self, *disjuncts):
        self.disjuncts = frozenset(disjuncts)
        self.hashable = self.disjuncts
    def __hash__(self):
        return hash(('Or', self.disjuncts))
    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts
    def __repr__(self):
        reprs = []
        for d in self.disjuncts:
            r = repr(d)
            reprs.append(r)
        o = ", ".join(reprs)
        return f"Or({o})"
    def atom_names(self):
        names = set()
        for d in self.disjuncts:
            names |= d.atom_names()
        return names
    def evaluate(self, assignment):
        return any(d.evaluate(assignment) for d in self.disjuncts)
    def to_cnf(self):
        return to_cnf(self)

class Implies(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)
    def __hash__(self):
        return hash(('Implies', self.left, self.right))
    def __eq__(self, other):
        return isinstance(other, Implies) and self.left == other.left and self.right == other.right
    def __repr__(self):
        return f"Implies({self.left}, {self.right})"
    def atom_names(self):
        return self.left.atom_names() | self.right.atom_names()
    def evaluate(self, assignment):
        return ((not self.left.evaluate(assignment)) or self.right.evaluate(assignment))
    def to_cnf(self):
        return to_cnf(self)

class Iff(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.hashable = (left, right)
    def __hash__(self):
        return hash(('Iff', frozenset([self.left, self.right])))
    def __eq__(self, other):
        if not isinstance(other, Iff):
            return False
        return (self.left == other.left and self.right == other.right) or (self.left == other.right and self.right == other.left)
    def __repr__(self):
        return f"Iff({self.left}, {self.right})"
    def atom_names(self):
        return self.left.atom_names() | self.right.atom_names()
    def evaluate(self, assignment):
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)
    def to_cnf(self):
        return to_cnf(self)

def help_rec(expr, i, assign, names, results):
    if i == len(names):
        if expr.evaluate(assign):
            results.append(assign.copy())
        return
    assign[names[i]] = False
    help_rec(expr, i + 1, assign, names, results)
    assign[names[i]] = True
    help_rec(expr, i + 1, assign, names, results)
    del assign[names[i]]

def satisfying_assignments(expr):
    names = sorted(list(expr.atom_names()))
    results = []
    help_rec(expr, 0, {}, names, results)
    return results

def distr_help(disjuncts):
    flat = []
    for d in disjuncts:
        if isinstance(d, Or):
            flat.extend(d.disjuncts)
        else:
            flat.append(d)
    disjuncts = flat
    
    if not any(isinstance(d, And) for d in disjuncts):
        return Or(*disjuncts)
    
    for i, d in enumerate(disjuncts):
        if isinstance(d, And):
            rest = disjuncts[:i] + disjuncts[i + 1:]
            distributed = [distr_help([c] + rest) for c in d.conjuncts]
            conjs = []
            for item in distributed:
                if isinstance(item, And):
                    conjs.extend(item.conjuncts)
                else:
                    conjs.append(item)
            if len(conjs) == 1:
                return conjs[0]
            return And(*conjs)

def to_cnf(expr):
    expr = deepcopy(expr)
    if isinstance(expr, Iff):
        return to_cnf(And(Implies(expr.left, expr.right), Implies(expr.right, expr.left)))
    if isinstance(expr, Implies):
        return to_cnf(Or(Not(expr.left), expr.right))
    
    if isinstance(expr, Not):
        a = expr.arg
        if isinstance(a, Atom):
            return expr
        elif isinstance(a, Not):
            return to_cnf(a.arg)
        elif isinstance(a, And):
            return to_cnf(Or(*[Not(c) for c in a.conjuncts]))
        elif isinstance(a, Or):
            return to_cnf(And(*[Not(d) for d in a.disjuncts]))
        elif isinstance(a, Implies) or isinstance(a, Iff):
            return to_cnf(Not(to_cnf(a)))
        else:
            return expr 
        
    if isinstance(expr, And):
        conjuncts = []
        for c in expr.conjuncts:
            ccnf = to_cnf(c)
            if isinstance(ccnf, And):
                conjuncts.extend(ccnf.conjuncts)
            else:
                conjuncts.append(ccnf)
        return And(*conjuncts)
    
    if isinstance(expr, Or):
        disjuncts = []
        for d in expr.disjuncts:
            d_cnf = to_cnf(d)
            if isinstance(d_cnf, Or):
                disjuncts.extend(d_cnf.disjuncts)
            else:
                disjuncts.append(d_cnf)
        return distr_help(disjuncts)
    if isinstance(expr, Atom):
        return expr
    
    return expr

def get_clauses(expr):
    stack = [expr]
    candidates = []
    while stack:
        node = stack.pop()
        if isinstance(node, And):
            for c in node.conjuncts:
                stack.append(c)
        else:
            candidates.append(node)
    clauses = []
    for c in candidates:
        lit_stack = [c]
        lits = set()
        while lit_stack:
            node = lit_stack.pop()
            if isinstance(node, Or):
                for d in node.disjuncts:
                    lit_stack.append(d)
                continue
            lits.add(node)
        clauses.append(frozenset(lits))
    return clauses
    
def is_tautology(clause):
    lits = {}
    for l in clause:
        if isinstance(l, Atom):
            name = l.name
            if name not in lits:
                lits[name] = set()
            lits[name].add(True)
        elif isinstance(l, Not) and isinstance(l.arg, Atom):
            name = l.arg.name
            if name not in lits:
                lits[name] = set()
            lits[name].add(False)
    for v in lits.values():
        if True in v and False in v:
            return True
    return False

def resolve(x, y):
    r = set()
    for l in x:
        if isinstance(l, Atom):
            comp = Not(l)
        if isinstance(l, Not) and isinstance(l.arg, Atom):
            comp = l.arg
        if comp in y:
            newc = set(x - {l}) | set(y - {comp})
            if not is_tautology(newc):
                r.add(frozenset(newc))
    return r

class KnowledgeBase(object):
    def __init__(self):
        self.clauses = set()
    def get_facts(self):
        result = set()
        for c in self.clauses:
            lits = list(c)
            if len(lits) == 0:
                expr = And()
            elif len(lits) == 1:
                expr = lits[0]
            else:
                sort = sorted(lits, key=lambda x: repr(x))
                expr = Or(*sort)
            result.add(expr)
        return result
    def tell(self, expr):
        cnf = to_cnf(expr)
        clauses = get_clauses(cnf)
        for c in clauses:
            if not is_tautology(c):
                self.clauses.add(c)
    def ask(self, expr):
        clauses = set(self.clauses)
        neg = to_cnf(Not(expr))
        for c in get_clauses(neg):
            if not is_tautology(c):
                clauses.add(c)
        new = set()
        while True:
            pairs = []
            clause_list = list(clauses)
            n = len(clause_list)
            for i in range(n):
                for j in range(i+1, n):
                    pairs.append((clause_list[i], clause_list[j]))
            added = False
            for (x, y) in pairs:
                res = resolve(x, y)
                if frozenset() in res:
                    return True
                for r in res:
                    if r not in clauses and r not in new:
                        new.add(r)
                        added = True
            if not added:
                return False
            clauses = clauses | new
            new.clear()

# a, b, c = map(Atom, "abc")
# print(Implies(a, Iff(b, c)))

# a, b, c = map(Atom, "abc")
# print(And(a, Or(Not(b), c)))

# print(Atom("a").atom_names())
# print(Not(Atom("a")).atom_names())
# expr = And(a, Implies(b, Iff(a, c)))
# print(expr.atom_names())

# e = Implies(Atom("a"), Atom("b"))
# print(e.evaluate({"a": False, "b": True}))
# print(e.evaluate({"a": True, "b": False}))

# e = And(Not(a), Or(b, c))
# print(e.evaluate({"a": False, "b": False, "c": True}))

# e = Implies(Atom("a"), Atom("b"))
# a = satisfying_assignments(e)
# print(a)

# e = Iff(Iff(Atom("a"), Atom("b")), Atom("c"))
# a = satisfying_assignments(e)
# print(a)

# print(Atom("a").to_cnf())
# a, b, c = map(Atom, "abc")
# print(Iff(a, Or(b, c)).to_cnf())
# print(Or(Atom("a"), Atom("b")).to_cnf())
# a, b, c, d = map(Atom, "abcd")
# print(Or(And(a, b), And(c, d)).to_cnf())

# a, b, c = map(Atom, "abc")
# kb = KnowledgeBase()
# kb.tell(a)
# kb.tell(Implies(a, b))
# print(kb.get_facts())
# print([kb.ask(x) for x in (a, b, c)])

# a, b, c = map(Atom, "abc")
# kb = KnowledgeBase()
# kb.tell(Iff(a, Or(b, c)))
# kb.tell(Not(a))
# print([kb.ask(x) for x in (a, Not(a))])
# print([kb.ask(x) for x in (b, Not(b))])
# print([kb.ask(x) for x in (c, Not(c))])