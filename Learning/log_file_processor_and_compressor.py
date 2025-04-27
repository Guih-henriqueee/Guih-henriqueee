import os
import gzip
from collections import Counter
from tqdm import tqdm
import datetime

# Caminho para o diretório
caminho_diretorio = r'.\Log'
caminho_saida = r'.\resultado.txt'
caminho_log = r'.\Log_20250401.txt/'
caminho_saida_gzip = caminho_log + '.gz'

# Tamanho do bloco para processar (200MB por vez)
tamanho_bloco = 200 * 1024 * 1024  # 200MB

# Função para processar em blocos
def processar_bloco(buffer, contador_linhas):
    for linha in buffer.splitlines():
        linha = linha.strip()
        if linha:  # Ignora linhas vazias
            contador_linhas[linha] += 1

# Função para analisar um arquivo
def analisar_arquivo(caminho_arquivo, caminho_saida):
    print(f"🔍 Analisando: {os.path.basename(caminho_arquivo)}")
    total_tamanho = os.path.getsize(caminho_arquivo)
    contador_linhas = Counter()  # Cria um contador para cada arquivo

    with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as file, tqdm(total=total_tamanho, unit="B", unit_scale=True, desc=f"Lendo {os.path.basename(caminho_arquivo)}") as pbar:
        while True:
            buffer = file.read(tamanho_bloco)
            if not buffer:
                break
            processar_bloco(buffer, contador_linhas)
            pbar.update(len(buffer))

    # Processa e escreve os resultados no arquivo de saída
    with open(caminho_saida, 'a', encoding='utf-8') as output_file:
        for linha, quantidade in contador_linhas.items():
            output_file.write(f"{linha} - {quantidade}\n")
    
    # Limpeza do contador para liberar memória
    del contador_linhas

# Função para analisar todos os arquivos do diretório
def analisar_diretorio(caminho_diretorio, caminho_saida):
    print("📁 Iniciando análise de diretório...")
    for nome_arquivo in os.listdir(caminho_diretorio):
        caminho_completo = os.path.join(caminho_diretorio, nome_arquivo)
        if os.path.isfile(caminho_completo) and nome_arquivo.lower().endswith('.txt'):
            analisar_arquivo(caminho_completo, caminho_saida)

# Função para compactar arquivo com GZIP
def compactar_log_gzip(caminho_log, caminho_saida_gzip):
    tamanho_original = os.path.getsize(caminho_log)
    print("🔍 Iniciando compactação com GZIP...")
    with open(caminho_log, 'rb') as file_in:
        with gzip.open(caminho_saida_gzip, 'wb') as file_out:
            with tqdm(total=tamanho_original, unit="B", unit_scale=True, desc="Compactando") as pbar:
                while True:
                    buffer = file_in.read(tamanho_bloco)
                    if not buffer:
                        break
                    file_out.write(buffer)
                    pbar.update(len(buffer))

    # Resultado da compactação
    tamanho_compactado = os.path.getsize(caminho_saida_gzip)
    print("\n📈 Tamanho original: {:.2f} MB".format(tamanho_original / (1024 * 1024)))
    print("📉 Tamanho compactado (GZIP): {:.2f} MB".format(tamanho_compactado / (1024 * 1024)))
    reducao = ((tamanho_original - tamanho_compactado) / tamanho_original) * 100
    print("\n🎯 Redução de tamanho: {:.2f}%".format(reducao))

# --------- Análise de linhas ---------
# Faixas de tamanho
faixas_tamanhos = {
    '< 100 bytes': 0,
    '100B - 1KB': 0,
    '1KB - 10KB': 0,
    '> 10KB': 0
}

# Contador geral
contador_linhas_total = Counter()

# Ler o arquivo de saída e calcular as estatísticas
with open(caminho_saida, 'r', encoding='utf-8') as file:
    for linha in file:
        linha = linha.strip()
        if linha:
            contador_linhas_total[linha] += 1

# Lista para armazenar informações de cada linha
info_linhas = []

for linha, quantidade in contador_linhas_total.items():
    tamanho_bytes = len(linha.encode('utf-8'))
    tamanho_total_linha = tamanho_bytes * quantidade

    info_linhas.append({
        'linha': linha,
        'quantidade': quantidade,
        'tamanho_bytes': tamanho_bytes,
        'tamanho_total': tamanho_total_linha
    })

    # Classificar por faixa de tamanho
    if tamanho_bytes < 100:
        faixas_tamanhos['< 100 bytes'] += tamanho_total_linha
    elif tamanho_bytes < 1024:
        faixas_tamanhos['100B - 1KB'] += tamanho_total_linha
    elif tamanho_bytes < 10 * 1024:
        faixas_tamanhos['1KB - 10KB'] += tamanho_total_linha
    else:
        faixas_tamanhos['> 10KB'] += tamanho_total_linha

# Ordenar as linhas pelo tamanho total que ocupam
info_linhas.sort(key=lambda x: x['tamanho_total'], reverse=True)

# Calcula o total geral para porcentagem
total_arquivo = sum(faixas_tamanhos.values())

# --------- Resultados ---------

print("\n🏆 Top 10 mensagens que mais ocupam espaço:")
for info in info_linhas[:10]:
    tamanho_linha_mb = info['tamanho_total'] / (1024 * 1024)
    print(f"{info['quantidade']}x - {info['tamanho_bytes']} bytes por linha - Total: {tamanho_linha_mb:.2f} MB - Linha: {info['linha'][:60]}...")

# Tamanho das demais linhas
tamanho_restante = total_arquivo - sum([info['tamanho_total'] for info in info_linhas[:10]])
print(f"\n📈 Total de tamanho das demais linhas condensadas: {tamanho_restante / (1024 * 1024):.2f} MB")

# Total de mensagens únicas
print(f"\n📈 Total de mensagens únicas: {len(contador_linhas_total)}")

# Distribuição por faixa
print("\n📊 Distribuição do tamanho do arquivo por faixa:")
for faixa, tamanho in faixas_tamanhos.items():
    percentual = (tamanho / total_arquivo) * 100 if total_arquivo > 0 else 0
    print(f"{faixa}: {tamanho / (1024 * 1024):.2f} MB ({percentual:.2f}%)")

# Tamanho total do arquivo analisado
print(f"\n💾 Tamanho total analisado: {total_arquivo / (1024 * 1024):.2f} MB")

# Iniciar análise do diretório
analisar_diretorio(caminho_diretorio, caminho_saida)

# Compactação do arquivo de log
compactar_log_gzip(caminho_log, caminho_saida_gzip)
