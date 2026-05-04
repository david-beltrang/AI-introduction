class VariableAleatoria:
    def __init__(self, nombre, estados, padres=None):
        self.nombre = nombre
        self.estados = estados          # Lista de strings
        self.padres = padres or []      # Lista de nombres de padres
        self.cpt = {}                   # Tabla de probabilidad condicional

    def __repr__(self):
        p = f"({','.join(self.padres)})" if self.padres else ""
        return f"{self.nombre}{p} -> ({','.join(self.estados)})"


class RedBayesiana:
    def __init__(self):
        self.variables = {}   # nombre -> VariableAleatoria
        self.orden = []       # Orden topológico

    def agregar_variable(self, var: VariableAleatoria):
        self.variables[var.nombre] = var
        if var.nombre not in self.orden:
            self.orden.append(var.nombre)

    def definir_cpt(self, nombre_var, cpt_dict):
        """cpt_dict: {(estado_padre1, estado_padre2, ...): {estado_hijo: prob}}
           Para variables sin padres: {(): {estado: prob}}
        """
        self.variables[nombre_var].cpt = cpt_dict

    def _ordenar_topologicamente(self):
        visitados = set()
        orden = []
        # Los padres quedan añadidos por delante de los hijos
        def dfs(nombre):
            if nombre in visitados:
                return
            visitados.add(nombre)
            for padre in self.variables[nombre].padres:
                dfs(padre)
            orden.append(nombre)

        for n in self.variables:
            dfs(n)
        return orden

    def probabilidad(self, evidencia: dict, consulta: dict) -> float:
        """
        Calcula P(consulta | evidencia) para un estado en particular de la variable consultada.
        consulta: {variable: estado}
        evidencia: {variable: estado}
        """
        orden = self._ordenar_topologicamente()
        # Ver cuales son las variables ocultas
        ocultas = [v for v in orden
                   if v not in consulta and v not in evidencia]
        

        
        def calcular_prob(estado):
            estado.update(evidencia)
            estado.update(consulta)
            print(estado)
            p = 1.0
            for nombre in orden:
                var = self.variables[nombre]
                clave_padres = tuple(estado[padre] for padre in var.padres)
                try:
                    p *= var.cpt[clave_padres][estado[nombre]]
                except KeyError:
                    return 0.0
            return p     
                

        def sumar_ocultas(cubiertas, estado, tot):
            if(cubiertas < len(ocultas)):
                i=ocultas[cubiertas]
                print(i)
                for j in self.variables[i].estados:
                    print(j)
                    if(cubiertas==0):
                        estado={}
                    estado.update({self.variables[i].nombre : j})
                    print(estado)
                    if(cubiertas == len(ocultas)-1):
                        tot += calcular_prob(estado)
                    else:
                        tot += sumar_ocultas(cubiertas+1, estado)
            return tot
        """   
            return prob_conjunta(asig)
            nombre = ocultas[sumadas]
            total = 0.0
            for estado in self.variables[nombre].estados:
                asig[nombre] = estado
                total += sumar_ocultas(sumadas + 1, asig)
            del asig[nombre]
            return total
        """

        prob_sin_ajustar = sumar_ocultas(0,{},0)
        return prob_sin_ajustar

    def distribucion_completa(self, evidencia: dict, var_consulta: str) -> dict:
        """Retorna la distribución P(var_consulta | evidencia) para todos sus estados."""
        resultado = {}
        alfa = 0.0
        resultado_ajustado = {}
        suma_total= 0
        for estado in self.variables[var_consulta].estados:
            resultado[estado] = self.probabilidad(evidencia, {var_consulta: estado})
        for probabilidad in resultado:
            suma_total += resultado[probabilidad]
        alfa=1/suma_total
        for estado in self.variables[var_consulta].estados:
            resultado_ajustado[estado] = resultado[estado]*alfa
        return resultado_ajustado
