import os
from datetime import datetime

def extrair_tempo(caminho_arquivo):
    try:
        with open(caminho_arquivo, "r") as f:
            linhas = f.readlines()

        inicio_str = fim_str = None
        for linha in linhas:
            if "Tempo de início:" in linha:
                inicio_str = linha.strip().split("Tempo de início:")[1].strip()
            elif "Tempo de fim:" in linha:
                fim_str = linha.strip().split("Tempo de fim:")[1].strip()

        if inicio_str and fim_str:
            formato = "%Y-%m-%d %H:%M:%S"
            inicio = datetime.strptime(inicio_str, formato)
            fim = datetime.strptime(fim_str, formato)
            return (fim - inicio).total_seconds()
    except Exception as e:
        print(f"⚠️ Erro ao processar {caminho_arquivo}: {e}")
    return None

def analisar_tempos(pasta_raiz):
    resultados = []
    eliminados = 0

    with open("resumo_tempos.txt", "w") as f:
        for dirpath, dirnames, filenames in os.walk(pasta_raiz):
            nome_pasta = os.path.basename(dirpath)
            if nome_pasta.startswith("n"):
                f.write(f"{dirpath}: Eliminado por não completar a trajetória\n\n")
                eliminados += 1
                continue

            for nome_arquivo in filenames:
                if nome_arquivo == "tempo_simulacao.txt":
                    caminho = os.path.join(dirpath, nome_arquivo)
                    tempo = extrair_tempo(caminho)
                    if tempo is not None:
                        resultados.append((dirpath, tempo))
                        f.write(f"{dirpath}:\n")
                        f.write(f"  Tempo total: {int(tempo)} segundos\n\n")

        if resultados:
            tempos = [t for _, t in resultados]
            media = sum(tempos) / len(tempos)
            f.write("⏱️ Tempo médio (excluindo eliminados):\n")
            f.write(f"Tempo médio: {int(media)} segundos\n")
            f.write(f"\n🚫 Pastas eliminadas: {eliminados}\n")
            print("✅ Estatísticas de tempo salvas em resumo_tempos.txt")
        else:
            f.write("Nenhum arquivo tempo_simulacao.txt encontrado.\n")
            f.write(f"🚫 Pastas eliminadas: {eliminados}\n")
            print("⚠️ Nenhum tempo encontrado.")

# === Execução principal ===
if __name__ == "__main__":
    pasta_raiz = os.getcwd()  # Diretório atual
    analisar_tempos(pasta_raiz)
