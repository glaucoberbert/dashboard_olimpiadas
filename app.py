# ETAPA 1. Baixar e limpar um conjunto de dados “Olympic Medals by Country” 
# usando o código Python gerado pelo ChatGPT.

import os                      # os: ajuda a achar o caminho do arquivo CSV
import pandas as pd            # pandas: biblioteca para trabalhar com tabelas (DataFrames)
import plotly.express as px    # plotly express: biblioteca para criar os gráficos
from dash import Dash, dcc, html   # Dash: o aplicativo / dcc: componentes (gráficos e filtros) / html: tags HTML
from dash import Input, Output     # Input e Output: ligam os filtros (entrada) aos gráficos (saída)

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


# CONFIGURAÇÃO DOS FILTROS (dicionários que "traduzem" o que o usuário escolhe na tela)

# Traduz o texto do filtro de medalha (o que o usuário vê) para o nome da coluna no df
COLUNA_DA_MEDALHA = {
    'Todos':  'Total_Medals',   # Todos = soma das 3 medalhas
    'Ouro':   'Gold',
    'Prata':  'Silver',
    'Bronze': 'Bronze',
}

# Cor das barras para cada tipo de medalha (no tutorial a barra fica 'gold')
COR_DA_MEDALHA = {
    'Todos':  '#0081C8',   # azul olímpico
    'Ouro':   'gold',
    'Prata':  '#A9A9A9',   # cinza (o 'silver' puro fica muito claro no fundo branco)
    'Bronze': '#CD7F32',
}

# Texto que aparece nos títulos dos gráficos conforme a medalha escolhida
TEXTO_DA_MEDALHA = {
    'Todos':  'Total de medalhas',
    'Ouro':   'Medalhas de Ouro',
    'Prata':  'Medalhas de Prata',
    'Bronze': 'Medalhas de Bronze',
}

# Cores de cada fatia da pizza
CORES_DA_PIZZA = {'Ouro': 'gold', 'Prata': '#A9A9A9', 'Bronze': '#CD7F32'}

# Lista dos anos olímpicos da base (1992, 1996, ..., 2020) em ordem crescente
ANOS = sorted(df['Year'].unique())

# Dicionário "ano -> país sede e cidade sede". Ex.: 1992 -> Spain, Barcelona
# drop_duplicates('Year') deixa só uma linha por ano (todas do mesmo ano têm a mesma sede)
sedes = df.drop_duplicates('Year').set_index('Year')[['Host_country', 'Host_city']]

# Opções do filtro de ANO. Cada opção tem um "label" (texto que aparece) e um "value" (valor interno).
# A primeira é 'Todos' (usa todos os anos) e depois vem uma opção para cada ano olímpico.
OPCOES_ANO = [{'label': 'Todos os anos (1992-2020)', 'value': 'Todos'}]
for ano in ANOS:
    OPCOES_ANO.append({
        'label': f"{ano} - {sedes.loc[ano, 'Host_country']} ({sedes.loc[ano, 'Host_city']})",   # Ex.: "1992 - Spain (Barcelona)"
        'value': int(ano),                                                                       # int() converte o número do numpy para int normal
    })

# Lista de países (em ordem alfabética) para o filtro do gráfico de pizza
PAISES = sorted(df['Country_Name'].unique())


# Função que cria o MAPA. Ela recebe o tipo de medalha escolhido no filtro e devolve a figura.
# (Virou função porque o mapa precisa ser refeito toda vez que o usuário muda o filtro.)
def criar_mapa(tipo):
    # Descobre qual coluna usar (ex.: 'Todos' -> 'Total_Medals', 'Ouro' -> 'Gold')
    coluna = COLUNA_DA_MEDALHA[tipo]

    # Agrupa por país e soma o total de medalhas de todos os anos.
    # reset_index() faz Country_Name voltar a ser uma coluna normal.
    df_country_medals = df.groupby('Country_Name')[coluna].sum().reset_index()

    # Gera o mapa onde cada país recebe uma cor conforme a quantidade de medalhas
    map_fig = px.choropleth(
        df_country_medals,                                    # tabela que alimenta o mapa
        locations='Country_Name',                             # coluna com os nomes dos países
        locationmode='country names',                         # diz ao Plotly que os locais são NOMES de países
        color=coluna,                                         # coluna que define a cor de cada país
        hover_name='Country_Name',                            # nome que aparece ao passar o mouse
        color_continuous_scale=px.colors.diverging.RdYlGn,    # escala de cores: vermelho (poucas) -> verde (muitas) [ETAPA 5]
        title=f'{TEXTO_DA_MEDALHA[tipo]} de 1992 a 2020',     # título do gráfico (muda conforme o filtro)
        labels={coluna: 'Medalhas'},                          # nome mais bonito na barra de cores
    )
    return map_fig



# ETAPA 3. Adicionar um gráfico de área empilhada ao painel, que exibe os 10 principais países por 
# contagem total de medalhas ao longo do tempo. 

# Função que cria o gráfico de ÁREA (também depende do filtro de medalha)
def criar_area(tipo):
    coluna = COLUNA_DA_MEDALHA[tipo]

    # Pega os nomes dos 10 países com mais medalhas no total (.nlargest(10) = os 10 maiores)
    top_countries = df.groupby('Country_Name')[coluna].sum().nlargest(10).index

    # Soma as medalhas por país E por ano (uma linha para cada combinação país + ano)
    df_countries = df.groupby(['Country_Name', 'Year'])[coluna].sum().reset_index()

    # Fica só com as linhas dos 10 países (.isin verifica se o país está na lista top_countries)
    df_top_10_countries = df_countries[df_countries['Country_Name'].isin(top_countries)]

    # Gera o gráfico de áreas empilhadas: eixo X = ano, eixo Y = medalhas, uma cor para cada país
    area_fig = px.area(
        df_top_10_countries,                                          # tabela que alimenta o gráfico
        x='Year',                                                     # coluna do eixo X (anos)
        y=coluna,                                                     # coluna do eixo Y (medalhas)
        color='Country_Name',                                         # uma cor (uma área) para cada país
        title=f'Top 10 Países - {TEXTO_DA_MEDALHA[tipo]} de 1992 a 2020',   # título do gráfico
        labels={coluna: 'Medalhas', 'Country_Name': 'País', 'Year': 'Ano'}, # nomes mais bonitos nos eixos e na legenda
    )
    return area_fig



# Etapa 4. Adicionando um segundo gráfico, um gráfico de barras mostrando os 10 países 
# com mais medalhas de ouro durante o mesmo período.

# Função que cria o gráfico de BARRAS. Depende do filtro de medalha E do filtro de ano.
def criar_barras(tipo, ano):
    coluna = COLUNA_DA_MEDALHA[tipo]

    if ano == 'Todos':
        # Sem filtro de ano: usa a base inteira (1992 a 2020)
        base = df
        periodo = 'de 1992 a 2020'
    else:
        # Com filtro de ano: fica só com as linhas daquele ano olímpico
        base = df[df['Year'] == ano]
        periodo = f"em {ano} (sede: {sedes.loc[ano, 'Host_country']})"

    # Soma a coluna escolhida por país e pega os 10 maiores.
    # reset_index() faz Country_Name voltar a ser uma coluna normal.
    df_top_countries = base.groupby('Country_Name')[coluna].sum().nlargest(10).reset_index()

    # Gera o gráfico de barras: país no eixo X e quantidade de medalhas no eixo Y
    bar_fig = px.bar(
        df_top_countries,                                                 # tabela que alimenta o gráfico
        x='Country_Name',                                                 # coluna do eixo X (países)
        y=coluna,                                                         # coluna do eixo Y (medalhas)
        color_discrete_sequence=[COR_DA_MEDALHA[tipo]],                   # cor das barras [ETAPA 5 do tutorial: 'gold']
        title=f'Top 10 países - {TEXTO_DA_MEDALHA[tipo]} {periodo}',      # título do gráfico
        labels={coluna: 'Medalhas', 'Country_Name': 'País'},              # nomes mais bonitos nos eixos
    )
    return bar_fig



# GRÁFICO NOVO (pedido no trabalho): pizza com o total de Ouro, Prata e Bronze de um país.

# Função que cria a PIZZA. Recebe o país, o tipo de medalha (só pra destacar a fatia) e o ANO escolhido.
def criar_pizza(pais, tipo, ano):
    if ano == 'Todos':
        # Sem filtro de ano: usa a base inteira (1992 a 2020)
        base = df
        periodo = 'de 1992 a 2020'
    else:
        # Com filtro de ano: fica só com as linhas daquele ano olímpico
        base = df[df['Year'] == ano]
        periodo = f"em {ano} (sede: {sedes.loc[ano, 'Host_country']})"

    # Pega só as linhas do país escolhido e soma cada tipo de medalha
    totais = base[base['Country_Name'] == pais][['Gold', 'Silver', 'Bronze']].sum()

    # Monta uma tabelinha com 3 linhas (uma para cada medalha) que o gráfico vai usar.
    # int() converte o número do numpy para um inteiro normal do Python.
    df_pizza = pd.DataFrame({
        'Medalha':    ['Ouro', 'Prata', 'Bronze'],
        'Quantidade': [int(totais['Gold']), int(totais['Silver']), int(totais['Bronze'])],
    })

    # Se o país não ganhou nenhuma medalha naquele ano, a pizza ficaria vazia.
    # Então avisamos isso no título.
    if df_pizza['Quantidade'].sum() == 0:
        titulo = f'{pais} não ganhou medalhas {periodo}'
    else:
        titulo = f'Medalhas de {pais} {periodo}'

    # Cria a pizza: names = nome de cada fatia / values = tamanho de cada fatia
    pie_fig = px.pie(
        df_pizza,
        names='Medalha',
        values='Quantidade',
        color='Medalha',                          # pinta cada fatia de acordo com a medalha
        color_discrete_map=CORES_DA_PIZZA,        # ouro = dourado, prata = cinza, bronze = bronze
        title=titulo,
    )

    # Mostra o número E a porcentagem dentro de cada fatia
    pie_fig.update_traces(textinfo='value+percent')

    # A fatia da medalha escolhida no filtro "salta" para fora (no 'Todos' nenhuma salta).
    # A pizza sempre mostra as 3 medalhas, o filtro só destaca uma.
    pie_fig.update_traces(pull=[0.12 if nome == tipo else 0 for nome in df_pizza['Medalha']])
    return pie_fig



# Cria o aplicativo Dash (o painel que vai juntar os gráficos)
app = Dash(__name__, title='Quadro de Medalhas Olímpicas')

# IMPORTANTE PARA O RENDER: "server" é o servidor web que fica dentro do Dash.
# O Render roda o comando "gunicorn app:server", que procura exatamente esta variável.
server = app.server

# Define o layout: filtros em cima, depois o mapa, depois área e barras lado a lado, e a pizza no final
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif', 'padding': '10px'}, children=[

    # Título principal da página
    html.H1('Quadro de Medalhas Olímpicas de Verão (1992 a 2020)', style={'textAlign': 'center'}),

    # Barra de filtros: os dois filtros lado a lado (display flex)
    html.Div(style={'display': 'flex', 'gap': '40px', 'flexWrap': 'wrap', 'justifyContent': 'center',
                    'backgroundColor': '#f2f2f2', 'padding': '10px', 'borderRadius': '8px'}, children=[

        # FILTRO GLOBAL: tipo de medalha (vale para o mapa, a área e as barras)
        html.Div([
            html.Label('Tipo de medalha (mapa, área e barras):', style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='filtro-medalha',                          # id: nome que os callbacks usam para achar este filtro
                options=['Todos', 'Ouro', 'Prata', 'Bronze'],
                value='Todos',                                # valor que já vem marcado quando a página abre
                inline=True,                                  # deixa as opções na mesma linha
                inputStyle={'marginLeft': '12px', 'marginRight': '4px'},
            ),
        ]),

        # FILTRO DE ANO: vale só para o gráfico de barras
        html.Div([
            html.Label('Ano olímpico / país sede (barras):', style={'fontWeight': 'bold'}),
            dcc.Dropdown(id='filtro-ano', options=OPCOES_ANO, value='Todos',
                         clearable=False, style={'width': '320px'}),   # clearable=False: n deixa o usuário esvaziar o filtro
        ]),
    ]),

    # Primeiro o mapa. O style (da Etapa 5 do tutorial) faz ele ocupar 50% da altura da tela e 100% da largura
    dcc.Graph(id='map', style={'height': '50vh', 'width': '100%'}),

    # Esta Div agrupa os dois gráficos da segunda linha
    html.Div([
        dcc.Graph(id='area-chart', style={'flex': '1'}),      # flex 1: cada gráfico ocupa metade da linha
        dcc.Graph(id='bar-chart', style={'flex': '1'}),
    ], style={'display': 'flex'}),                            # flex = coloca um gráfico ao lado do outro

    # Pizza com os seus próprios filtros: país e ano
    html.Div(style={'marginTop': '20px'}, children=[
        html.Div(style={'display': 'flex', 'gap': '40px', 'flexWrap': 'wrap'}, children=[
            html.Div([
                html.Label('Escolha um país para ver a pizza de medalhas:', style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='filtro-pais', options=PAISES, value='United States of America',
                             clearable=False, style={'width': '320px'}),
            ]),
            html.Div([
                html.Label('Ano olímpico / país sede (pizza):', style={'fontWeight': 'bold'}),
                dcc.Dropdown(id='filtro-ano-pizza', options=OPCOES_ANO, value='Todos',
                             clearable=False, style={'width': '320px'}),   # usa as mesmas opções de ano das barras
            ]),
        ]),
        dcc.Graph(id='pie-chart'),
    ]),
])



# CALLBACKS: ligam os filtros aos gráficos.
# Quando o usuário muda um Input, o Dash chama a função e coloca a figura nova no Output.
# A ORDEM dos parâmetros da função segue a ORDEM dos Inputs.

# Callback 1: o filtro de medalha atualiza o MAPA e a ÁREA ao mesmo tempo (2 saídas = a função devolve 2 figuras)
@app.callback(
    Output('map', 'figure'),
    Output('area-chart', 'figure'),
    Input('filtro-medalha', 'value'),
)
def atualizar_mapa_e_area(tipo):
    return criar_mapa(tipo), criar_area(tipo)


# Callback 2: o filtro de medalha E o filtro de ano atualizam as BARRAS
@app.callback(
    Output('bar-chart', 'figure'),
    Input('filtro-medalha', 'value'),
    Input('filtro-ano', 'value'),
)
def atualizar_barras(tipo, ano):
    return criar_barras(tipo, ano)


# Callback 3: o filtro de país, o de medalha E o de ano da pizza atualizam a PIZZA (3 entradas)
@app.callback(
    Output('pie-chart', 'figure'),
    Input('filtro-pais', 'value'),
    Input('filtro-medalha', 'value'),
    Input('filtro-ano-pizza', 'value'),
)
def atualizar_pizza(pais, tipo, ano):
    return criar_pizza(pais, tipo, ano)



# Só pra testar
if __name__ == '__main__':
    print(df.groupby('Country_Name')['Total_Medals'].sum().nlargest(10))   # top 10 do mapa
    # Inicia o servidor local. Depois abra http://127.0.0.1:8050 no navegador.
    # (O tutorial usa app.run_server(), que nas versões novas do Dash virou app.run().)
    app.run(debug=False)    # com debug=True aparecem as mensagens de erro na tela
