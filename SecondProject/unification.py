"""
Módulo de Unificación para Lógica de Predicados de Primer Orden.

Implementa el algoritmo de unificación de Robinson:
- Encuentra la sustitución más general (MGU) que hace dos literales idénticos.
- Maneja variables, constantes y funciones.
"""

import copy
from structures import Term, Literal


def occurs_check(var, term):
    """
    Verifica si la variable 'var' aparece dentro de 'term'.
    Esto evita sustituciones circulares como X = f(X).
    """
    if isinstance(term, Term):
        if term == var:
            return True
        for arg in term.args:
            if occurs_check(var, arg):
                return True
    return False


def apply_substitution_to_term(term, substitution):
    """
    Aplica una sustitución {Variable -> Término} a un término.
    Ejemplo: aplicar {X: a} a f(X, Y) da f(a, Y).
    """
    if not isinstance(term, Term):
        return term

    # Si es una variable y está en la sustitución, reemplazar
    if term.is_variable() and term.name in substitution:
        return apply_substitution_to_term(substitution[term.name], substitution)

    # Si tiene argumentos (es función), aplicar recursivamente
    if term.args:
        new_args = [apply_substitution_to_term(arg, substitution) for arg in term.args]
        return Term(term.name, new_args)

    return copy.deepcopy(term)


def apply_substitution_to_literal(literal, substitution):
    """
    Aplica una sustitución a todos los argumentos de un literal.
    """
    new_args = [apply_substitution_to_term(arg, substitution) for arg in literal.args]
    return Literal(literal.positive, literal.predicate, new_args)


def apply_substitution_to_clause(clause, substitution):
    """
    Aplica una sustitución a todos los literales de una cláusula.
    """
    from structures import Clause
    new_literals = [apply_substitution_to_literal(lit, substitution) for lit in clause.literals]
    return Clause(new_literals)


def unify_terms(term1, term2, substitution=None):
    """
    Algoritmo de unificación de Robinson para dos términos.
    Retorna la sustitución más general (MGU) o None si no se pueden unificar.

    Ejemplos:
        unify_terms(X, a) -> {X: a}
        unify_terms(f(X), f(a)) -> {X: a}
        unify_terms(a, b) -> None (constantes distintas)
    """
    if substitution is None:
        substitution = {}

    # Aplicar sustituciones existentes
    t1 = apply_substitution_to_term(term1, substitution)
    t2 = apply_substitution_to_term(term2, substitution)

    # Si son iguales, ya están unificados
    if t1 == t2:
        return substitution

    # Si t1 es variable
    if isinstance(t1, Term) and t1.is_variable():
        if occurs_check(t1, t2):
            return None  # Fallo: sustitución circular
        substitution[t1.name] = t2
        return substitution

    # Si t2 es variable
    if isinstance(t2, Term) and t2.is_variable():
        if occurs_check(t2, t1):
            return None
        substitution[t2.name] = t1
        return substitution

    # Si ambos son funciones/constantes
    if isinstance(t1, Term) and isinstance(t2, Term):
        if t1.name != t2.name:
            return None  # Nombres distintos
        if len(t1.args) != len(t2.args):
            return None  # Aridad distinta

        # Unificar argumento por argumento
        for a1, a2 in zip(t1.args, t2.args):
            substitution = unify_terms(a1, a2, substitution)
            if substitution is None:
                return None

        return substitution

    return None


def unify_literals(lit1, lit2):
    """
    Intenta unificar dos literales.
    Solo unifica si tienen el mismo predicado y la misma aridad.
    NO verifica el signo (eso lo hace el resolvente).

    Retorna la MGU o None.
    """
    if lit1.predicate != lit2.predicate:
        return None
    if len(lit1.args) != len(lit2.args):
        return None

    substitution = {}
    for a1, a2 in zip(lit1.args, lit2.args):
        substitution = unify_terms(a1, a2, substitution)
        if substitution is None:
            return None

    return substitution


# ==================== TESTS ====================
if __name__ == "__main__":
    # Test 1: Unificar variable con constante
    x = Term("X")
    a = Term("a")
    result = unify_terms(x, a)
    assert result == {"X": a}, f"Test 1 falló: {result}"
    print("✓ Test 1: X unifica con a ->", result)

    # Test 2: Unificar dos constantes iguales
    result = unify_terms(Term("a"), Term("a"))
    assert result == {}, f"Test 2 falló: {result}"
    print("✓ Test 2: a unifica con a ->", result)

    # Test 3: Dos constantes distintas NO unifican
    result = unify_terms(Term("a"), Term("b"))
    assert result is None, f"Test 3 falló: {result}"
    print("✓ Test 3: a NO unifica con b -> None")

    # Test 4: Unificar literales P(X) y P(a)
    l1 = Literal(True, "P", [Term("X")])
    l2 = Literal(True, "P", [Term("a")])
    result = unify_literals(l1, l2)
    assert result == {"X": Term("a")}, f"Test 4 falló: {result}"
    print("✓ Test 4: P(X) unifica con P(a) ->", result)

    # Test 5: Unificar literales P(X,Y) y P(a,b)
    l1 = Literal(True, "P", [Term("X"), Term("Y")])
    l2 = Literal(True, "P", [Term("a"), Term("b")])
    result = unify_literals(l1, l2)
    assert result == {"X": Term("a"), "Y": Term("b")}, f"Test 5 falló: {result}"
    print("✓ Test 5: P(X,Y) unifica con P(a,b) ->", result)

    # Test 6: Predicados distintos NO unifican
    l1 = Literal(True, "P", [Term("X")])
    l2 = Literal(True, "Q", [Term("a")])
    result = unify_literals(l1, l2)
    assert result is None, f"Test 6 falló: {result}"
    print("✓ Test 6: P(X) NO unifica con Q(a) -> None")

    print("\n¡Todos los tests de unificación pasaron!")