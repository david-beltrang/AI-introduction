import copy

class Term:
    """Representa un término: variable (X, Y...) o constante (a, b, jack...) o función f(x)."""
    def __init__(self, name, args=None):
        self.name = name
        self.args = args if args else []

    def is_variable(self):
        """Una variable empieza con mayúscula."""
        return len(self.name) > 0 and self.name[0].isupper()

    def __str__(self):
        if not self.args:
            return self.name
        return f"{self.name}({', '.join(str(arg) for arg in self.args)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Term):
            return False
        return self.name == other.name and self.args == other.args

    def __hash__(self):
        return hash((self.name, tuple(self.args)))


class Literal:
    """Representa un predicado con signo: P(x,y) o ¬P(x,y)."""
    def __init__(self, positive, predicate, args):
        self.positive = positive
        self.predicate = predicate
        self.args = args  # lista de Term

    def negate(self):
        """Retorna una copia negada de este literal."""
        return Literal(not self.positive, self.predicate, copy.deepcopy(self.args))

    def complements(self, other):
        """Verifica si este literal es complementario a otro (mismo predicado, signo opuesto)."""
        return self.predicate == other.predicate and self.positive != other.positive

    def __str__(self):
        sign = "¬" if not self.positive else ""
        args_str = ", ".join(str(arg) for arg in self.args)
        if self.args:
            return f"{sign}{self.predicate}({args_str})"
        else:
            return f"{sign}{self.predicate}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return False
        return (self.positive == other.positive and
                self.predicate == other.predicate and
                self.args == other.args)

    def __hash__(self):
        return hash((self.positive, self.predicate, tuple(self.args)))


class Clause:
    """Representa una cláusula: disyunción de literales (L1 ∨ L2 ∨ ... ∨ Ln)."""
    def __init__(self, literals):
        self.literals = literals

    def is_empty(self):
        """Cláusula vacía = contradicción encontrada."""
        return len(self.literals) == 0

    def __str__(self):
        if not self.literals:
            return "□ (cláusula vacía)"
        return " ∨ ".join(str(literal) for literal in self.literals)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Clause):
            return False
        return set((l.positive, l.predicate, tuple(l.args)) for l in self.literals) == \
               set((l.positive, l.predicate, tuple(l.args)) for l in other.literals)

    def __hash__(self):
        return hash(frozenset((l.positive, l.predicate, tuple(l.args)) for l in self.literals))