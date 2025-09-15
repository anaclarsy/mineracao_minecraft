import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Configurações iniciais
OUTPUT_DIR = "analise_mobs_graficos"
os.makedirs(OUTPUT_DIR, exist_ok=True)
CREDENTIALS_FILE = "minecraftvanillamobs-12b6cf523fe0.json"

# --------------------------------------------------------------------------------
# Etapa 1: Leitura e Limpeza dos Dados do Google Sheets
# --------------------------------------------------------------------------------

def load_data_from_google_sheets():
    """
    Lê os dados diretamente de duas planilhas do Google Sheets e os combina.
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        # Lista com os nomes das suas planilhas
        sheet_names = ["alexs_mobs", "minecraft_mobs"]
        all_dataframes = []

        for sheet_name in sheet_names:
            try:
                sheet = client.open(sheet_name).sheet1
                data = sheet.get_all_records()
                df = pd.DataFrame(data)
                
                # Normaliza os nomes das colunas para remover espaços e converter para minúsculas
                df.columns = [col.strip().lower() for col in df.columns]
                
                print(f"Dados lidos da planilha '{sheet_name}'. Colunas encontradas: {list(df.columns)}")
                
                all_dataframes.append(df)
            except gspread.exceptions.SpreadsheetNotFound:
                print(f"Erro: Planilha '{sheet_name}' não encontrada. Verifique o nome e se foi compartilhada.")
                continue

        if not all_dataframes:
            return pd.DataFrame(), pd.DataFrame()

        # Combina os dataframes em um único
        combined_df = pd.concat(all_dataframes, ignore_index=True)

        # Encontra a coluna de vida, tratando o caso de nomes diferentes
        health_column = None
        for col in combined_df.columns:
            if 'health' in col or 'vida' in col:
                health_column = col
                break
        
        if not health_column:
            print("Erro: Nenhuma coluna de Vida ('Health' ou 'Vida') encontrada. Verifique os cabeçalhos das planilhas.")
            return pd.DataFrame(), pd.DataFrame()

        # Trata as colunas de texto para extrair números e limpa os dados
        combined_df[health_column] = combined_df[health_column].astype(str).apply(
            lambda x: re.search(r'(\d+)', x).group(1) if re.search(r'(\d+)', x) else None
        )
        combined_df[health_column] = pd.to_numeric(combined_df[health_column], errors='coerce')
        
        # Remove linhas com valores NaN para a análise
        df_cleaned = combined_df.dropna(subset=[health_column])
        
        print(f"Dados totais válidos para análise de Vida: {len(df_cleaned)} mobs")
        return combined_df, df_cleaned

    except FileNotFoundError:
        print(f"Erro: Arquivo '{CREDENTIALS_FILE}' não encontrado na pasta.")
        return pd.DataFrame(), pd.DataFrame()

# --------------------------------------------------------------------------------
# Etapa 2: Análise e Geração de Gráficos (Ajustado)
# --------------------------------------------------------------------------------

def perform_analysis(df, df_cleaned):
    """ Realiza a análise e gera gráficos com os dados da planilha. """
    if df.empty or df_cleaned.empty:
        print("Não há dados suficientes para a análise. Verifique se a planilha foi preenchida.")
        return

    health_column = None
    for col in df_cleaned.columns:
        if 'health' in col or 'vida' in col:
            health_column = col
            break
            
    if not health_column:
        print("Erro interno: Coluna de vida não encontrada para análise.")
        return

    print("\nAnálise Estatística de Vida:")
    # Verifica se a coluna 'Fonte' existe antes de agrupar
    if 'fonte' in df_cleaned.columns:
        summary = df_cleaned.groupby('fonte')[[health_column]].mean().round(2)
        print(summary)
    else:
        print("A coluna 'Fonte' não foi encontrada. Calculando média geral.")
        print(f"Média de Vida: {df_cleaned[health_column].mean().round(2)}")

    if 'drops' in df.columns:
        print("\nAnálise de Drops (top 10):")
        all_drops = df['drops'].astype(str).str.lower().str.split(',').explode().str.strip()
        all_drops = all_drops[all_drops.str.len() > 1]
        all_drops = all_drops[all_drops != 'nan']
        all_drops = all_drops[all_drops != 'não especificado']
        top_drops = all_drops.value_counts().head(10)
        print(top_drops)
    else:
        print("A coluna 'Drops' não foi encontrada.")
        top_drops = pd.Series()
    
    print("\nGerando gráficos...")

    # Gráfico de média de vida por fonte (original)
    if 'fonte' in df_cleaned.columns:
        plt.figure(figsize=(8, 6))
        sns.barplot(x=summary.index, y=summary[health_column])
        plt.title('Média de Pontos de Vida (HP) por Fonte')
        plt.xlabel('Fonte')
        plt.ylabel('Média de Vida (HP)')
        plt.savefig(os.path.join(OUTPUT_DIR, 'media_hp_por_fonte.png'))
        plt.close()

    # NOVO GRÁFICO: Média de Vida por Temperamento
    if 'temper' in df_cleaned.columns:
        temper_summary = df_cleaned.groupby('temper')[[health_column]].mean().round(2)
        plt.figure(figsize=(10, 7))
        sns.barplot(x=temper_summary.index, y=temper_summary[health_column])
        plt.title('Média de Vida por Temperamento do Mob')
        plt.xlabel('Temperamento')
        plt.ylabel('Média de Vida (HP)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'media_hp_por_temperamento.png'))
        plt.close()
        print("Gráfico de Média de Vida por Temperamento gerado com sucesso!")
    else:
        print("A coluna 'Temper' não foi encontrada para gerar o gráfico.")

    if not top_drops.empty:
        plt.figure(figsize=(10, 7))
        top_drops.plot(kind='bar')
        plt.title('Top 10 Drops mais Comuns')
        plt.xlabel('Item de Drop')
        plt.ylabel('Frequência')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'frequencia_drops.png'))
        plt.close()
    else:
        print("Não há drops suficientes para gerar o gráfico.")
    
    print(f"\nAnálise completa. Gráficos e dados salvos na pasta '{OUTPUT_DIR}'.")

# --------------------------------------------------------------------------------
# Pipeline Principal
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    main_df, cleaned_df = load_data_from_google_sheets()
    if not main_df.empty:
        perform_analysis(main_df, cleaned_df)