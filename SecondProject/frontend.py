import tkinter as tk
from tkinter import messagebox, scrolledtext, Button, Entry, Listbox, Label
from parser import parsear
from cnf_converter import convertir_a_fnc_paso_a_paso
from resolution import extraer_clausulas, resolucion
from structures import Not

class LogicInferenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor de Inferencia en LPO - Resolución")

        # Frame superior para entrada de conocimiento
        kb_frame = tk.LabelFrame(root, text="Base de Conocimiento (Hechos y Reglas)")
        kb_frame.pack(padx=10, pady=5, fill="both", expand=True)

        Label(kb_frame, text="Ingresa una fórmula en LPO:").pack(pady=2)
        self.clause_entry = Entry(kb_frame, width=60)
        self.clause_entry.pack(pady=2)

        # Teclado virtual (ahora dentro del kb_frame)
        self.create_lpo_keyboard(kb_frame, self.clause_entry)

        self.add_button = Button(kb_frame, text="Agregar", command=self.add_clause)
        self.add_button.pack(pady=5)

        Label(kb_frame, text="Cláusulas ingresadas:").pack(pady=2)
        self.clauses_listbox = Listbox(kb_frame, width=70, height=8)
        self.clauses_listbox.pack(pady=5)

        # Frame para la consulta
        query_frame = tk.LabelFrame(root, text="Consulta (Pregunta)")
        query_frame.pack(padx=10, pady=5, fill="both", expand=False)

        Label(query_frame, text="¿Qué quieres probar? (ej: Mortal(Marco))").pack(pady=2)
        self.query_entry = Entry(query_frame, width=60)
        self.query_entry.pack(pady=2)

        self.create_lpo_keyboard(query_frame, self.query_entry)

        self.infer_button = Button(query_frame, text="Probar Inferencia (Refutación)", command=self.execute_inference, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.infer_button.pack(pady=10)

        # Botón para ver FNC (Oculto al inicio)
        self.fnc_steps_button = Button(query_frame, text="Ver Paso a Paso FNC", command=self.show_fnc_steps, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))

        # Área de resultados
        Label(root, text="Proceso de transformación y resultado:").pack(pady=5)
        self.result_text = scrolledtext.ScrolledText(root, width=80, height=12)
        self.result_text.pack(pady=5, padx=10)

        # Lista interna de ASTs de la KB
        self.kb_formulas = []

    def create_lpo_keyboard(self, parent, target_entry):
        """Crea un teclado virtual con símbolos de LPO."""
        keyboard_frame = tk.Frame(parent)
        keyboard_frame.pack(pady=2)

        buttons = [
            ("∀", "∀"), ("∃", "∃"), ("¬", "¬"), ("∧", "∧"),
            ("∨", "∨"), ("→", "→"), ("↔", "↔"), ("(", "("), (")", ")")
        ]

        for text, symbol in buttons:
            button = Button(keyboard_frame, text=text, command=lambda s=symbol, e=target_entry: e.insert(tk.END, s))
            button.pack(side=tk.LEFT, padx=1, pady=1)

    def add_clause(self):
        """Agrega la cláusula ingresada a la KB."""
        texto = self.clause_entry.get()
        if texto:
            try:
                formula_ast = parsear(texto)
                self.kb_formulas.append(formula_ast)
                self.clauses_listbox.insert(tk.END, str(formula_ast))
                self.clause_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Fórmula inválida: {e}")
        else:
            messagebox.showwarning("Aviso", "Ingresa una fórmula primero.")

    def execute_inference(self):
        """Ejecuta el proceso de resolución."""
        query_text = self.query_entry.get()
        if not query_text:
            messagebox.showwarning("Aviso", "Ingresa una consulta para probar.")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"--- INICIANDO INFERENCIA ---\n")
        self.result_text.insert(tk.END, f"Consulta: {query_text}\n\n")

        try:
            # 1. Procesar la consulta y NEGARLA
            query_ast = parsear(query_text)
            negated_query = Not(query_ast)
            self.result_text.insert(tk.END, f"1. Consulta negada para refutación: {negated_query}\n")

            # 2. Convertir TODO a FNC
            all_clauses = []
            
            # Convertir KB
            self.result_text.insert(tk.END, "2. Convirtiendo KB a FNC...\n")
            for f in self.kb_formulas:
                pasos = convertir_a_fnc_paso_a_paso(f)
                finc_f = pasos[-1][1] # El último resultado en texto
                # Necesitamos el AST final para extraer cláusulas
                # Para simplificar, usamos el último paso que devuelve el string y lo re-parseamos
                # o mejor aún, modificamos convertir_a_fnc para que devuelva el objeto final.
                # Como el parser es robusto, re-parseamos el string final de FNC.
                f_fnc_ast = parsear(finc_f)
                all_clauses.extend(extraer_clausulas(f_fnc_ast))
            
            # Convertir consulta negada
            pasos_q = convertir_a_fnc_paso_a_paso(negated_query)
            q_fnc_str = pasos_q[-1][1]
            q_fnc_ast = parsear(q_fnc_str)
            all_clauses.extend(extraer_clausulas(q_fnc_ast))

            self.result_text.insert(tk.END, f"3. Conjunto de cláusulas resultante ({len(all_clauses)}):\n")
            for i, c in enumerate(all_clauses):
                self.result_text.insert(tk.END, f"   C{i+1}: {c}\n")

            # 3. Ejecutar algoritmo de Resolución
            self.result_text.insert(tk.END, "\n4. Ejecutando algoritmo de Resolución...\n")
            resultado = resolucion(all_clauses)

            if resultado:
                self.result_text.insert(tk.END, "\n¡ÉXITO! Se encontró la cláusula vacía.\n")
                self.result_text.insert(tk.END, "RESULTADO: La consulta es VERDADERA (por refutación).")
                messagebox.showinfo("Inferencia", "Resultado: VERDADERO")
            else:
                self.result_text.insert(tk.END, "\nNo se pudo encontrar una contradicción.\n")
                self.result_text.insert(tk.END, "RESULTADO: La consulta NO se puede demostrar (Falso o Insuficiente).")
                messagebox.showinfo("Inferencia", "Resultado: FALSO / NO PROBABLE")

            # Guardar consultas para la ventana de FNC y mostrar el botón
            self.last_query_ast = query_ast
            self.last_negated_query = negated_query
            self.fnc_steps_button.pack(pady=5)

        except Exception as e:
            self.result_text.insert(tk.END, f"\nERROR durante el proceso: {e}")
            messagebox.showerror("Error", str(e))

    def show_fnc_steps(self):
        """Abre una ventana mostrando los pasos a FNC para la KB y la consulta."""
        if not self.kb_formulas:
            messagebox.showwarning("Aviso", "No hay fórmulas en la Base de Conocimiento.")
            return

        try:
            ventana_fnc = tk.Toplevel(self.root)
            ventana_fnc.title("Conversión a FNC - Paso a Paso")
            ventana_fnc.geometry("700x500")

            Label(ventana_fnc, text="Proceso de transformación a FNC:", font=("Arial", 12, "bold")).pack(pady=10)
            
            txt_area = scrolledtext.ScrolledText(ventana_fnc, width=80, height=25)
            txt_area.pack(padx=10, pady=10, fill="both", expand=True)

            txt_area.insert(tk.END, "=== BASE DE CONOCIMIENTO (HECHOS Y REGLAS) ===\n\n")
            for i, formula in enumerate(self.kb_formulas):
                txt_area.insert(tk.END, f"--- Fórmula {i+1} ---\n")
                pasos = convertir_a_fnc_paso_a_paso(formula)
                for nombre_paso, formula_str in pasos:
                    txt_area.insert(tk.END, f"[{nombre_paso}]:\n  {formula_str}\n\n")

            # Mostrar pasos de la consulta negada
            if hasattr(self, 'last_negated_query') and self.last_negated_query:
                txt_area.insert(tk.END, "=== CONSULTA (PREPARACIÓN PARA RESOLUCIÓN) ===\n\n")
                txt_area.insert(tk.END, f"[Consulta Original]:\n  {self.last_query_ast}\n\n")
                txt_area.insert(tk.END, f"[Consulta Negada (Esta es la que se pasa a FNC)]:\n  {self.last_negated_query}\n\n")
                
                txt_area.insert(tk.END, "--- Transformación a FNC de la Consulta Negada ---\n")
                pasos_q = convertir_a_fnc_paso_a_paso(self.last_negated_query)
                for nombre_paso, formula_str in pasos_q:
                    txt_area.insert(tk.END, f"[{nombre_paso}]:\n  {formula_str}\n\n")

            txt_area.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar los pasos: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogicInferenceGUI(root)
    root.mainloop()