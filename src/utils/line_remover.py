import csv
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog

def list_csv_files(directory="data"):
    return [f for f in os.listdir(directory) if f.endswith(".csv")]

def process_csv(file_path, log_widget, preview_widget):
    try:
        # Primeiro tenta ler o CSV completo
        df_original = pd.read_csv(file_path, sep=';')

        # Exibir conteúdo original ANTES de qualquer pergunta
        preview_widget.configure(state='normal')
        preview_widget.delete(1.0, tk.END)
        preview_widget.insert(tk.END, "📄 Conteúdo original do arquivo:\n\n")
        preview_widget.insert(tk.END, df_original.to_string(index=False))
        preview_widget.configure(state='disabled')

        # Log da leitura bem-sucedida do original
        log_widget.configure(state='normal')
        log_widget.insert(tk.END, f"\n✅ Arquivo lido com sucesso: {file_path}\n")
        log_widget.insert(tk.END, f"📊 Linhas: {df_original.shape[0]}, Colunas: {df_original.shape[1]}\n")
        log_widget.insert(tk.END, "👀 Visualização do conteúdo original exibida.\n")
        log_widget.insert(tk.END, "-" * 50 + "\n")
        log_widget.configure(state='disabled')

        # Perguntar ao user se deseja remover linhas
        remove_rows = simpledialog.askinteger(
            "Remover Linhas",
            "Deseja remover quantas linhas do início do CSV?",
            minvalue=0
        )

        if remove_rows is None:
            messagebox.showinfo("Cancelado", "Operação cancelada pelo usuário.")
            return

        if remove_rows > 0:
            # Reprocessar com linhas removidas
            df = pd.read_csv(file_path, sep=';', skiprows=remove_rows)

            # Exibir conteúdo após remoção das linhas
            preview_widget.configure(state='normal')
            preview_widget.delete(1.0, tk.END)
            preview_widget.insert(tk.END, f"📄 Conteúdo após remover {remove_rows} linhas:\n\n")
            preview_widget.insert(tk.END, df.to_string(index=False))
            preview_widget.configure(state='disabled')

            # Perguntar ao utilizador os nomes das colunas
            columns = []
            for i in range(df.shape[1]):
                column_name = simpledialog.askstring(
                    "Novo Cabeçalho",
                    f"Indique o nome de todas as colunas: {i + 1}?"
                )
                if column_name:
                    columns.append(column_name)
                else:
                    columns.append(f"column_{i + 1}")

            # Atribuir os novos nomes às colunas
            df.columns = columns

            # Salvar versão limpa com novos cabeçalhos
            output_file = os.path.join("data", "cleaned_removed_" + os.path.basename(file_path))
            df.to_csv(output_file, index=False, sep=';', quoting=csv.QUOTE_NONE, escapechar='\\')

            # Log da nova leitura
            log_widget.configure(state='normal')
            log_widget.insert(tk.END, f"\n🧹 Linhas removidas: {remove_rows}\n")
            log_widget.insert(tk.END, f"📁 Arquivo limpo salvo como: {output_file}\n")
            log_widget.insert(tk.END, f"📊 Linhas restantes: {df.shape[0]}, Colunas: {df.shape[1]}\n")
            log_widget.insert(tk.END, "-" * 50 + "\n")
            log_widget.configure(state='disabled')

    except pd.errors.ParserError:
        # Tratamento em caso de erro ao ler
        remove_invalid_rows = simpledialog.askinteger(
            "Linhas Inválidas",
            "Erro ao ler o CSV.\nQuantas linhas deseja eliminar do topo do arquivo?",
            minvalue=0
        )

        if remove_invalid_rows is not None and remove_invalid_rows > 0:
            try:
                df = pd.read_csv(file_path, sep=';', skiprows=remove_invalid_rows)
                output_file = os.path.join("data", "cleaned_removed_" + os.path.basename(file_path))
                df.to_csv(output_file, index=False, sep=';', quoting=csv.QUOTE_NONE, escapechar='\\')

                log_widget.configure(state='normal')
                log_widget.insert(tk.END, f"\n✅ Linhas removidas: {remove_invalid_rows}\n")
                log_widget.insert(tk.END, f"📁 Novo arquivo salvo como: {output_file}\n")
                log_widget.insert(tk.END, f"📊 Linhas: {df.shape[0]}, Colunas: {df.shape[1]}\n")
                log_widget.insert(tk.END, "-" * 50 + "\n")
                log_widget.configure(state='disabled')

                preview_widget.configure(state='normal')
                preview_widget.delete(1.0, tk.END)
                preview_widget.insert(tk.END, df.to_string(index=False))
                preview_widget.configure(state='disabled')

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao tentar reprocessar o arquivo: {str(e)}")
        else:
            messagebox.showinfo("Cancelado", "Nenhuma linha foi removida.")

def main_gui():
    root = tk.Tk()
    root.title("Remover Linhas Inválidas do CSV")
    root.geometry("1200x800")
    root.resizable(False, True)


    label = tk.Label(root, text="Selecione o arquivo CSV para remover as linhas:", font=("Arial", 12))
    label.pack(pady=10)

    csv_files = list_csv_files()
    if not csv_files:
        messagebox.showinfo("Nenhum CSV", "Nenhum arquivo CSV foi encontrado na pasta 'data'.")
        root.destroy()
        return

    combo = ttk.Combobox(root, values=csv_files, state="readonly", width=50)
    combo.pack(pady=5)

    log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12, state='disabled')
    log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    preview_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, state='disabled')
    preview_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def on_process():
        selected = combo.get()
        if selected:
            path = os.path.join("data", selected)
            process_csv(path, log_text, preview_text)
        else:
            messagebox.showwarning("Aviso", "Por favor, selecione um arquivo.")

    # Centralizando o botão na tela
    button = tk.Button(root, text="Processar CSV", command=on_process, font=("Arial", 11))
    button.place(relx=0.5, rely=0.5, anchor="center")

    root.mainloop()

if __name__ == "__main__":
    main_gui()
