import openai
from query import df
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


openai.api_key = [TOKEN]
df_reduzido = df  
texto = df_reduzido.to_string(index=False)

def conversar(texto):
    # """Envia os dados para o ChatGPT e retorna uma análise simplificada."""
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": (
                "Você é um analista de dados comerciais com perfil gerencial. "
                "Recebe tabelas com dados e retorna uma análise detalhada que inclui indicadores de desempenho, "
                "resultados comparativos e planejamento estratégico. A análise deve focar em resultados concretos, "
                "identificação de tendências e recomendações para tomada de decisão. Use métricas como crescimento, "
                "eficiência operacional, margem de lucro, e outros KPIs relevantes."
            )},
            {"role": "user", "content": texto},
        ],
        max_tokens=200,  
        temperature=0.3,  
    )
    return resposta['choices'][0]['message']['content']


analise = conversar(texto)


def gerar_pdf(conteudo, nome_arquivo="relatorio_analise.pdf"):
    # """Gera um PDF com a análise dos dados."""}
    c = canvas.Canvas(nome_arquivo, pagesize=letter)
    largura, altura = letter


    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, altura - 50, "Relatório de Análise de Dados")


    c.setFont("Helvetica", 10)
    y_pos = altura - 80

    for linha in conteudo.split("\n"):
        if y_pos < 50:  
            c.showPage()
            c.setFont("Helvetica", 10)
            y_pos = altura - 50
        c.drawString(50, y_pos, linha)
        y_pos -= 15

    c.save()
    print(f"Relatório gerado: {nome_arquivo}")

gerar_pdf(analise)

def gerar_txt(conteudo, nome_arquivo="relatorio_analise.txt"):
    """Gera um arquivo TXT com a análise dos dados."""
    with open(nome_arquivo, "w") as file:
        file.write("Relatório de Análise de Dados Comerciais\n\n")
        file.write(conteudo)
    print(f"Relatório gerado: {nome_arquivo}")

gerar_txt(analise)
