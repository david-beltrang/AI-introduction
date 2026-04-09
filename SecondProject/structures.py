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

# --- Clases para el Árbol de Expresión (AST) ---

class Formula:
    """Clase base para todas las fórmulas."""
    pass

class Predicado(Formula):
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos # Lista de Term

    def __str__(self):
        if not self.argumentos:
            return self.nombre
        args_str = ", ".join(str(a) for a in self.argumentos)
        return f"{self.nombre}({args_str})"

class Not(Formula):
    def __init__(self, formula):
        self.formula = formula

    def __str__(self):
        return f"¬({self.formula})"

class And(Formula):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def __str__(self):
        return f"({self.izquierda} ∧ {self.derecha})"

class Or(Formula):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def __str__(self):
        return f"({self.izquierda} ∨ {self.derecha})"

class Implica(Formula):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def __str__(self):
        return f"({self.izquierda} → {self.derecha})"

class DobleImplica(Formula):
    def __init__(self, izquierda, derecha):
        self.izquierda = izquierda
        self.derecha = derecha

    def __str__(self):
        return f"({self.izquierda} ↔ {self.derecha})"

class ParaTodo(Formula):
    def __init__(self, variable, formula):
        self.variable = variable # Term
        self.formula = formula

    def __str__(self):
        return f"∀{self.variable} {self.formula}"

class Existe(Formula):
    def __init__(self, variable, formula):
        self.variable = variable # Term
        self.formula = formula

    def __str__(self):
        return f"∃{self.variable} {self.formula}"
