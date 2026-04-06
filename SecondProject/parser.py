import re
from structures import *

def parse_literal(literal_str):
    positive = not literal_str.startswith("¬")
    predicate_part = literal_str[1:] if not positive else literal_str

    #con dos arguments
    match = re.match(r"([a-zA-Z_0-9\-]+)\(\s*([a-zA-Z_0-9\-]+)\s*,\s*([a-zA-Z_0-9\-]+)\s*\)", predicate_part)
    if match:
        predicate = match.group(1)
        arg1 = match.group(2)
        arg2 = match.group(3)
        args = [Term(arg1), Term(arg2)]
    else:
        # Si no hay dos argumentos, probar con un solo argumento
        match = re.match(r"([a-zA-Z_0-9\-]+)\(\s*([a-zA-Z_0-9\-]+)\s*\)", predicate_part)
        if match:
            predicate = match.group(1)
            arg1 = match.group(2)
            args = [Term(arg1)]
        else:
            # Si no hay paréntesis, es un predicado sin argumentos
            match = re.match(r"([a-zA-Z_0-9\-]+)", predicate_part)
            if match:
                predicate = match.group(1)
                args = []
            else:
                raise ValueError(f"Literal inválido: {literal_str}")

    return Literal(positive, predicate, args)


assert str(parse_literal("P(x,y)")) == "P(x, y)"
assert str(parse_literal("P(x ,y)")) == "P(x, y)"
assert str(parse_literal("P(x, y)")) == "P(x, y)"
assert str(parse_literal("P( x, y )")) == "P(x, y)"
assert str(parse_literal("P(x)")) == "P(x)"
assert str(parse_literal("P")) == "P"
assert str(parse_literal("¬Q(a,b)")) == "¬Q(a, b)"

print("Tests passed")