import itertools

class ClauseKnowledgeBase:
    def __init__(self):
        self.clauses = []

    @staticmethod
    def declare(kb, clause_strings):
        for clause_str in clause_strings:
            clause = Clause.parse_clause(clause_str)
            clause.flatten()
            kb.add(clause)

    def add(self, clause):
        self.clauses.append(clause)


class Clause:
    def __init__(self):
        self.literals = []

    def __repr__(self):
        return '{}' if len(self.literals) == 0 else ' OR '.join(str(literal) for literal in self.literals)

    def flatten(self):
        self.literals = sorted(set(self.literals))

    def __lt__(self, rhs):
        return (len(self.literals), self.literals) < (len(rhs.literals), rhs.literals)

    def __eq__(self, rhs):
        return self.literals == rhs.literals

    def __hash__(self):
        return hash(tuple(self.literals))

    def empty(self):
        return len(self.literals) == 0

    def add(self, literal):
        self.literals.append(literal)

    def negate(self):
        for literal in self.literals:
            literal.negate()

    def is_pointless(self):
        for i in range(len(self.literals) - 1):
            if self.literals[i].complement(self.literals[i + 1]):
                return True
        return False

    def copy_except(self, excluded_literal):
        new_clause = Clause()
        for literal in self.literals:
            if literal != excluded_literal:
                new_clause.add(literal.copy())
        return new_clause

    @staticmethod
    def parse_clause(clause_str):
        literal_strings = clause_str.strip().split('OR')
        clause = Clause()
        for literal_str in literal_strings:
            literal = Literal.parse_literal(literal_str)
            clause.add(literal)
        clause.flatten()
        return clause

    @staticmethod
    def merge(c1, c2):
        merged_clause = Clause()
        merged_clause.literals = c1.literals + c2.literals
        merged_clause.flatten()
        return merged_clause

    @staticmethod
    def resolve(ci, cj):
        resolvents = set()
        found_empty_clause = False

        for li in ci.literals:
            for lj in cj.literals:
                if li.complement(lj):
                    new_clause = Clause.merge(ci.copy_except(li), cj.copy_except(lj))
                    if not new_clause.is_pointless():
                        if new_clause.empty():
                            found_empty_clause = True
                        resolvents.add(new_clause)

        return resolvents, found_empty_clause


class Literal:
    def __init__(self, symbol='', negated=False):
        self.symbol = symbol
        self.negated = negated

    def copy(self):
        return Literal(self.symbol, self.negated)

    def __repr__(self):
        return f'-{self.symbol}' if self.negated else self.symbol

    def __eq__(self, rhs):
        return self.symbol == rhs.symbol and self.negated == rhs.negated

    def __lt__(self, rhs):
        return (self.symbol, self.negated) < (rhs.symbol, rhs.negated)

    def __hash__(self):
        return hash((self.symbol, self.negated))

    def complement(self, rhs):
        return self.symbol == rhs.symbol and self.negated != rhs.negated

    def negate(self):
        self.negated = not self.negated

    @staticmethod
    def parse_literal(literal_str):
        literal_str = literal_str.strip()
        return Literal(symbol=literal_str[1:], negated=True) if literal_str[0] == '-' else Literal(symbol=literal_str)


def pl_resolution(kb, alpha):
    steps = []
    entailment = False
    alpha.negate()
    clauses = set(kb.clauses)
    clauses.add(alpha)

    while True:
        new_clauses = set()

        for ci, cj in itertools.combinations(sorted(clauses), 2):
            resolvents, contradict = Clause.resolve(ci, cj)
            new_clauses.update(resolvents)
            entailment |= contradict

        generated_clauses = sorted(new_clauses.difference(clauses))
        steps.append(generated_clauses)
        clauses.update(new_clauses)

        if entailment:
            return True, steps
        if not generated_clauses:
            return False, steps


def read_file(input_file):
    kb = ClauseKnowledgeBase()
    with open(input_file, 'r') as f:
        alpha = Clause.parse_clause(f.readline())
        num_clauses = int(f.readline().strip())
        clause_strings = f.readlines()
        ClauseKnowledgeBase.declare(kb, clause_strings)
    return kb, alpha


def write_file(output_file, steps, entailment):
    with open(output_file, 'w') as f:
        for clauses in steps:
            f.write(f'{len(clauses)}\n')
            for clause in clauses:
                f.write(f'{clause}\n')
        f.write('YES' if entailment else 'NO')

