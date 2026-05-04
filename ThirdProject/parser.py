from classes import VariableAleatoria,RedBayesiana
import re

def parsear_definicion_variable(texto):
    """
    Parsea: A(B,C) -> (D,E,F)  o  A -> (D,E,F)
    Retorna: VariableAleatoria
    """
    texto = texto.strip()
    patron = r'^(\w+)(?:\(([^)]*)\))?\s*->\s*\(([^)]+)\)$'
    m = re.match(patron, texto)
    if not m:
        raise ValueError(
            f"Formato inválido: '{texto}'\n"
            "Usa: NombreVar(Padre1,Padre2) -> (Estado1,Estado2,Estado3)\n"
            "O sin padres: NombreVar -> (Estado1,Estado2)"
        )
    nombre = m.group(1).strip()
    padres_str = m.group(2)
    estados_str = m.group(3)

    padres = [p.strip() for p in padres_str.split(',') if p.strip()] if padres_str else []
    estados = [e.strip() for e in estados_str.split(',') if e.strip()]

    if len(estados) < 2:
        raise ValueError("La variable debe tener al menos 2 estados.")

    return VariableAleatoria(nombre, estados, padres)


def parsear_cpt_texto(texto_cpt, variables):
    """
    Parsea el texto de las CPTs ingresadas por el usuario.
    Formato esperado:
        P(A) = 0.3, 0.7
        P(B|A=si) = 0.9, 0.1
        P(B|A=no) = 0.2, 0.8
        P(C|A=si,B=x) = ...
    """
    cpts = {}
    lineas = [l.strip() for l in texto_cpt.strip().splitlines() if l.strip()]

    for linea in lineas:
        if not linea.startswith('P('):
            continue
        # Separar LHS y RHS
        if '=' not in linea:
            raise ValueError(f"Línea inválida: {linea}")
        idx_eq = linea.rindex('=')
        lhs = linea[:idx_eq].strip()
        rhs = linea[idx_eq + 1:].strip()

        probs = [float(x.strip()) for x in rhs.split(',')]

        # Parsear LHS: P(X) o P(X|A=a,B=b)
        m = re.match(r'^P\((\w+)(?:\|([^)]*))?\)$', lhs)
        if not m:
            raise ValueError(f"Formato inválido en cabecera: {lhs}")

        var_nombre = m.group(1).strip()
        condicion_str = m.group(2)

        if var_nombre not in variables:
            raise ValueError(f"Variable '{var_nombre}' no definida.")

        var = variables[var_nombre]

        if len(probs) != len(var.estados):
            raise ValueError(
                f"La variable '{var_nombre}' tiene {len(var.estados)} estados "
                f"pero se dieron {len(probs)} probabilidades en: {linea}"
            )

        # Construir clave de padres
        if condicion_str:
            partes = [p.strip() for p in condicion_str.split(',')]
            clave = tuple()
            for parte in partes:
                if '=' not in parte:
                    raise ValueError(f"Condición mal formada: {parte}")
                pnombre, pestado = parte.split('=', 1)
                clave += (pestado.strip(),)
        else:
            clave = ()

        if var_nombre not in cpts:
            cpts[var_nombre] = {}

        cpts[var_nombre][clave] = {
            estado: prob for estado, prob in zip(var.estados, probs)
        }

    return cpts