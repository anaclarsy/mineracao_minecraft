Este é um script Python projetado para automatizar a análise de dados de mobs a partir de planilhas do Google Sheets. Ele se conecta à sua conta do Google, extrai dados de duas planilhas separadas (alexs_mobs e minecraft_mobs), os combina em um único conjunto de dados e gera gráficos de análise para visualização.

Funcionalidades
Leitura de Múltiplas Planilhas: Conecta-se à API do Google Sheets para ler e combinar dados de duas planilhas diferentes.

Limpeza de Dados: Extrai valores numéricos da coluna de vida (Health) e garante que os dados estejam prontos para a análise.

Análise de Dados: Calcula a média de vida dos mobs por fonte (Minecraft ou Alex's Mobs) e por comportamento (Behavior).

Geração de Gráficos: Salva gráficos de barras para facilitar a visualização da análise estatística.

Pré-requisitos
Certifique-se de ter as seguintes bibliotecas Python instaladas em seu ambiente. Você pode instalá-las com o pip:

pip install gspread oauth2client pandas matplotlib seaborn
Configuração da API do Google
Para que o script funcione, ele precisa de acesso às suas planilhas. Siga estes passos de configuração apenas uma vez:

Baixe o arquivo de credenciais: No Google Cloud Console, crie uma conta de serviço e baixe o arquivo de chave JSON. Certifique-se de que o arquivo esteja nomeado como minecraftvanillamobs-12b6cf523fe0.json e salvo na mesma pasta do script.

Compartilhe as planilhas: Abra as planilhas alex_mobs e minecraft_mobs no Google Sheets e compartilhe-as com o e-mail da conta de serviço que você criou. Dê a permissão de Editor.

Como Rodar o Script
Abra o Prompt de Comando (no Windows).

Navegue até a pasta do projeto. Use o seguinte comando para ir até o diretório correto:

cd C:caminho-sua-pasta
pip install gspread oauth2client pandas matplotlib seaborn

Execute o script com o comando:
python mineracao.py
O Que o Script Produz
Após a execução, o script irá:

Exibir uma análise estatística no terminal.

Criar uma pasta chamada analise_mobs_graficos no seu diretório.

Salvar os seguintes gráficos dentro dessa pasta:

media_hp_por_fonte.png: Um gráfico de barras comparando a média de vida dos mobs entre as duas planilhas.

media_hp_por_comportamento.png: Um gráfico de barras mostrando a média de vida por tipo de comportamento (seus dados de "behavior").

frequencia_drops.png: Um gráfico dos drops mais comuns.