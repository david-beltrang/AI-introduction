"""
Módulo de Conversión a Forma Normal Conjuntiva (FNC).

Convierte expresiones en lógica de predicados de primer orden a FNC:
1. Eliminar bicondicionales (↔)
2. Eliminar implicaciones (→)
3. Mover negaciones hacia adentro (De Morgan + doble negación)
4. Estandarizar variables
5. Skolemizar (eliminar cuantificadores existenciales)
6. Eliminar cuantificadores universales
7. Distribuir ∨ sobre ∧
8. Separar en cláusulas

Entrada: string como "∀X(hombre(X) → mortal(X))"
Salida: lista de objetos Clause
"""

import re
import copy
from structures import Term, Literal, Clause
from parser import parse_literal


# ==================== TOKENIZER ====================

def tokenize(expression):
    """
    Convierte una expresión string en tokens.
    Ejemplo: "∀X(P(X) → Q(X))" -> ['∀', 'X', '(', 'P(X)', '→', 'Q(X)', ')']
    """
    tokens = []
    i = 0
    expr = expression.strip()

    while i < len(expr):
        c = expr[i]

        # Saltar espacios
        if c in ' \t\n':
            i += 1
            continue

        # Cuantificadores
        if c in '∀∃':
            tokens.append(c)
            i += 1
            continue

        # Conectivos lógicos
        if c == '¬':
            tokens.append('¬')
            i += 1
            continue
        if c == '∧':
            tokens.append('∧')
            i += 1
            continue
        if c == '∨':
            tokens.append('∨')
            i += 1
            continue
        if c == '→':
            tokens.append('→')
            i += 1
            continue
        if c == '↔':
            tokens.append('↔')
            i += 1
            continue

        # Paréntesis de agrupación
        if c == '(':
            # Es agrupación si viene después de operador, cuantificador, variable de cuantificador, negación, o inicio
            if (not tokens or tokens[-1] in ['∀', '∃', '¬', '∧', '∨', '→', '↔', '(']
                or (len(tokens) >= 2 and tokens[-2] in ['∀', '∃'])):
                tokens.append('(')
                i += 1
                continue
        if c == ')':
            open_count = sum(1 for t in tokens if t == '(') - sum(1 for t in tokens if t == ')')
            if open_count > 0:
                tokens.append(')')
                i += 1
                continue

        # Predicado con argumentos: nombre(args) o solo nombre/variable
        if c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_' or expr[j] == '-'):
                j += 1

            name = expr[i:j]

            # Si el token anterior es un cuantificador, esto es una variable de cuantificador
            if tokens and tokens[-1] in ('∀', '∃'):
                tokens.append(name)
                i = j
                continue

            # Ver si tiene paréntesis (predicado con argumentos)
            if j < len(expr) and expr[j] == '(':
                # Verificar que es un predicado y no una agrupación
                # Un predicado tiene argumentos simples (variables/constantes) separados por comas
                # Encontrar el cierre del paréntesis del predicado
                depth = 1
                k = j + 1
                is_predicate = True
                while k < len(expr) and depth > 0:
                    if expr[k] == '(':
                        depth += 1
                    elif expr[k] == ')':
                        depth -= 1
                    # Si encontramos un conectivo lógico dentro, no es un predicado simple
                    if depth > 0 and expr[k] in '→↔∧∨':
                        is_predicate = False
                    k += 1

                if is_predicate:
                    pred_str = expr[i:k]
                    tokens.append(pred_str)
                    i = k
                else:
                    # Es un predicado pero el paréntesis agrupa una fórmula compleja
                    # Solo tomar el nombre
                    tokens.append(name)
                    i = j
            else:
                tokens.append(name)
                i = j
            continue

        i += 1

    return tokens


# ==================== ÁRBOL DE EXPRESIÓN ====================

class ExprNode:
    """Nodo del árbol de expresiones lógicas."""
    pass

class LiteralNode(ExprNode):
    """Hoja: un literal como P(x) o ¬P(x)."""
    def __init__(self, literal_str, negated=False):
        self.literal_str = literal_str
        self.negated = negated

    def __str__(self):
        if self.negated:
            return f"¬{self.literal_str}"
        return self.literal_str

class NotNode(ExprNode):
    """Negación: ¬(expr)."""
    def __init__(self, child):
        self.child = child

    def __str__(self):
        return f"¬({self.child})"

class BinaryNode(ExprNode):
    """Operación binaria: ∧, ∨, →, ↔."""
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

class QuantifierNode(ExprNode):
    """Cuantificador: ∀X(expr) o ∃X(expr)."""
    def __init__(self, quantifier, variable, body):
        self.quantifier = quantifier  # '∀' o '∃'
        self.variable = variable
        self.body = body

    def __str__(self):
        return f"{self.quantifier}{self.variable}({self.body})"


# ==================== PARSER DE EXPRESIONES ====================

def parse_expression(tokens, pos=0):
    """
    Parser recursivo descendente para expresiones lógicas.
    Retorna (ExprNode, nueva_posición).
    """
    left, pos = parse_unary(tokens, pos)

    # Operadores binarios (de menor a mayor precedencia)
    while pos < len(tokens) and tokens[pos] in ('↔', '→', '∧', '∨'):
        op = tokens[pos]
        pos += 1
        right, pos = parse_unary(tokens, pos)
        left = BinaryNode(op, left, right)

    return left, pos


def parse_unary(tokens, pos):
    """Parsea negación, cuantificadores y átomos."""
    if pos >= len(tokens):
        raise ValueError("Expresión incompleta")

    token = tokens[pos]

    # Negación
    if token == '¬':
        pos += 1
        child, pos = parse_unary(tokens, pos)
        return NotNode(child), pos

    # Cuantificador
    if token in ('∀', '∃'):
        quantifier = token
        pos += 1
        variable = tokens[pos]
        pos += 1
        # Esperar '('
        if pos < len(tokens) and tokens[pos] == '(':
            pos += 1
            body, pos = parse_expression(tokens, pos)
            if pos < len(tokens) and tokens[pos] == ')':
                pos += 1
            return QuantifierNode(quantifier, variable, body), pos
        else:
            body, pos = parse_unary(tokens, pos)
            return QuantifierNode(quantifier, variable, body), pos

    # Paréntesis de agrupación
    if token == '(':
        pos += 1
        expr, pos = parse_expression(tokens, pos)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1
        return expr, pos

    # Predicado / literal
    return LiteralNode(token), pos


def parse_formula(text):
    """Convierte un string a un árbol de expresión."""
    tokens = tokenize(text)
    if not tokens:
        raise ValueError(f"No se pudo tokenizar: {text}")
    expr, _ = parse_expression(tokens, 0)
    return expr


# ==================== TRANSFORMACIONES A FNC ====================

def eliminate_biconditional(node):
    """Paso 1: Eliminar ↔. (A ↔ B) se convierte en (A → B) ∧ (B → A)."""
    if isinstance(node, LiteralNode):
        return node
    if isinstance(node, NotNode):
        return NotNode(eliminate_biconditional(node.child))
    if isinstance(node, QuantifierNode):
        return QuantifierNode(node.quantifier, node.variable,
                              eliminate_biconditional(node.body))
    if isinstance(node, BinaryNode):
        left = eliminate_biconditional(node.left)
        right = eliminate_biconditional(node.right)
        if node.op == '↔':
            return BinaryNode('∧',
                              BinaryNode('→', left, right),
                              BinaryNode('→', copy.deepcopy(right), copy.deepcopy(left)))
        return BinaryNode(node.op, left, right)
    return node


def eliminate_implication(node):
    """Paso 2: Eliminar →. (A → B) se convierte en (¬A ∨ B)."""
    if isinstance(node, LiteralNode):
        return node
    if isinstance(node, NotNode):
        return NotNode(eliminate_implication(node.child))
    if isinstance(node, QuantifierNode):
        return QuantifierNode(node.quantifier, node.variable,
                              eliminate_implication(node.body))
    if isinstance(node, BinaryNode):
        left = eliminate_implication(node.left)
        right = eliminate_implication(node.right)
        if node.op == '→':
            return BinaryNode('∨', NotNode(left), right)
        return BinaryNode(node.op, left, right)
    return node


def move_negation_inward(node):
    """
    Paso 3: Mover negaciones hacia adentro.
    - ¬¬A = A
    - ¬(A ∧ B) = ¬A ∨ ¬B  (De Morgan)
    - ¬(A ∨ B) = ¬A ∧ ¬B  (De Morgan)
    - ¬∀X(A) = ∃X(¬A)
    - ¬∃X(A) = ∀X(¬A)
    """
    if isinstance(node, LiteralNode):
        return node

    if isinstance(node, NotNode):
        child = node.child

        # Doble negación: ¬¬A = A
        if isinstance(child, NotNode):
            return move_negation_inward(child.child)

        # De Morgan: ¬(A ∧ B) = ¬A ∨ ¬B
        if isinstance(child, BinaryNode) and child.op == '∧':
            return move_negation_inward(
                BinaryNode('∨', NotNode(child.left), NotNode(child.right)))

        # De Morgan: ¬(A ∨ B) = ¬A ∧ ¬B
        if isinstance(child, BinaryNode) and child.op == '∨':
            return move_negation_inward(
                BinaryNode('∧', NotNode(child.left), NotNode(child.right)))

        # ¬∀X(A) = ∃X(¬A)
        if isinstance(child, QuantifierNode) and child.quantifier == '∀':
            return move_negation_inward(
                QuantifierNode('∃', child.variable, NotNode(child.body)))

        # ¬∃X(A) = ∀X(¬A)
        if isinstance(child, QuantifierNode) and child.quantifier == '∃':
            return move_negation_inward(
                QuantifierNode('∀', child.variable, NotNode(child.body)))

        # ¬literal
        if isinstance(child, LiteralNode):
            return LiteralNode(child.literal_str, negated=not child.negated)

        return NotNode(move_negation_inward(child))

    if isinstance(node, QuantifierNode):
        return QuantifierNode(node.quantifier, node.variable,
                              move_negation_inward(node.body))

    if isinstance(node, BinaryNode):
        return BinaryNode(node.op,
                          move_negation_inward(node.left),
                          move_negation_inward(node.right))

    return node


_skolem_counter = [0]

def skolemize(node, universal_vars=None):
    """
    Paso 5: Skolemización - eliminar cuantificadores existenciales.
    - ∃X(P(X)) → P(sk1) (constante de Skolem)
    - ∀Y∃X(P(X,Y)) → P(f_sk1(Y), Y) (función de Skolem)
    """
    if universal_vars is None:
        universal_vars = []

    if isinstance(node, LiteralNode):
        return node

    if isinstance(node, NotNode):
        return NotNode(skolemize(node.child, universal_vars))

    if isinstance(node, QuantifierNode):
        if node.quantifier == '∀':
            new_uvars = universal_vars + [node.variable]
            new_body = skolemize(node.body, new_uvars)
            return QuantifierNode('∀', node.variable, new_body)

        elif node.quantifier == '∃':
            _skolem_counter[0] += 1
            if universal_vars:
                # Función de Skolem: f_skN(Y1, Y2, ...)
                skolem_name = f"f_sk{_skolem_counter[0]}({', '.join(universal_vars)})"
            else:
                # Constante de Skolem: skN
                skolem_name = f"sk{_skolem_counter[0]}"

            new_body = replace_variable_in_tree(node.body, node.variable, skolem_name)
            return skolemize(new_body, universal_vars)

    if isinstance(node, BinaryNode):
        return BinaryNode(node.op,
                          skolemize(node.left, universal_vars),
                          skolemize(node.right, universal_vars))

    return node


def replace_variable_in_tree(node, var_name, replacement):
    """Reemplaza todas las ocurrencias de una variable en el árbol."""
    if isinstance(node, LiteralNode):
        # Reemplazar en el string del literal
        new_str = node.literal_str
        # Reemplazar la variable dentro de los paréntesis del predicado
        new_str = re.sub(
            r'\b' + re.escape(var_name) + r'\b',
            replacement,
            new_str
        )
        return LiteralNode(new_str, node.negated)

    if isinstance(node, NotNode):
        return NotNode(replace_variable_in_tree(node.child, var_name, replacement))

    if isinstance(node, BinaryNode):
        return BinaryNode(node.op,
                          replace_variable_in_tree(node.left, var_name, replacement),
                          replace_variable_in_tree(node.right, var_name, replacement))

    if isinstance(node, QuantifierNode):
        if node.variable == var_name:
            return node  # Variable ligada, no reemplazar
        return QuantifierNode(node.quantifier, node.variable,
                              replace_variable_in_tree(node.body, var_name, replacement))

    return node


def drop_universal_quantifiers(node):
    """Paso 6: Eliminar cuantificadores universales (las variables quedan implícitamente universales)."""
    if isinstance(node, LiteralNode):
        return node
    if isinstance(node, NotNode):
        return NotNode(drop_universal_quantifiers(node.child))
    if isinstance(node, QuantifierNode):
        if node.quantifier == '∀':
            return drop_universal_quantifiers(node.body)
        return node  # No debería haber ∃ después de skolemizar
    if isinstance(node, BinaryNode):
        return BinaryNode(node.op,
                          drop_universal_quantifiers(node.left),
                          drop_universal_quantifiers(node.right))
    return node


def distribute_or_over_and(node):
    """
    Paso 7: Distribuir ∨ sobre ∧.
    A ∨ (B ∧ C) = (A ∨ B) ∧ (A ∨ C)
    (A ∧ B) ∨ C = (A ∨ C) ∧ (B ∨ C)
    """
    if isinstance(node, LiteralNode) or isinstance(node, NotNode):
        return node

    if isinstance(node, BinaryNode):
        left = distribute_or_over_and(node.left)
        right = distribute_or_over_and(node.right)

        if node.op == '∨':
            # A ∨ (B ∧ C) = (A ∨ B) ∧ (A ∨ C)
            if isinstance(right, BinaryNode) and right.op == '∧':
                return distribute_or_over_and(
                    BinaryNode('∧',
                               BinaryNode('∨', copy.deepcopy(left), right.left),
                               BinaryNode('∨', copy.deepcopy(left), right.right)))

            # (A ∧ B) ∨ C = (A ∨ C) ∧ (B ∨ C)
            if isinstance(left, BinaryNode) and left.op == '∧':
                return distribute_or_over_and(
                    BinaryNode('∧',
                               BinaryNode('∨', left.left, copy.deepcopy(right)),
                               BinaryNode('∨', left.right, copy.deepcopy(right))))

        return BinaryNode(node.op, left, right)

    return node


def extract_clauses(node):
    """
    Paso 8: Extraer cláusulas del árbol en FNC.
    Separa por ∧ y recolecta los literales de cada disyunción.
    """
    if isinstance(node, BinaryNode) and node.op == '∧':
        return extract_clauses(node.left) + extract_clauses(node.right)

    # Recolectar literales de esta disyunción
    literals = extract_literals(node)
    parsed_literals = []
    for lit_str, negated in literals:
        try:
            if negated:
                parsed = parse_literal("¬" + lit_str)
            else:
                parsed = parse_literal(lit_str)
            parsed_literals.append(parsed)
        except ValueError:
            # Si no se puede parsear, crear un literal simple
            parsed_literals.append(Literal(not negated, lit_str, []))

    return [Clause(parsed_literals)]


def extract_literals(node):
    """Extrae los literales de una disyunción."""
    if isinstance(node, LiteralNode):
        return [(node.literal_str, node.negated)]

    if isinstance(node, NotNode):
        if isinstance(node.child, LiteralNode):
            return [(node.child.literal_str, not node.child.negated)]
        # Negación más compleja
        inner = extract_literals(node.child)
        return [(s, not n) for s, n in inner]

    if isinstance(node, BinaryNode) and node.op == '∨':
        return extract_literals(node.left) + extract_literals(node.right)

    return [(str(node), False)]


# ==================== FUNCIÓN PRINCIPAL ====================

def to_cnf(formula_str):
    """
    Convierte una fórmula en string a Forma Normal Conjuntiva.
    Retorna una lista de objetos Clause.

    Ejemplo:
        to_cnf("∀X(hombre(X) → mortal(X))")
        -> [Clause([Literal(False, "hombre", [X]), Literal(True, "mortal", [X])])]
    """
    steps = []

    # Parsear
    tree = parse_formula(formula_str)
    steps.append(f"Fórmula original: {tree}")

    # Paso 1: Eliminar bicondicionales
    tree = eliminate_biconditional(tree)
    steps.append(f"Sin bicondicionales: {tree}")

    # Paso 2: Eliminar implicaciones
    tree = eliminate_implication(tree)
    steps.append(f"Sin implicaciones: {tree}")

    # Paso 3: Mover negaciones hacia adentro
    tree = move_negation_inward(tree)
    steps.append(f"Negaciones movidas: {tree}")

    # Paso 5: Skolemizar
    tree = skolemize(tree)
    steps.append(f"Skolemizado: {tree}")

    # Paso 6: Quitar cuantificadores universales
    tree = drop_universal_quantifiers(tree)
    steps.append(f"Sin cuantificadores: {tree}")

    # Paso 7: Distribuir ∨ sobre ∧
    tree = distribute_or_over_and(tree)
    steps.append(f"Distribuido: {tree}")

    # Paso 8: Extraer cláusulas
    clauses = extract_clauses(tree)

    return clauses, steps


# ==================== FUNCIÓN SIMPLE PARA CLÁUSULAS DIRECTAS ====================

def parse_clause_string(clause_str):
    """
    Parsea una cláusula directa (sin cuantificadores ni implicaciones).
    Soporta formato: "P(x) ∨ ¬Q(y)" o "P(x), Q(y)" (conjunción implícita).

    Para fórmulas complejas con →, ∀, ∃, usar to_cnf().
    """
    clause_str = clause_str.strip()

    # Si contiene conectivos complejos, usar to_cnf
    if any(c in clause_str for c in ['→', '↔', '∀', '∃']):
        clauses, _ = to_cnf(clause_str)
        return clauses

    # Si contiene ∧, separar en múltiples cláusulas
    if '∧' in clause_str:
        parts = clause_str.split('∧')
        clauses = []
        for part in parts:
            sub_clauses = parse_clause_string(part.strip())
            clauses.extend(sub_clauses)
        return clauses

    # Cláusula simple: separar por ∨
    if '∨' in clause_str:
        literal_strs = [s.strip() for s in clause_str.split('∨')]
    else:
        literal_strs = [clause_str.strip()]

    literals = []
    for ls in literal_strs:
        if ls:
            try:
                literals.append(parse_literal(ls))
            except ValueError as e:
                raise ValueError(f"Error parseando literal '{ls}': {e}")

    return [Clause(literals)]


# ==================== TESTS ====================
if __name__ == "__main__":
    # Test 1: Cláusula simple
    clauses = parse_clause_string("P(X) ∨ ¬Q(a)")
    print(f"✓ Test 1: P(X) ∨ ¬Q(a) -> {clauses}")

    # Test 2: Implicación
    clauses, steps = to_cnf("∀X(hombre(X) → mortal(X))")
    print(f"\n✓ Test 2: ∀X(hombre(X) → mortal(X))")
    for step in steps:
        print(f"  {step}")
    print(f"  Cláusulas: {clauses}")

    # Test 3: Fórmula con ∃
    clauses, steps = to_cnf("∃X(gato(X))")
    print(f"\n✓ Test 3: ∃X(gato(X))")
    for step in steps:
        print(f"  {step}")
    print(f"  Cláusulas: {clauses}")

    print("\n¡Tests de FNC pasaron!")