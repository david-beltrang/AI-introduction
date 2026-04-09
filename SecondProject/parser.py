from structures import *
import re

def encontrar_operador_principal(texto, operadores):
    """
    Busca uno de los operadores en el texto que esté en el nivel 0 de paréntesis.
    Devuelve la posición del operador si lo encuentra, o -1 si no.
    """
    nivel = 0
    # Recorremos el texto de izquierda a derecha
    for i in range(len(texto)):
        char = texto[i]
        if char == '(':
            nivel += 1
        elif char == ')':
            nivel -= 1
        elif nivel == 0:
            # Si estamos en el nivel principal, revisamos si el carácter coincide con algún operador
            # Algunos operadores pueden ser de más de un carácter (ej: ->)
            for op in operadores:
                if texto.startswith(op, i):
                    return i, op
    return -1, None

def quitar_parentesis_externos(texto):
    """
    Quita paréntesis externos solo si estan afuera de toda la formula
    """
    texto = texto.strip()
    while texto.startswith('(') and texto.endswith(')'):
        # Verificar si este '(' cierra con el último ')'
        nivel = 0
        balanceado = True
        for i in range(len(texto) - 1):
            char = texto[i]
            if char == '(': 
                nivel += 1
            elif char == ')':
                nivel -= 1
            if nivel == 0: # Se cerró antes del final
                balanceado = False
                break
        if balanceado:
            texto = texto[1:-1].strip()
        else:
            break
    return texto

def parsear(texto):
    texto = texto.strip()
    if not texto:
        return None

    # 1. Quitar paréntesis externos innecesarios
    texto = quitar_parentesis_externos(texto)

    # 2. Buscar operadores de menor a mayor jerarquía (orden inverso)
    # Jerarquía: ↔, →, ∨, ∧
    prioridades = ["↔", "→", "∨", "∧"]
    
    for ops in prioridades:
        pos, op_encontrado = encontrar_operador_principal(texto, ops)
        if pos != -1:
            izq_txt = texto[:pos].strip()
            der_txt = texto[pos + len(op_encontrado):].strip()
            
            izq = parsear(izq_txt)
            der = parsear(der_txt)
            
            if op_encontrado == "↔": return DobleImplica(izq, der)
            if op_encontrado == "→": return Implica(izq, der)
            if op_encontrado == "∨":   return Or(izq, der)
            if op_encontrado == "∧":   return And(izq, der)

    # 3. Manejar operadores unarios (Negación ¬, Cuantificadores ∀, ∃)
    if texto.startswith("¬"):
        return Not(parsear(texto[1:].strip()))
    
    if texto.startswith("∀"):
        match = re.match(r"(∀)\s*([a-zA-Z0-9]+)\s*(.*)", texto)
        if match:
            var_nombre = match.group(2)
            cuerpo = match.group(3)
            return ParaTodo(Term(var_nombre), parsear(cuerpo))

    if texto.startswith("∃"):
        match = re.match(r"(∃)\s*([a-zA-Z0-9]+)\s*(.*)", texto)
        if match:
            var_nombre = match.group(2)
            cuerpo = match.group(3)
            return Existe(Term(var_nombre), parsear(cuerpo))

    # 4. Base: Predicados (ej: P(x, y) o Mortal(Marco))
    match = re.match(r"([a-zA-Z_0-9]+)\s*(\((.*)\))?", texto)
    if match:
        nombre = match.group(1)
        args_txt = match.group(3)
        args = []
        if args_txt:
            # Dividir argumentos por coma (muy simple, asumiendo que no hay funciones anidadas)
            partes = args_txt.split(",")
            args = [Term(p.strip()) for p in partes]
        return Predicado(nombre, args)

    raise ValueError(f"No se pudo parsear la expresión: {texto}")

if __name__ == "__main__":
    # Prueba con paréntesis anidados
    test = "((P(x) ∧ Q(x)) ∨ R(x)) → Mortal(Marco)"
    print(f"Texto: {test}")
    print(f"AST:   {parsear(test)}")