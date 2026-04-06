class Term:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args if args else []

    def __str__(self):
        if not self.args:
            return self.name
        return f"{self.name}({', '.join(str(arg) for arg in self.args)})"

class Literal:
    def __init__(self, positive, predicate, args):
        self.positive = positive
        self.predicate = predicate
        self.args = args

    def __str__(self):
        sign = "¬" if not self.positive else ""
        args_str = ", ".join(str(arg) for arg in self.args)
        if self.args:
            return f"{sign}{self.predicate}({args_str})"
        else:
            return f"{sign}{self.predicate}"

class Clause:
    def __init__(self, literals):
        self.literals = literals

    def __str__(self):
        return " ∨ ".join(str(literal) for literal in self.literals)


# Crear términos
x = Term("x")
y = Term("y")
a = Term("a")

# Crear literales
p_x = Literal(False, "P", [x,y])
not_q_a = Literal(False, "Q", [a])

# Crear una cláusula
clause = Clause([p_x, not_q_a])
print(clause)