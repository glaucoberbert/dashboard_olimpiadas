# DASHBOARD - QUADRO DE MEDALHAS OLÍMPICAS
# Disciplina: Visualização de Dados
# Aluno: Glauco Roberto Berbert Souza Costa 

# ETAPA 1 -> Baixando e limpando o conjunto de dados "Olympic Medals by Country"

import os                      # os: ajuda a achar o caminho do arquivo CSV
import pandas as pd            # pandas: biblioteca para trabalhar com tabelas (DataFrames)

# Descobre a pasta onde este arquivo (app.py) está salvo.
# Assim o programa acha o CSV mesmo quando for executado de outro lugar (como no Render).
PASTA_DO_ARQUIVO = os.path.dirname(os.path.abspath(__file__))

# Monta o caminho completo até o arquivo lá do CSV (que eu coloquei na mesma pasta do app.py)
CAMINHO_CSV = os.path.join(PASTA_DO_ARQUIVO, 'Summer_olympic_Medals.csv')

# Lê o arquivo CSV e guarda no DataFrame
# OBS: o tutorial usa sep=';', mas o nosso arquivo é separado por VÍRGULA (o padrão do pandas),
# por isso eu n informei o sep
df = pd.read_csv(CAMINHO_CSV)

# Troca 'United States' por 'United States of America' na coluna Country_Name.
# Motivo: o tutorial pede essa troca, Assim todas as linhas dos EUA ficam com o mesmo nome,
# e as somas (mapa, área e barras) não separam o país em dois nomes.
df['Country_Name'] = df['Country_Name'].replace('United States', 'United States of America')


# Só pra testar

if __name__ == '__main__':
    print(df.head())                                                    # mostra as 5 primeiras linhas
    print('Linhas e colunas:', df.shape)                                # esperado: (1344, 8)
    print('Ainda existe "United States"?', (df['Country_Name'] == 'United States').any())    # esperado: False
    print('Linhas com "United States of America":', (df['Country_Name'] == 'United States of America').sum())  # esperado: 28

