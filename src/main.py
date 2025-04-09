import os
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading

def list_available_scripts(directory="./src/utils"):
    """
    Lista os scripts Python disponíveis no diretório especificado.
    """
    scripts = {}
    try:
        # Lista todos os arquivos no diretório e filtra os .py
        files = [f for f in os.listdir(directory) if f.endswith(".py")]
        for i, file in enumerate(files, start=1):
            scripts[i] = os.path.join(directory, file)  # Mapeia o número ao caminho do arquivo
        # Se o ficheiro for o "file_reader.py", remove-o da lista
        if "file_reader.py" in scripts.values():
            scripts.pop(list(scripts.keys())[list(scripts.values()).index("file_reader.py")])

    except FileNotFoundError:
        messagebox.showerror("Erro", f"O diretório {directory} não foi encontrado.")

    return scripts

def execute_script_in_thread(script_path, output_callback):
    """
    Executa o script Python em um thread e redireciona a saída para o callback.
    """
    def run_script():
        try:
            # Rodando o script no subprocesso e capturando a saída
            process = subprocess.Popen(
                ['python3', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Lê a saída do script em tempo real
            for line in process.stdout:
                output_callback(line)  # Passa cada linha de saída para o callback
            for line in process.stderr:
                output_callback(f"Erro: {line}")  # Passa os erros para o callback
            process.wait()  # Espera o processo terminar

        except Exception as e:
            output_callback(f"Erro ao executar o script: {str(e)}")

    # Inicia a execução em uma thread para não bloquear a interface
    threading.Thread(target=run_script, daemon=True).start()

class ScriptSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Selecionar e Executar Script")
        self.root.geometry("800x400")

        self.selected_script = None

        # Definindo o layout com um PanedWindow para redimensionar as áreas
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Frame da lista de scripts (coluna da esquerda)
        self.left_frame = ttk.Frame(self.paned_window, padding=20)
        self.paned_window.add(self.left_frame, weight=1)  # weight define como o espaço é distribuído

        self.listbox = tk.Listbox(self.left_frame, width=40, height=20, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        self.load_scripts()

        self.run_button = ttk.Button(self.left_frame, text="Executar Script", command=self.run_script)
        self.run_button.pack(pady=10)

        # Frame para exibir as mensagens de execução (coluna da direita)
        self.right_frame = ttk.Frame(self.paned_window, padding=20)
        self.paned_window.add(self.right_frame, weight=3)  # weight define como o espaço é distribuído

        # Aqui você pode colocar uma área de texto para exibir a saída do script
        self.script_output_frame = tk.Frame(self.right_frame)
        self.script_output_frame.pack(fill=tk.BOTH, expand=True)

        # Widget de texto para exibir a saída do script
        self.output_text = tk.Text(self.script_output_frame, wrap=tk.WORD, height=15, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def load_scripts(self):
        """
        Carrega os scripts disponíveis e os adiciona à Listbox
        """
        self.scripts = list_available_scripts()

        # Limpa a listbox e adiciona os scripts
        self.listbox.delete(0, tk.END)
        for i, script_path in self.scripts.items():
            script_name = os.path.basename(script_path)
            self.listbox.insert(tk.END, script_name)

    def run_script(self):
        """
        Executa o script selecionado e exibe a saída na área de texto.
        """
        try:
            # Obtém o script selecionado
            selection = self.listbox.curselection()
            if not selection:
                messagebox.showwarning("Seleção", "Por favor, selecione um script da lista.")
                return

            script_name = self.listbox.get(selection[0])
            # Encontra a chave correta no dicionário self.scripts usando o índice da listbox
            script_index = list(self.scripts.keys())[selection[0]]
            script_path = self.scripts[script_index]

            # Limpa a área de saída antes de rodar o novo script
            self.output_text.delete(1.0, tk.END)

            # Exibe uma label dizendo que o script está sendo executado
            label = tk.Label(self.script_output_frame, text=f"Executando {script_name}...", font=("Arial", 14))
            label.pack()

            # Executa o script e redireciona a saída para a área de texto
            execute_script_in_thread(script_path, self.update_output)

        except Exception as e:
            messagebox.showerror("Erro ao executar", f"Erro ao tentar executar o script: {str(e)}")

    def update_output(self, output):
        """
        Atualiza a área de texto com a saída do script.
        """
        self.output_text.insert(tk.END, output + "\n")
        self.output_text.yview(tk.END)  # Rolagem automática para o final

if __name__ == "__main__":
    root = tk.Tk()
    app = ScriptSelectorApp(root)
    root.mainloop()
