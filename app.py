# ETAPA 1. Baixar e limpar um conjunto de dados “Olympic Medals by Country” 
# usando o código Python gerado pelo ChatGPT.

import os                      # os: ajuda a achar o caminho do arquivo CSV
import pandas as pd            # pandas: biblioteca para trabalhar com tabelas (DataFrames)
import plotly.express as px    # plotly express: biblioteca para criar os gráficos
from dash import Dash, dcc, html   # Dash: o aplicativo / dcc: componentes (gráficos) / html: tags HTML

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



# ETAPA 3. Adicionar um gráfico de área empilhada ao painel, que exibe os 10 principais países por 
# contagem total de medalhas ao longo do tempo. 

# Pega os nomes dos 10 países com mais medalhas no total (.nlargest(10) = os 10 maiores)
top_countries = df_country_medals.groupby('Country_Name')['Total_Medals'].sum().nlargest(10).index

# Soma as medalhas por país E por ano (uma linha para cada combinação país + ano)
df_countries = df.groupby(['Country_Name', 'Year'])['Total_Medals'].sum().reset_index()

# Fica só com as linhas dos 10 países (.isin verifica se o país está na lista top_countries)
df_top_10_countries = df_countries[df_countries['Country_Name'].isin(top_countries)]

# Gera o gráfico de áreas empilhadas: eixo X = ano, eixo Y = medalhas, uma cor para cada país
area_fig = px.area(
    df_top_10_countries,                                          # tabela que alimenta o gráfico
    x='Year',                                                     # coluna do eixo X (anos)
    y='Total_Medals',                                             # coluna do eixo Y (medalhas)
    color='Country_Name',                                         # uma cor (uma área) para cada país
    title='Top 10 Países por contagem total de medalhas de 1992 a 2020',   # título do gráfico
)

# Cria o aplicativo Dash (o painel que vai juntar os gráficos)
app = Dash(__name__)

# Define o layout: o mapa em cima, e embaixo os gráficos de área e de barras lado a lado
app.layout = html.Div([
     # primeiro o mapa (id: nome do gráfico, vamos usar nos filtros)
    dcc.Graph(figure=map_fig, id='map'),                 
    # esta Div agrupa os dois gráficos da segunda linha
    html.Div([                                            
        dcc.Graph(figure=area_fig, id='area-chart'),
        dcc.Graph(figure=bar_fig, id='bar-chart'),
    ], style={'display': 'flex'}),                        # flex = coloca um gráfico ao lado do outro
])

# Só pra testar
if __name__ == '__main__':
    print(df_country_medals.sort_values('Total_Medals', ascending=False).head(10))   # top 10 do mapa
    # Inicia o servidor local. Depois abra http://127.0.0.1:8050 no navegador.
    # (O tutorial usa app.run_server(), que nas versões novas do Dash virou app.run().)
    app.run(debug=False)    # com debug=True aparecem as mensagens de erro na tela



# Etapa 4. Adicionando um segundo gráfico, um gráfico de barras mostrando os 10 países 
# com mais medalhas de ouro durante o mesmo período.

# Soma só a coluna Gold (ouro) por país e pega os 10 maiores.
# reset_index() faz Country_Name voltar a ser uma coluna normal.
df_top_countries_gold = df.groupby('Country_Name')['Gold'].sum().nlargest(10).reset_index()

# Gera o gráfico de barras: país no eixo X e quantidade de ouros no eixo Y
bar_fig = px.bar(
    df_top_countries_gold,                                            # tabela que alimenta o gráfico
    x='Country_Name',                                                 # coluna do eixo X (países)
    y='Gold',                                                         # coluna do eixo Y (medalhas de ouro)
    title='Top 10 países com mais medalhas de ouro de 1992 a 2020',   # título do gráfico
)

