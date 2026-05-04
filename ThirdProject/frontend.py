import tkinter as tk
from tkinter import messagebox, scrolledtext, Button, Entry, Listbox, Label
from itertools import product
import re
from classes import VariableAleatoria,RedBayesiana
from parser import parsear_definicion_variable,parsear_cpt_texto

class BayesianNetworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor de Inferencia — Red Bayesiana")
        self.root.resizable(True, True)

        self.variables_definidas = {}
        self.red = RedBayesiana()

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root)
        header.pack(fill="x", padx=20, pady=(18, 4))
        tk.Label(
            header, text="RED BAYESIANA — MOTOR DE INFERENCIA", font=("Courier New", 14, "bold")
        ).pack(side="left")
        
        sep = tk.Frame(self.root, height=1)
        sep.pack(fill="x", padx=20, pady=4)

        # Contenedor principal con scroll horizontal implícito
        main = tk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=8)

        # ── PANEL 1: Variables ──────────────────────────────────────────────
        self._panel_variables(main)

        # ── PANEL 2: Probabilidades ─────────────────────────────────────────
        self._panel_probabilidades(main)

        # ── PANEL 3: Consulta + Resultado ───────────────────────────────────
        self._panel_consulta(main)

    def _make_panel(self, parent, title, row, col, rowspan=1, colspan=1):
        frame = tk.LabelFrame(
            parent, text=f"  {title}  ",
            bd=1, relief="solid",
            labelanchor="nw"
        )
        frame.grid(row=row, column=col, rowspan=rowspan, columnspan=colspan,
                   padx=6, pady=6, sticky="nsew")
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        return frame

    def _panel_variables(self, main):
        panel = self._make_panel(main, "DEFINICIÓN DE VARIABLES", 0, 0)
        Label(
            panel,
            text="Formato:  NomVar(Padre1,Padre2) -> (Est1,Est2,Est3)\n"
            "Sin padres:  NomVar -> (Est1,Est2)",
        ).pack(anchor="w", padx=10, pady=(8, 2))

        self.var_entry = tk.Entry(
            panel, width=52,
            relief="flat", bd=6
        )
        self.var_entry.pack(padx=10, pady=4, fill="x")
        self.var_entry.bind("<Return>", lambda e: self._agregar_variable())

        btn_row = tk.Frame(panel)
        btn_row.pack(padx=10, pady=2, fill="x")
        Button(btn_row, text="Agregar Variable", command=self._agregar_variable).pack(side="left")
        Button(btn_row, text="Limpiar Todo", command=self._limpiar_todo).pack(side="left", padx=8)

        Label(panel,  text="Variables en la red:").pack(
            anchor="w", padx=10, pady=(8, 2))

        list_frame = tk.Frame(panel)
        list_frame.pack(fill="both", expand=True, padx=10, pady=4)

        self.var_listbox = tk.Listbox(
            list_frame, selectforeground="white", relief="flat", bd=0,
            activestyle="none", height=7
        )
        self.var_listbox.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(list_frame, orient="vertical",
                           command=self.var_listbox.yview)
        sb.pack(side="right", fill="y")
        self.var_listbox.configure(yscrollcommand=sb.set)

        # Generador de plantilla CPT
        Button(
            panel, text="Generar Plantilla de Probabilidades",
            command=self._generar_plantilla_cpt
        ).pack(padx=10, pady=(4, 10))

    def _panel_probabilidades(self, main):
        panel = self._make_panel(main, "TABLAS DE PROBABILIDAD (CPT)", 0, 1)

        self.cpt_text = scrolledtext.ScrolledText(
            panel, width=40, height=14, relief="flat", bd=6
        )
        self.cpt_text.pack(padx=10, pady=4, fill="both", expand=True)

        Button(
            panel, text="Cargar Probabilidades", command=self._cargar_probabilidades,
        ).pack(padx=10, pady=(0, 10))

        self.cpt_status = Label(panel, text="")
        self.cpt_status.pack(anchor="w", padx=10, pady=(0, 6))

    def _panel_consulta(self, main):
        main.grid_rowconfigure(1, weight=1)
        panel = self._make_panel(main, "CONSULTA E INFERENCIA", 1, 0, colspan=2)

        top = tk.Frame(panel)
        top.pack(fill="x", padx=10, pady=8)
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=1)

        # Columna izquierda: variable a consultar
        izq = tk.Frame(top)
        izq.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        Label(izq,  text="Variable a consultar:").pack(anchor="w")
        self.consulta_entry = tk.Entry(
            izq, width=30, relief="flat", bd=6
        )
        self.consulta_entry.pack(fill="x", pady=2)
        Label(izq,  text="Ej: A").pack(anchor="w")

        # Columna derecha: evidencia
        der = tk.Frame(top)
        der.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        Label(der,  text="Evidencia (opcional):").pack(anchor="w")
        self.evidencia_entry = tk.Entry(
            der, width=40, relief="flat", bd=6
        )
        self.evidencia_entry.pack(fill="x", pady=2)
        Label(
            der,  text="Ej: B=si, C=no"
        ).pack(anchor="w")

        btn_infer = Button(
            panel, text="EJECUTAR INFERENCIA", command=self._ejecutar_inferencia
        )
        btn_infer.pack(pady=6)

        sep2 = tk.Frame(panel, height=1)
        sep2.pack(fill="x", padx=10, pady=4)

        Label(panel,  text="Resultado de la inferencia:").pack(
            anchor="w", padx=10)

        self.result_text = scrolledtext.ScrolledText(
            panel, width=80, height=10,
            relief="flat", bd=6
        )
        self.result_text.pack(padx=10, pady=(4, 10), fill="both", expand=True)

    # ── LÓGICA DE VARIABLES ─────────────────────────────────────────────────

    def _agregar_variable(self):
        texto = self.var_entry.get().strip()
        if not texto:
            messagebox.showwarning("Aviso", "Ingresa la definición de la variable.")
            return
        try:
            var = parsear_definicion_variable(texto)
            if var.nombre in self.variables_definidas:
                messagebox.showwarning(
                    "Aviso", f"La variable '{var.nombre}' ya fue definida.")
                return
            # Validar que los padres existan
            for padre in var.padres:
                if padre not in self.variables_definidas:
                    raise ValueError(
                        f"El padre '{padre}' no está definido aún.\n"
                        "Define primero las variables padre.")

            self.variables_definidas[var.nombre] = var
            self.red.agregar_variable(var)
            self.var_listbox.insert(
                tk.END, f"  {var}  ")
            self.var_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Error de formato", str(e))

    def _limpiar_todo(self):
        if not messagebox.askyesno("Confirmar", "¿Eliminar todas las variables y datos?"):
            return
        self.variables_definidas.clear()
        self.red = RedBayesiana()
        self.var_listbox.delete(0, tk.END)
        self.cpt_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.cpt_status.config(text="")

    # ── GENERADOR DE PLANTILLA ──────────────────────────────────────────────

    def _generar_plantilla_cpt(self):
        if not self.variables_definidas:
            messagebox.showwarning("Aviso", "Primero agrega variables a la red.")
            return

        plantilla = ""
        for nombre, var in self.variables_definidas.items():
            if not var.padres:
                plantilla += f"P({nombre}) = " + ", ".join(
                    ["0.0"] * len(var.estados)) + "\n"
            else:
                estados_padres = [
                    self.variables_definidas[p].estados for p in var.padres
                ]
                for combo in product(*estados_padres):
                    cond = ",".join(
                        f"{p}={e}" for p, e in zip(var.padres, combo))
                    plantilla += f"P({nombre}|{cond}) = " + ", ".join(
                        ["0.0"] * len(var.estados)) + "\n"
            plantilla += "\n"

        self.cpt_text.delete(1.0, tk.END)
        self.cpt_text.insert(tk.END, plantilla.strip())
        self.cpt_status.config(
            text="Plantilla generada — reemplaza los 0.0 con tus probabilidades.")

    def _cargar_probabilidades(self):
        texto = self.cpt_text.get(1.0, tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Ingresa las tablas de probabilidad.")
            return
        if not self.variables_definidas:
            messagebox.showwarning("Aviso", "Primero define las variables.")
            return
        try:
            cpts = parsear_cpt_texto(texto, self.variables_definidas)
            for nombre, cpt in cpts.items():
                self.red.definir_cpt(nombre, cpt)

        except Exception as e:
            self.cpt_status.config(text=f"Error: {e}")
            messagebox.showerror("Error en CPT", str(e))

    def _ejecutar_inferencia(self):
        var_consulta = self.consulta_entry.get().strip()
        evidencia_txt = self.evidencia_entry.get().strip()
 
        if not var_consulta:
            messagebox.showwarning("Aviso", "Ingresa la variable a consultar.")
            return
        if var_consulta not in self.variables_definidas:
            messagebox.showerror(
                "Error", f"La variable '{var_consulta}' no está definida.")
            return
 
        # Parsear evidencia
        evidencia = {}
        if evidencia_txt:
            try:
                partes = [p.strip() for p in evidencia_txt.split(',')]
                for parte in partes:
                    if '=' not in parte:
                        raise ValueError(f"Formato inválido: '{parte}'. Usa Var=estado.")
                    vnombre, vestado = parte.split('=', 1)
                    vnombre = vnombre.strip()
                    vestado = vestado.strip()
                    if vnombre not in self.variables_definidas:
                        raise ValueError(f"Variable de evidencia '{vnombre}' no definida.")
                    if vestado not in self.variables_definidas[vnombre].estados:
                        raise ValueError(
                            f"Estado '{vestado}' no existe para '{vnombre}'.\n"
                            f"Estados válidos: {', '.join(self.variables_definidas[vnombre].estados)}")
                    evidencia[vnombre] = vestado
            except ValueError as e:
                messagebox.showerror("Error en evidencia", str(e))
                return
 
        # Verificar que las CPTs estén cargadas
        for nombre, var in self.variables_definidas.items():
            if not var.cpt:
                messagebox.showerror(
                    "Falta CPT",
                    f"La variable '{nombre}' no tiene probabilidades cargadas.\n"
                    "Usa 'Generar Plantilla', completa los valores y carga.")
                return
 
        # Ejecutar
        self.result_text.delete(1.0, tk.END)
        self._log("═" * 60 + "\n", "dim")
        self._log("  INFERENCIA POR ENUMERACIÓN — RED BAYESIANA\n", "header")
        self._log("═" * 60 + "\n", "dim")
 
        consulta_str = f"P({var_consulta}"
        if evidencia:
            ev_str = ", ".join(f"{k}={v}" for k, v in evidencia.items())
            consulta_str += f" | {ev_str}"
            self._log(f"\n  Evidencia:   {ev_str}\n", "warn")
        consulta_str += ")"
        self._log(f"  Consulta:    {consulta_str}\n\n", "var")
 
        try:
            distribucion = self.red.distribucion_completa(evidencia, var_consulta)
            total = sum(distribucion.values())
 
            self._log("  Distribución de probabilidad:\n", "dim")
            self._log("  " + "─" * 36 + "\n", "dim")
 
            for estado, prob in distribucion.items():
                self._log(
                    f"  {var_consulta} = {estado:<10}", "var")
                self._log(f"{prob * 100:6.2f}%\n", "prob")
 
            self._log("  " + "─" * 36 + "\n", "dim")
            self._log(f"  Suma total: {total:.4f}", "dim")
 
            if abs(total - 1.0) > 0.001:
                self._log(
                    f"La suma no es 1.0 — revisa las probabilidades.\n",
                    "error")
            else:
                self._log("\n", "prob")
 
            # Estado más probable
            mas_probable = max(distribucion, key=distribucion.get)
            self._log(
                f"\n  Estado más probable: {var_consulta} = {mas_probable} "
                f"({distribucion[mas_probable] * 100:.2f}%)\n",
                "header"
            )
            self._log("\n" + "═" * 60 + "\n", "dim")
 
        except Exception as e:
            self._log(f"\n  ERROR: {e}\n", "error")
            messagebox.showerror("Error en inferencia", str(e))
            
    def _log(self, texto, tag=None):
        if tag:
            self.result_text.insert(tk.END, texto, tag)
        else:
            self.result_text.insert(tk.END, texto)
        self.result_text.see(tk.END)
 

if __name__ == "__main__":
    root = tk.Tk()
    app = BayesianNetworkGUI(root)
    root.mainloop()