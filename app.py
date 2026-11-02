# ETAPA 1. Baixar e limpar um conjunto de dados “Olympic Medals by Country” 
# usando o código Python gerado pelo ChatGPT.

import os                      # os: ajuda a achar o caminho do arquivo CSV
import pandas as pd            # pandas: biblioteca para trabalhar com tabelas (DataFrames)
import plotly.express as px    # plotly express: biblioteca para criar os gráficos

# Descobre a pasta onde este arquivo (app.py) está salvo.
# Assim o programa acha o CSV mesmo quando for executado de outro lugar (como no Render).
PASTA_DO_ARQUIVO = os.path.dirname(os.path.abspath(__file__))

# Monta o caminho completo até o arquivo lá do CSV (q eu coloquei na mesma pasta do app.py)
CAMINHO_CSV = os.path.join(PASTA_DO_ARQUIVO, 'Summer_olympic_Medals.csv')

# Lê o arquivo CSV e guarda no DataFrame
# OBS: o tutorial usa sep=';', mas o arquivo é separado por VÍRGULA 
# (o padrão do pandas), por isso eu n informei o sep
df = pd.read_csv(CAMINHO_CSV)

# Troca 'United States' por 'United States of America' na coluna Country_Name
# pq o tutorial pede essa troca. Assim todas as linhas dos EUA ficam com o mesmo nome,
# e as somas (mapa, área e barras) não separam o país em dois.
df['Country_Name'] = df['Country_Name'].replace('United States', 'United States of America')


# ETAPA 2. Elaborar um mapa Plotly para representar visualmente o total de 
# medalhas cumulativas por país de 1992 a 2020.

# Fica só com as linhas entre 1992 e 2020
# O .copy() cria uma cópia independente. Com ele evitamos o aviso 
# "SettingWithCopyWarning" que aparecia no tutorial quando criei a 
# coluna nova em cima de um pedaço do df.
df = df[(df['Year'] >= 1992) & (df['Year'] <= 2020)].copy()

# Cria a coluna Total_Medals somando Ouro + Prata + Bronze de cada linha
df['Total_Medals'] = df['Gold'] + df['Silver'] + df['Bronze']

# Agrupa por país e soma o total de medalhas de todos os anos.
# reset_index() faz Country_Name voltar a ser uma coluna normal.
df_country_medals = df.groupby('Country_Name')['Total_Medals'].sum().reset_index()

# Gera o mapa onde cada país recebe uma cor conforme a quantidade de medalhas
map_fig = px.choropleth(
    df_country_medals,                                    # tabela que alimenta o mapa
    locations='Country_Name',                             # coluna com os nomes dos países
    locationmode='country names',                  # diz ao Plotly que os locais são NOMES de países
    color='Total_Medals',                                 # coluna que define a cor de cada país
    hover_name='Country_Name',                            # nome que aparece ao passar o mouse
    color_continuous_scale=px.colors.sequential.YlOrRd,   # escala de cores amarelo -> vermelho
    title='Total de medalhas de 1992 a 2020',             # título do gráfico
)

# Só pra testar

if __name__ == '__main__':
    print(df_country_medals.sort_values('Total_Medals', ascending=False).head(10))   # top 10 do mapa
    map_fig.show()                                                                    # abre o mapa
