from structures import *

def extraer_clausulas(formula):
    if isinstance(formula, And):
        return extraer_clausulas(formula.izquierda) + extraer_clausulas(formula.derecha)
    else:
        return [Clause(extraer_literales(formula))]

def extraer_literales(formula):
    if isinstance(formula, Or):
        return extraer_literales(formula.izquierda) + extraer_literales(formula.derecha)

    if isinstance(formula, Not):
        f = formula.formula
        return [Literal(False, f.nombre, f.argumentos)]

    if isinstance(formula, Predicado):
        return [Literal(True, formula.nombre, formula.argumentos)]

    return []

def es_variable(term):
    """Consideramos variable a un término sin argumentos que empieza con minúscula."""
    if isinstance(term, Term):
        if not term.args and term.name[0].islower():
            return True
    return False

def unificar(x, y, subs=None):
    if subs is None:
        subs = {}

    if x == y:
        return subs

    # Si x y y son términos iguales
    if isinstance(x, Term) and isinstance(y, Term) and x.name == y.name and x.args == y.args:
        return subs

    if es_variable(x):
        return unificar_var(x, y, subs)

    if es_variable(y):
        return unificar_var(y, x, subs)

    if isinstance(x, Term) and isinstance(y, Term):
        # Mismo nombre de función/predicado, intentamos unificar argumentos
        if x.name == y.name:
            return unificar(x.args, y.args, subs)
        else:
            return None # Diferentes constantes o funciones

    if isinstance(x, list) and isinstance(y, list):
        if len(x) != len(y):
            return None
        for xi, yi in zip(x, y):
            subs = unificar(xi, yi, subs)
            if subs is None:
                return None
        return subs

    return None

def occurs_check(var, term):
    """Verifica si la variable 'var' ocurre dentro del término 'term' para evitar recursión infinita."""
    if not isinstance(term, Term):
        return False
    if var.name == term.name:
        return True
    for arg in term.args:
        if occurs_check(var, arg):
            return True
    return False

def unificar_var(var, x, subs):
    if var.name in subs:
        return unificar(subs[var.name], x, subs)

    if isinstance(x, Term) and x.name in subs:
        return unificar(var, subs[x.name], subs)

    # Occurs check: evitar x = f(x) que causa stack overflow
    if isinstance(x, Term) and occurs_check(var, x):
        return None

    subs[var.name] = x
    return subs

def aplicar_subs(term, subs):
    if isinstance(term, Term):
        if term.name in subs:
            # Reemplazar la variable recursivamente si la sustitución resultante también tiene variables mapadas
            return aplicar_subs(subs[term.name], subs)
        
        # Si tiene argumentos (es una función/Skolem), aplicar sustitución a los argumentos
        nuevos_args = [aplicar_subs(arg, subs) for arg in term.args]
        return Term(term.name, nuevos_args)
    return term


def aplicar_subs_literal(literal, subs):
    nuevos_args = [aplicar_subs(arg, subs) for arg in literal.args]
    return Literal(literal.positive, literal.predicate, nuevos_args)


def resolver(c1, c2):
    resolventes = []

    for l1 in c1.literals:
        for l2 in c2.literals:
            if l1.predicate == l2.predicate and l1.positive != l2.positive:

                subs = unificar(l1.args, l2.args, {})
                if subs is not None:

                    nuevos_lits = []

                    for l in c1.literals:
                        if l != l1:
                            nuevos_lits.append(aplicar_subs_literal(l, subs))

                    for l in c2.literals:
                        if l != l2:
                            nuevos_lits.append(aplicar_subs_literal(l, subs))

                    resolventes.append(Clause(nuevos_lits))

    return resolventes

def resolucion(clausulas):
    # Optimización: Convertimos a conjunto de strings para búsqueda O(1) de duplicados
    clausulas_vistas = set(str(c) for c in clausulas)
    
    # Límite de seguridad
    max_iteraciones = 15
    max_clausulas_totales = 800
    iter_actual = 0

    while iter_actual < max_iteraciones:
        iter_actual += 1
        nuevos_resolventes = []

        # Unit Preference: Ordenamos las cláusulas de menor a mayor longitud
        # para resolver primero hechos y cláusulas unitarias.
        clausulas.sort(key=lambda c: len(c.literals))

        pares = [(clausulas[i], clausulas[j])
                 for i in range(len(clausulas))
                 for j in range(i+1, len(clausulas))]

        for (c1, c2) in pares:
            # Poda heurística simple: evitamos combinar dos cláusulas masivas entre sí
            if len(c1.literals) > 3 and len(c2.literals) > 3:
                continue

            resolventes = resolver(c1, c2)

            for r in resolventes:
                if len(r.literals) == 0:
                    return True # ¡Contradicción encontrada!

                r_str = str(r)
                if r_str not in clausulas_vistas:
                    clausulas_vistas.add(r_str)
                    nuevos_resolventes.append(r)
                    
                    # Cortacircuitos si el espacio de búsqueda explota
                    if len(clausulas_vistas) > max_clausulas_totales:
                        return False

        if not nuevos_resolventes:
            return False

        clausulas.extend(nuevos_resolventes)