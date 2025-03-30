import google.generativeai as genai
import pandas as pd
import json  
from query import df
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


genai.configure(api_key="API_TOKEN")

df_reduzido = df  
texto = df_reduzido.to_string(index=False)

def conversar(texto):
    model = genai.GenerativeModel("gemini-2.0-flash")  
    
    resposta = model.generate_content([ 
        "Você é um analista de dados comerciais com perfil gerencial. "
        "Recebe tabelas com dados e retorna uma análise detalhada estruturada em Markdown, "
        "com foco na apresentação para a diretoria comercial. Organize a resposta com os seguintes itens:\n"
        "1. **Resumo Executivo** - Apresente um resumo claro e conciso dos dados.\n"
        "2. **Indicadores de Desempenho** - Inclua métricas relevantes como crescimento, margem de lucro, etc.\n"
        "3. **Conclusões e Recomendações** - Ofereça insights sobre os dados e sugestões de ações.\n"
        "Use títulos e subtítulos adequados e formatação de listas onde necessário.\n\n"
        f"Aqui estão os dados fornecidos de forma tabulada:\n{texto}\n"
        "Por favor, retorne sua resposta em formato Markdown."
    ])
    
    if resposta and hasattr(resposta, 'text'):
        resposta_texto = resposta.text.strip()

        if resposta_texto.startswith("```json"):
            resposta_texto = resposta_texto[7:-3].strip()

        return resposta_texto
    
    return "Erro ao gerar análise."

analise_markdown = conversar(texto)

def gerar_pdf(conteudo, nome_arquivo="relatorio_analise.pdf"):

    margem_esquerda = 85
    margem_superior = 780  
    margem_direita = 540  
    margem_inferior = 50  
    espaco_entre_linhas = 12  

    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    largura, altura = A4
    pagina = 1

    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margem_esquerda, margem_superior, "Relatório de Análise Comercial")
    
    c.setFont("Helvetica", 10)
    y_pos = margem_superior - 30  

    linhas = conteudo.split("\n")

    for linha in linhas:
        linhas_quebradas = simpleSplit(linha, "Helvetica", 10, margem_direita - margem_esquerda)

        for sub_linha in linhas_quebradas:
            if y_pos < margem_inferior:  
                c.showPage()
                pagina += 1
                c.setFont("Helvetica", 10)
                y_pos = margem_superior  

            c.drawString(margem_esquerda, y_pos, sub_linha)
            y_pos -= espaco_entre_linhas

    
    for i in range(1, pagina + 1):
        c.setFont("Helvetica", 10)
        c.drawString(margem_esquerda, margem_inferior - 10, f"Página {i}")

    c.save()
    print(f"✅ Relatório gerado: {nome_arquivo}")

def gerar_txt(conteudo, nome_arquivo="relatorio_analise.md"):
    with open(nome_arquivo, "w", encoding="utf-8") as file:
        file.write(conteudo)
    print(f"✅ Relatório salvo em: {nome_arquivo}")

gerar_txt(analise_markdown)  
gerar_pdf(analise_markdown)  
