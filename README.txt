DASHBOARD - QUADRO DE MEDALHAS OLIMPICAS (JOGOS DE VERAO, 1992-2020)
Disciplina: Visualizacao de Dados - IF Sudeste MG
Dupla: Glauco Roberto Berbert Souza Costa

LINK DO DASHBOARD NO RENDER:
https://dashboard-olimpiadas-qkkv.onrender.com/

REPOSITORIO NO GITHUB:
https://github.com/glaucoberbert/dashboard_olimpiadas

ARQUIVOS
- app.py                     codigo-fonte do dashboard (Dash + Plotly Express), comentado
- Summer_olympic_Medals.csv  base de dados original disponibilizada pelo professor
- requirements.txt           bibliotecas necessarias (usado pelo Render)

O QUE O DASHBOARD TEM
- Mapa com o total de medalhas por pais (verde = mais medalhas, vermelho = menos)
- Grafico de areas empilhadas com o top 10 paises ao longo dos anos
- Grafico de barras com o top 10 paises
- Grafico de pizza: escolhe o pais e mostra o total de Ouro, Prata e Bronze
- Filtro de tipo de medalha (Ouro, Prata, Bronze ou Todos): atua no mapa, na area e nas barras
- Filtro de ano olimpico (pais sede): atua no grafico de barras

COMO RODAR NO COMPUTADOR
1) py -m pip install -r requirements.txt
2) py app.py
3) abrir http://127.0.0.1:8050 no navegador
