import customtkinter as ctk
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import csv
import pdfplumber
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image


# Função para processar o texto do protocolo em uma estrutura de dados
def process_protocol_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            content = ""
            for page in pdf.pages:
                content += page.extract_text() + "\n"
        content = re.sub(r'\s{2,}', ' ', content)
        content = re.sub(r'(\n)+', '\n', content)
        sections = re.split(r"(\d+\.\s[A-ZÁÀÂÃÉÈÍÓÔÕÚÇ][^\n]*)", content)

        protocol = {}
        current_key = None

        for i, section in enumerate(sections):
            if i % 2 == 1:
                current_key = section.strip()
                protocol[current_key] = ""
            elif current_key:
                protocol[current_key] += section.strip()

        return protocol
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        return {}


# Gráfico de análise de sentimento
def plot_sentiment(sentiment):
    labels = ['Positivo', 'Negativo', 'Neutro']
    sizes = [sentiment['pos'], sentiment['neg'], sentiment['neu']]
    colors = ['#8BC34A', '#FF5722', '#FFC107']
    explode = (0.1, 0.1, 0)

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)  # Fecha o gráfico para evitar consumo excessivo de memória
    return buffer


# Carregar os dados do protocolo a partir do PDF
protocol_data = process_protocol_pdf("D:/Senac/5Periodo/IA/catrina-bot/remume-2021-protocolo-doencas-infecto-parasitarias.pdf")


class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Catrina - Assistente Virtual")
        master.geometry("700x700")

        try:
            master.iconbitmap("icon_1c46f8d5bbe5584b28c70191887fe3d5.ico")
        except Exception:
            print("Ícone não encontrado. Ignorando...")

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)
        master.grid_rowconfigure(3, weight=0)
        master.grid_rowconfigure(4, weight=0)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=600, height=350, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Catrina, sua assistente virtual. Escolha uma opção e me diga como posso ajudar!\n")
        self.text_area.configure(state="disabled")

        # Menu de opções
        self.option_menu = ctk.CTkOptionMenu(
            master, 
            values=["Buscar Remédios", "Análise de Sentimento", "Consulta ao Protocolo"], 
            command=self.update_option
        )
        self.option_menu.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.option_menu.set("Buscar Remédios")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=500, placeholder_text="Digite aqui...")
        self.entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", command=self.process_input)
        self.send_button.grid(row=3, column=0, padx=20, pady=10)

        # Variável para rastrear a opção selecionada
        self.selected_option = "Buscar Remédios"

        # Label para exibir gráficos
        self.image_label = None

        # Analisador de sentimentos
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def update_option(self, value):
        self.selected_option = value
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, f"\nCatrina: Você escolheu a opção '{value}'.\n")
        self.text_area.configure(state="disabled")

        # Remover o gráfico se estiver visível
        if self.image_label:
            self.image_label.destroy()
            self.image_label = None

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        # Limpar gráfico se houver
        if self.image_label:
            self.image_label.destroy()
            self.image_label = None

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")

        response = ""
        if self.selected_option == "Buscar Remédios":
            response = self.get_medicine_info(user_input)
        elif self.selected_option == "Análise de Sentimento":
            response = self.analyze_sentiment(user_input)
        elif self.selected_option == "Consulta ao Protocolo":
            response = self.get_disease_and_treatment(user_input)

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Catrina: " + response + "\n")
        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

    def get_medicine_info(self, user_input):
        try:
            csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSyG1HVyy-9iNSpta7wbi61Hrqb4k7gk6kpYAZufNtIkKwmfwMzJpMIHCK9aEMjaDyNsreAE9Juke7s/pub?output=csv"
            response = requests.get(csv_url)
            response.raise_for_status()
            csv_data = response.text.splitlines()
            reader = csv.reader(csv_data)

            header = next(reader)
            for row in reader:
                if len(row) < 3:
                    continue
                remédio, família, uso = row[0], row[1], row[2]
                if user_input.lower() in remédio.lower():
                    return f"**Remédio**: {remédio}\n**Pertence à família**: {família}\n**Uso**: {uso}"

            return "Desculpe, não encontrei informações sobre esse remédio no CSV."
        except requests.exceptions.RequestException as e:
            return f"Erro ao acessar o CSV online: {e}"

    def analyze_sentiment(self, user_input):
        try:
            sentiment = self.sentiment_analyzer.polarity_scores(user_input)
            compound = sentiment['compound']
            if compound > 0:
                result = "O texto tem um sentimento positivo. 😊"
            elif compound < 0:
                result = "O texto tem um sentimento negativo. 😟"
            else:
                result = "O texto tem um sentimento neutro. 😐"

            self.display_sentiment_chart(sentiment)
            return result
        except Exception as e:
            return f"Ocorreu um erro ao analisar o sentimento: {e}"
    
    def display_sentiment_chart(self, sentiment):
        try:
            buffer = plot_sentiment(sentiment)
            chart = ctk.CTkImage(light_image=Image.open(buffer), dark_image=Image.open(buffer), size=(300, 300))

            if self.image_label:
                self.image_label.destroy()
            self.image_label = ctk.CTkLabel(self.master, image=chart)
            self.image_label.image = chart  # Manter referência
            self.image_label.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        except Exception as e:
            print(f"Erro ao exibir gráfico: {e}")

    def get_disease_and_treatment(self, query):
        for disease, info in protocol_data.items():
            if query.lower() in disease.lower():
                return f"**Doença**: {disease}\n**Informações**: {info}"
        return "Desculpe, não encontrei informações sobre essa doença no protocolo."


if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
