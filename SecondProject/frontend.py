import tkinter as tk
from tkinter import messagebox, scrolledtext, Button, Entry, Listbox, Label
from inference import run_inference


class LogicInferenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor de Inferencia en LPO")

        # Campo de texto para ingresar cláusulas
        Label(root, text="Ingresa una cláusula en LPO:").pack(pady=5)
        self.clause_entry = Entry(root, width=50)
        self.clause_entry.pack(pady=5)
        self.clause_entry.bind("<Return>", lambda e: self.add_clause())

        # Teclado virtual para LPO
        self.create_lpo_keyboard()

        # Botón para agregar cláusulas
        self.add_button = Button(root, text="Agregar", command=self.add_clause)
        self.add_button.pack(pady=5)

        # Lista de cláusulas ingresadas
        Label(root, text="Cláusulas ingresadas:").pack(pady=5)
        self.clauses_listbox = Listbox(root, width=50, height=10)
        self.clauses_listbox.pack(pady=5)

        # Campo de consulta
        Label(root, text="Consulta :").pack(pady=5)
        self.query_entry = Entry(root, width=50)
        self.query_entry.pack(pady=5)

        # Botón para ejecutar inferencia
        self.execute_button = Button(root, text="Ejecutar Inferencia", command=self.execute_inference)
        self.execute_button.pack(pady=5)

        # Área de resultados
        Label(root, text="Resultado:").pack(pady=5)
        self.result_text = scrolledtext.ScrolledText(root, width=50, height=10)
        self.result_text.pack(pady=5)

        # Lista interna para almacenar cláusulas
        self.clauses = []

    def create_lpo_keyboard(self):
        """Crea un teclado virtual con símbolos de LPO."""
        keyboard_frame = tk.Frame(self.root)
        keyboard_frame.pack(pady=5)

        # Botones del teclado LPO
        buttons = [
            ("∀", "∀"), ("∃", "∃"), ("¬", "¬"), ("∧", "∧"),
            ("∨", "∨"), ("→", "→"), ("↔", "↔"), ("(", "("), (")", ")")
        ]

        for text, symbol in buttons:
            button = Button(keyboard_frame, text=text, command=lambda s=symbol: self.insert_symbol(s))
            button.pack(side=tk.LEFT, padx=2, pady=2)

    def insert_symbol(self, symbol):
        """Inserta un símbolo de LPO en el campo de texto."""
        focused = self.root.focus_get()
        if focused == self.query_entry:
            self.query_entry.insert(tk.END, symbol)
        else:
            self.clause_entry.insert(tk.END, symbol)

    def add_clause(self):
        """Agrega la cláusula ingresada a la lista."""
        clause = self.clause_entry.get().strip()
        if clause:
            self.clauses.append(clause)
            self.clauses_listbox.insert(tk.END, clause)
            self.clause_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Advertencia", "Ingresa una cláusula válida.")

    def execute_inference(self):
        """Ejecuta el motor de inferencia con las cláusulas ingresadas."""
        if not self.clauses:
            messagebox.showwarning("Advertencia", "No hay cláusulas para ejecutar.")
            return

        self.result_text.delete(1.0, tk.END)

        query = self.query_entry.get().strip()
        query = query if query else None

        try:
            result, steps = run_inference(self.clauses, query)

            for step in steps:
                self.result_text.insert(tk.END, step + "\n")

            self.result_text.insert(tk.END, "\n" + "=" * 50 + "\n")
            if query:
                if result:
                    self.result_text.insert(tk.END, f"RESULTADO: '{query}' es VERDADERO\n")
                else:
                    self.result_text.insert(tk.END, f"RESULTADO: '{query}' NO se puede demostrar\n")
            else:
                self.result_text.insert(tk.END, "Resolución completada.\n")

        except Exception as e:
            self.result_text.insert(tk.END, f"ERROR: {str(e)}\n")
            import traceback
            self.result_text.insert(tk.END, traceback.format_exc())

        self.result_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicInferenceGUI(root)
    root.mainloop()