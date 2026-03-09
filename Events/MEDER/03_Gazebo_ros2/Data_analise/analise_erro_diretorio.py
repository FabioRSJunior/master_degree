import os
import pandas as pd
import numpy as np

def extrair_estatisticas_erro(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv, header=None, names=['timestamp', 'error'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%H:%M:%S.%f')
        df['time_sec'] = (df['timestamp'] - df['timestamp'][0]).dt.total_seconds()
        erro = df['error'].values

        return {
            "Erro médio": np.mean(erro),
            "MAE": np.mean(np.abs(erro)),
            "RMSE": np.sqrt(np.mean(erro**2)),
            "Overshoot": np.max(erro),
            "Esforço": np.sum(np.abs(erro)),
            "Ação": np.sum(np.abs(np.diff(erro))),
            "Desvio padrão": np.std(erro),
            "Erro final": erro[-1]
        }
    except Exception as e:
        print(f"⚠️ Erro ao processar {caminho_csv}: {e}")
        return None

def analisar_erros(pasta_raiz):
    resultados = []
    eliminados = 0

    with open("resumo_erros.txt", "w") as f:
        for dirpath, dirnames, filenames in os.walk(pasta_raiz):
            nome_pasta = os.path.basename(dirpath)
            if nome_pasta.startswith("n"):
                f.write(f"{dirpath}: Eliminado por não completar a trajetória\n\n")
                eliminados += 1
                continue

            for nome_arquivo in filenames:
                if nome_arquivo == "error_data.csv":
                    caminho = os.path.join(dirpath, nome_arquivo)
                    stats = extrair_estatisticas_erro(caminho)
                    if stats:
                        resultados.append((dirpath, stats))
                        f.write(f"{dirpath}:\n")
                        for k, v in stats.items():
                            f.write(f"  {k}: {v:.4f}\n")
                        f.write("\n")

        if resultados:
            chaves = resultados[0][1].keys()
            medias = {}
            for chave in chaves:
                valores = [stats[chave] for _, stats in resultados]
                medias[chave] = np.mean(valores)

            f.write("📊 Estatísticas Médias (excluindo eliminados):\n")
            for k, v in medias.items():
                f.write(f"{k}: {v:.4f}\n")
            f.write(f"\n🚫 Pastas eliminadas: {eliminados}\n")

            print("✅ Estatísticas médias salvas em resumo_erros.txt")
        else:
            f.write("Nenhum arquivo error_data.csv encontrado.\n")
            f.write(f"🚫 Pastas eliminadas: {eliminados}\n")
            print("⚠️ Nenhum erro encontrado.")

# === Execução principal ===
if __name__ == "__main__":
    pasta_raiz = os.getcwd()  # Diretório atual
    analisar_erros(pasta_raiz)

