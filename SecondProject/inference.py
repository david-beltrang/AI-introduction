"""
Motor de Inferencia por Resolución para Lógica de Predicados de Primer Orden (LPO).

Incluye:
- Unificación de términos (algoritmo de Robinson)
- Aplicación de sustituciones
- Resolución binaria entre cláusulas
- Algoritmo de resolución por refutación
"""

import copy
from structures import Term, Literal, Clause


# =============================================================================
# 1. SUSTITUCIÓN Y APLICACIÓN
# =============================================================================

def apply_substitution_term(term, substitution):
    """Aplica una sustitución {Var -> Term} a un término."""
    if term.is_variable():
        if term.name in substitution:
            # Aplicar recursivamente por si la sustitución apunta a otra variable
            return apply_substitution_term(substitution[term.name], substitution)
        return Term(term.name, [])
    # Si es constante o función, aplicar a los argumentos
    new_args = [apply_substitution_term(arg, substitution) for arg in term.args]
    return Term(term.name, new_args)


def apply_substitution_literal(literal, substitution):
    """Aplica una sustitución a un literal."""
    new_args = [apply_substitution_term(arg, substitution) for arg in literal.args]
    return Literal(literal.positive, literal.predicate, new_args)


def apply_substitution_clause(clause, substitution):
    """Aplica una sustitución a todos los literales de una cláusula."""
    new_literals = [apply_substitution_literal(lit, substitution) for lit in clause.literals]
    return Clause(new_literals)


# =============================================================================
# 2. OCCUR CHECK
# =============================================================================

def occurs_in(var_name, term):
    """Verifica si la variable var_name aparece dentro de term (occur check).
    Evita sustituciones circulares como X -> f(X).
    """
    if term.is_variable():
        return var_name == term.name
    return any(occurs_in(var_name, arg) for arg in term.args)


# =============================================================================
# 3. UNIFICACIÓN (Algoritmo de Robinson)
# =============================================================================

def unify(term1, term2, substitution=None):
    """
    Intenta unificar dos términos. Retorna el unificador más general (MGU)
    o None si no se pueden unificar.
    
    Ejemplos:
        unify(X, a) -> {X: a}
        unify(P(X), P(a)) -> {X: a}
        unify(P(X,Y), P(a,X)) -> {X: a, Y: a}
    """
    if substitution is None:
        substitution = {}

    # Aplicar sustitución actual
    t1 = apply_substitution_term(term1, substitution) if isinstance(term1, Term) else term1
    t2 = apply_substitution_term(term2, substitution) if isinstance(term2, Term) else term2

    # Caso 1: Son iguales
    if t1 == t2:
        return substitution

    # Caso 2: t1 es variable
    if isinstance(t1, Term) and t1.is_variable():
        if occurs_in(t1.name, t2):
            return None  # Occur check falla
        substitution[t1.name] = t2
        return substitution

    # Caso 3: t2 es variable
    if isinstance(t2, Term) and t2.is_variable():
        if occurs_in(t2.name, t1):
            return None  # Occur check falla
        substitution[t2.name] = t1
        return substitution

    # Caso 4: Ambos son funciones/constantes
    if isinstance(t1, Term) and isinstance(t2, Term):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return None  # No se pueden unificar
        for a1, a2 in zip(t1.args, t2.args):
            substitution = unify(a1, a2, substitution)
            if substitution is None:
                return None
        return substitution

    return None


def unify_literals(lit1, lit2, substitution=None):
    """
    Intenta unificar dos literales. Deben tener el mismo predicado
    y la misma cantidad de argumentos.
    Retorna el MGU o None.
    """
    if substitution is None:
        substitution = {}

    if lit1.predicate != lit2.predicate:
        return None
    if len(lit1.args) != len(lit2.args):
        return None

    for a1, a2 in zip(lit1.args, lit2.args):
        substitution = unify(a1, a2, substitution)
        if substitution is None:
            return None
    return substitution


# =============================================================================
# 4. ESTANDARIZACIÓN DE VARIABLES
# =============================================================================

_var_counter = 0

def reset_var_counter():
    global _var_counter
    _var_counter = 0

def get_fresh_var():
    """Genera un nombre de variable fresco único."""
    global _var_counter
    _var_counter += 1
    return f"V{_var_counter}"


def standardize_variables(clause, prefix=None):
    """
    Renombra todas las variables de una cláusula con nombres frescos
    para evitar conflictos al resolver dos cláusulas.
    """
    if prefix is None:
        prefix = get_fresh_var()

    var_map = {}

    def rename_term(term):
        if term.is_variable():
            if term.name not in var_map:
                var_map[term.name] = Term(f"{term.name}_{prefix}")
            return var_map[term.name]
        new_args = [rename_term(arg) for arg in term.args]
        return Term(term.name, new_args)

    new_literals = []
    for lit in clause.literals:
        new_args = [rename_term(arg) for arg in lit.args]
        new_literals.append(Literal(lit.positive, lit.predicate, new_args))

    return Clause(new_literals)


# =============================================================================
# 5. RESOLUCIÓN BINARIA
# =============================================================================

def resolve(clause1, clause2):
    """
    Aplica resolución binaria entre dos cláusulas.
    
    Busca un par de literales complementarios (uno positivo y otro negativo
    con el mismo predicado) entre las dos cláusulas. Si los puede unificar,
    genera la cláusula resolvente.
    
    Retorna una lista de cláusulas resolventes (puede haber más de una
    si hay múltiples pares complementarios).
    """
    # Estandarizar variables para evitar conflictos
    c1 = standardize_variables(copy.deepcopy(clause1))
    c2 = standardize_variables(copy.deepcopy(clause2))

    resolvents = []

    for i, lit1 in enumerate(c1.literals):
        for j, lit2 in enumerate(c2.literals):
            # Buscar literales complementarios (mismo predicado, signo opuesto)
            if lit1.complements(lit2):
                # Intentar unificar
                subst = unify_literals(lit1, lit2.negate())
                if subst is not None:
                    # Construir la resolvente: todos los literales excepto los resueltos
                    remaining1 = [c1.literals[k] for k in range(len(c1.literals)) if k != i]
                    remaining2 = [c2.literals[k] for k in range(len(c2.literals)) if k != j]
                    all_remaining = remaining1 + remaining2

                    # Aplicar la sustitución a todos los literales restantes
                    resolved_literals = [apply_substitution_literal(lit, subst) for lit in all_remaining]

                    # Eliminar duplicados
                    unique_literals = []
                    seen = set()
                    for lit in resolved_literals:
                        key = (lit.positive, lit.predicate, tuple(str(a) for a in lit.args))
                        if key not in seen:
                            seen.add(key)
                            unique_literals.append(lit)

                    resolvents.append(Clause(unique_literals))

    return resolvents


# =============================================================================
# 6. ALGORITMO DE RESOLUCIÓN POR REFUTACIÓN
# =============================================================================

def resolution(clauses, query_clause=None, max_iterations=1000):
    """
    Algoritmo de resolución por refutación.
    
    Para probar que una consulta se sigue de la base de conocimiento:
    1. Se niega la consulta
    2. Se agrega a las cláusulas
    3. Se intenta derivar la cláusula vacía (contradicción)
    
    Si se llega a la cláusula vacía, la consulta es VERDADERA.
    Si no se puede derivar más, la consulta NO se puede probar.
    
    Parámetros:
        clauses: lista de Clause (base de conocimiento en FNC)
        query_clause: Clause con la consulta negada (opcional)
        max_iterations: límite de iteraciones
        
    Retorna:
        (resultado: bool, pasos: lista de strings con la traza)
    """
    reset_var_counter()
    steps = []

    # Copiar las cláusulas de la base de conocimiento
    all_clauses = [copy.deepcopy(c) for c in clauses]

    # Si hay consulta, agregar su negación
    if query_clause is not None:
        negated = negate_clause(query_clause)
        for nc in negated:
            all_clauses.append(nc)
            steps.append(f"Negación de consulta agregada: {nc}")

    steps.append(f"\nBase de conocimiento ({len(all_clauses)} cláusulas):")
    for i, c in enumerate(all_clauses):
        steps.append(f"  C{i+1}: {c}")
    steps.append("")

    # Conjunto de cláusulas ya vistas (para evitar duplicados)
    clause_set = set()
    for c in all_clauses:
        clause_set.add(str(c))

    iteration = 0
    new_clauses_found = True

    while new_clauses_found and iteration < max_iterations:
        iteration += 1
        new_clauses_found = False

        # Intentar resolver cada par de cláusulas
        for i in range(len(all_clauses)):
            for j in range(i + 1, len(all_clauses)):
                resolvents = resolve(all_clauses[i], all_clauses[j])

                for resolvent in resolvents:
                    # ¿Cláusula vacía? ¡Contradicción encontrada!
                    if resolvent.is_empty():
                        steps.append(f"Paso {iteration}: Resolviendo C{i+1} y C{j+1}:")
                        steps.append(f"  {all_clauses[i]}  +  {all_clauses[j]}")
                        steps.append(f"  → □ (CLÁUSULA VACÍA)")
                        steps.append(f"\n✓ CONTRADICCIÓN ENCONTRADA en {iteration} iteraciones.")
                        steps.append("La consulta es VERDADERA (demostrada por refutación).")
                        return True, steps

                    # ¿Es nueva?
                    resolvent_str = str(resolvent)
                    if resolvent_str not in clause_set:
                        clause_set.add(resolvent_str)
                        all_clauses.append(resolvent)
                        new_clauses_found = True
                        steps.append(f"Paso {iteration}: Resolviendo C{i+1} y C{j+1}:")
                        steps.append(f"  {all_clauses[i]}  +  {all_clauses[j]}")
                        steps.append(f"  → C{len(all_clauses)}: {resolvent}")

    steps.append(f"\n✗ No se encontró contradicción después de {iteration} iteraciones.")
    steps.append("La consulta NO se puede demostrar con la base de conocimiento dada.")
    return False, steps


def negate_clause(clause):
    """
    Niega una cláusula para resolución por refutación.
    La negación de (L1 ∨ L2 ∨ ... ∨ Ln) es (¬L1) ∧ (¬L2) ∧ ... ∧ (¬Ln)
    Es decir, retorna una lista de cláusulas unitarias negadas.
    """
    negated_clauses = []
    for lit in clause.literals:
        negated_lit = lit.negate()
        negated_clauses.append(Clause([negated_lit]))
    return negated_clauses


# =============================================================================
# 7. CONVERSIÓN A FORMA NORMAL CONJUNTIVA (FNC)
# =============================================================================

def implication_to_clause(antecedent_literals, consequent_literal):
    """
    Convierte una implicación a forma clausal (FNC).
    
    P(x) ∧ Q(x) → R(x)  se convierte en  ¬P(x) ∨ ¬Q(x) ∨ R(x)
    
    Parámetros:
        antecedent_literals: lista de Literal (las condiciones)
        consequent_literal: Literal (la conclusión)
    
    Retorna: Clause
    """
    negated_antecedents = [lit.negate() for lit in antecedent_literals]
    all_literals = negated_antecedents + [consequent_literal]
    return Clause(all_literals)


def parse_implication(implication_str):
    """
    Parsea una implicación del tipo: P(x) ∧ Q(x) → R(x)
    y la convierte a forma clausal (FNC).
    
    También soporta cláusulas sin implicación (solo disyunciones):
        P(x) ∨ Q(x)
    
    Y hechos simples:
        P(a)
    """
    from parser import parse_literal

    implication_str = implication_str.strip()

    # Caso 1: Tiene implicación →
    if "→" in implication_str:
        parts = implication_str.split("→")
        antecedent_str = parts[0].strip()
        consequent_str = parts[1].strip()

        # Parsear antecedentes (separados por ∧)
        if "∧" in antecedent_str:
            ant_parts = [p.strip() for p in antecedent_str.split("∧")]
        else:
            ant_parts = [antecedent_str]

        antecedent_literals = [parse_literal(p) for p in ant_parts]
        consequent_literal = parse_literal(consequent_str)

        return implication_to_clause(antecedent_literals, consequent_literal)

    # Caso 2: Bicondicional ↔
    elif "↔" in implication_str:
        parts = implication_str.split("↔")
        left_str = parts[0].strip()
        right_str = parts[1].strip()
        left_lit = parse_literal(left_str)
        right_lit = parse_literal(right_str)
        # P ↔ Q equivale a (¬P ∨ Q) ∧ (P ∨ ¬Q), retornamos como lista
        clause1 = Clause([left_lit.negate(), right_lit])
        clause2 = Clause([left_lit, right_lit.negate()])
        return [clause1, clause2]

    # Caso 3: Disyunción (ya está en FNC)
    elif "∨" in implication_str:
        parts = [p.strip() for p in implication_str.split("∨")]
        literals = [parse_literal(p) for p in parts]
        return Clause(literals)

    # Caso 4: Hecho simple (un solo literal = cláusula unitaria)
    else:
        literal = parse_literal(implication_str)
        return Clause([literal])


# =============================================================================
# 8. FUNCIONES DE AYUDA PARA EL FRONTEND
# =============================================================================

def run_inference(clause_strings, query_string=None):
    """
    Función principal para ejecutar inferencia desde el frontend.
    
    Parámetros:
        clause_strings: lista de strings con cláusulas/implicaciones
        query_string: string con la consulta (opcional)
    
    Retorna:
        (resultado: bool, pasos: lista de strings)
    """
    # Parsear todas las cláusulas
    all_clauses = []
    parse_steps = []

    for cs in clause_strings:
        try:
            result = parse_implication(cs)
            if isinstance(result, list):
                # Bicondicional retorna múltiples cláusulas
                for r in result:
                    all_clauses.append(r)
                    parse_steps.append(f"'{cs}' → {r}")
            else:
                all_clauses.append(result)
                parse_steps.append(f"'{cs}' → {result}")
        except Exception as e:
            return False, [f"Error parseando '{cs}': {str(e)}"]

    steps = ["=== CONVERSIÓN A FORMA CLAUSAL (FNC) ==="]
    steps.extend(parse_steps)
    steps.append("")

    # Parsear la consulta si existe
    query = None
    if query_string:
        try:
            query = parse_implication(query_string)
            if isinstance(query, list):
                query = query[0]  # Tomar la primera cláusula del bicondicional
            steps.append(f"Consulta: {query_string} → {query}")
        except Exception as e:
            return False, [f"Error parseando consulta '{query_string}': {str(e)}"]

    steps.append("\n=== RESOLUCIÓN POR REFUTACIÓN ===")

    # Ejecutar resolución
    result, resolution_steps = resolution(all_clauses, query)
    steps.extend(resolution_steps)

    return result, steps


# =============================================================================
# 9. PRUEBAS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PRUEBA 1: Unificación simple")
    print("=" * 60)

    x = Term("X")
    a = Term("a")
    result = unify(x, a)
    print(f"unify(X, a) = {result}")
    assert result == {"X": a}

    x = Term("X")
    y = Term("Y")
    result = unify(x, y)
    print(f"unify(X, Y) = {result}")

    print()
    print("=" * 60)
    print("PRUEBA 2: Resolución simple - Modus Ponens")
    print("=" * 60)
    print("Base: hombre(socrates), hombre(X) → mortal(X)")
    print("Consulta: mortal(socrates)")

    # hombre(socrates) — hecho
    c1 = Clause([Literal(True, "hombre", [Term("socrates")])])
    # hombre(X) → mortal(X)  =>  ¬hombre(X) ∨ mortal(X)
    c2 = Clause([
        Literal(False, "hombre", [Term("X")]),
        Literal(True, "mortal", [Term("X")])
    ])
    # Consulta: mortal(socrates)
    query = Clause([Literal(True, "mortal", [Term("socrates")])])

    result, steps = resolution([c1, c2], query)
    for s in steps:
        print(s)
    print(f"\nResultado: {result}")

    print()
    print("=" * 60)
    print("PRUEBA 3: Usando run_inference con strings")
    print("=" * 60)

    clauses = [
        "hombre(socrates)",
        "hombre(X) → mortal(X)"
    ]
    query = "mortal(socrates)"

    result, steps = run_inference(clauses, query)
    for s in steps:
        print(s)
    print(f"\nResultado: {result}")