import customtkinter as ctk

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Catrina")
        master.geometry("700x600")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("system")  # "light" ou "dark"
        ctk.set_default_color_theme("blue")  # Temas disponíveis: "blue", "green", "dark-blue"

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Catrina, sua assistente virtual. Como posso te ajudar hoje?\n")
        self.text_area.configure(state="normal")  # edição direta na área de texto

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite sua pergunta aqui...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()