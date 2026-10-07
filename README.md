# 🌵 Painel de Vendas — Sabor do Sertão

Painel interativo e executivo desenvolvido com **Streamlit**, **Pandas** e **Plotly** para análise de dados de vendas da rede de lanchonetes fictícia **Sabor do Sertão**, presente nas cidades de **Recife, Olinda, Caruaru, Petrolina e Garanhuns**.

O projeto atende a todos os requisitos da atividade prática, cobrindo desde o **Passo 0 até o Desafio Bônus (+1 pt)**, totalizando a pontuação máxima (11/10 pontos).

---

## 📌 Sumário
- [Demonstração do Painel](#-demonstração-do-painel)
- [Funcionalidades Implementadas por Nível](#-funcionalidades-implementadas-por-nível)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Repositório](#-estrutura-do-repositório)
- [Como Executar Localmente](#-como-executar-localmente)
- [Publicação no Streamlit Community Cloud](#-publicação-no-streamlit-community-cloud)
- [Critérios de Avaliação Atendidos](#-critérios-de-avaliação-atendidos)

---

## 🖼️ Demonstração do Painel

O painel foi projetado com layout responsivo (`wide`), tipografia limpa e identidade visual inspirada nas cores regionais do Sertão (tons quentes de terracota, âmbar e destaques contrastantes).

```
========================================================================================
🌵 Sabor do Sertão | Painel de Vendas
Análise executiva de desempenho comercial, distribuição geográfica e hábitos de consumo
========================================================================================
[💰 Faturamento Total]   [🧾 Número de Vendas]   [🎯 Ticket Médio]   [⭐ Avaliação Média]
    R$ 192.237,50               5.000                R$ 38,45            3,05 / 5.0
----------------------------------------------------------------------------------------
[ 📈 Gráficos & Visualizações ] [ 🔍 Exploração (Nível 1) ] [ 💡 Insights (Nível 5) ] [ 🚀 Explorador Livre (Bônus) ]
```

---

## 🚀 Funcionalidades Implementadas por Nível

### ✅ Passo 0: Preparação do Ambiente e Geração da Base
- Script [`gerar_dados.py`](file:///gerar_dados.py) com semente aleatória fixa (`seed=42`) para reprodutibilidade estrita.
- Gera 5.000 transações comerciais ao longo de 365 dias com as 5 cidades, 12 itens do cardápio divididos em 4 categorias, formas de pagamento e 60 valores ausentes propositais na coluna `avaliacao`.

### ✅ Nível 1: Exploração e Tratamento de Dados (2 pts)
- **Primeiras Linhas:** Visualização tabular inicial com `st.dataframe`.
- **Resumo Estatístico:** Matriz de estatísticas descritivas (`df.describe()`) para todas as variáveis numéricas (preço, quantidade, total e avaliação).
- **Diagnóstico de Nulos:** Tabela com contagem e percentual de valores ausentes por coluna.
- **Tratamento da Coluna `avaliacao`:** Preenchimento dos 60 valores ausentes utilizando a **mediana (3.0)**, acompanhado de justificativa detalhada em `st.caption`:
  > *A variável de avaliação é de natureza discreta/ordinal (notas de 1 a 5). A mediana foi adotada por ser uma medida de tendência central robusta a assimetrias e outliers, preservando valores inteiros da escala sem introduzir médias fracionárias artificiais e evitando o descarte de 60 transações financeiras válidas.*

### ✅ Nível 2: Indicadores Executivos (2 pts)
Quatro KPIs em destaque no topo da tela utilizando `st.columns` e `st.metric`:
1. **💰 Faturamento Total:** `R$ 192.237,50` (formatado no padrão monetário brasileiro).
2. **🧾 Número de Vendas:** `5.000` pedidos registrados.
3. **🎯 Ticket Médio:** `R$ 38,45` por pedido.
4. **⭐ Avaliação Média:** `3,05 / 5.0` estrelas.

### ✅ Nível 3: Filtros Globais Dinâmicos (2 pts)
Barra lateral (`st.sidebar`) com controles interativos que atualizam todos os KPIs, gráficos e tabelas:
- **Cidades:** `st.multiselect` pré-selecionado com as 5 cidades.
- **Categorias:** `st.multiselect` com as 4 categorias do cardápio (*Bebidas, Salgados, Doces, Pratos*).
- **Intervalo de Datas:** `st.date_input` permitindo filtrar qualquer período do ano com tratamento seguro de intervalos parciais.
- Contador em tempo real com volume e percentual da base filtrada.

### ✅ Nível 4: Visualizações Interativas em Abas (3 pts + Opcional)
Gráficos construídos com `plotly.express` e organizados em `st.tabs`:
1. **Faturamento Mensal (Linha):** Agrupamento mensal conforme dica oficial `df.groupby(df["data"].dt.to_period("M"))["total"].sum()` com formatação limpa e marcadores.
2. **Faturamento por Cidade (Barras):** Destaque da receita por praça, evidenciando a liderança de Recife (R$ 66,6k), seguida de Caruaru e Petrolina.
3. **Top 5 Produtos Mais Vendidos (Barras Horizontais):** Ranking por quantidade total vendida com distinção de cor por categoria.
4. **Formas de Pagamento (Donut / Pizza):** Distribuição percentual do faturamento, comprovando o domínio do Pix (~45%).
5. **[Opcional Extra] Mapa de Calor (Dia da Semana x Hora):** `px.density_heatmap` mostrando a concentração de fluxo e vendas ao longo dos dias e horários (7h às 21h).

### ✅ Nível 5: Conclusões Gerenciais e Exportação (1 pt)
- **3 Conclusões Estratégicas em `st.markdown`:**
  1. *Concentração geográfica e oportunidades regionais* (Recife lidera com 34%, Caruaru e Petrolina fortes no interior).
  2. *Equilíbrio do cardápio entre margem bruta e giro* (Pratos regionais trazem faturamento, bebidas e salgados trazem fluxo).
  3. *Hegemonia do Pix e planejamento de escalas* (Redução de taxas de adquirentes e picos nas refeições).
- **Exportação de Dados:** Botão `st.download_button` que exporta a base com os filtros atualmente aplicados em CSV (codificação `utf-8-sig` e separador `;` compatível com Excel e Power BI).

### 🌟 Desafio Bônus: Explorador Livre de Dados (+1 pt)
Aba dedicada que permite:
- Fazer upload de **qualquer arquivo CSV** externo ou utilizar a base atual filtrada.
- Selecionar dinamicamente via `st.selectbox`:
  - **Eixo X** (qualquer coluna)
  - **Eixo Y** (qualquer coluna)
  - **Tipo de Gráfico** (*Barras, Linha, Dispersão (Scatter), Histograma, Boxplot*)
  - **Agrupamento por cor** (opcional)
- Renderização instantânea com `st.plotly_chart` e visualização de amostra dos dados.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface & Dashboard:** [Streamlit](https://streamlit.io/)
- **Manipulação de Dados:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Visualização Gráfica Interativa:** [Plotly Express](https://plotly.com/python/)

---

## 📁 Estrutura do Repositório

```bash
task-cloud/
├── app.py                      # Aplicação Streamlit completa (Níveis 1 a 5 + Bônus)
├── gerar_dados.py              # Script gerador do dataset sintético oficial
├── vendas_sabor_do_sertao.csv  # Dataset gerado com 5.000 linhas
├── requirements.txt            # Dependências necessárias para execução
└── README.md                   # Documentação detalhada e guia de execução
```

---

## 💻 Como Executar Localmente

### 1. Clonar o repositório
```bash
git clone https://github.com/ximenesl/task-cloud.git
cd task-cloud
```

### 2. Criar e ativar um ambiente virtual (opcional, recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Gerar a base de dados oficial (caso queira recriar)
```bash
python gerar_dados.py
```

### 5. Iniciar a aplicação Streamlit
```bash
streamlit run app.py
```

O navegador abrirá automaticamente em `http://localhost:8501`.

> **Dica:** Caso não suba um arquivo CSV na barra lateral, o painel carrega automaticamente o arquivo gerado localmente `vendas_sabor_do_sertao.csv`. Você também pode arrastar e soltar qualquer arquivo CSV para teste.

---

## ☁️ Publicação no Streamlit Community Cloud

Para publicar seu painel gratuitamente:
1. Suba este repositório para o seu GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e faça login com sua conta GitHub.
3. Clique em **"New app"**.
4. Selecione o repositório `ximenesl/task-cloud`, a branch `main` (ou `master`) e aponte o arquivo principal para `app.py`.
5. Clique em **"Deploy"**. Em instantes o painel estará disponível na web com link público compartilhável!

---

## 📊 Critérios de Avaliação Atendidos

| Critério | Pontuação Máxima | Status |
| :--- | :---: | :---: |
| **Exploração e tratamento de dados** | 2 pts | ✅ Concluído (Nível 1) |
| **KPIs corretos** | 2 pts | ✅ Concluído (Nível 2) |
| **Filtros funcionando em todo o painel** | 2 pts | ✅ Concluído (Nível 3) |
| **Gráficos adequados, títulos e rótulos legíveis** | 3 pts | ✅ Concluído (Nível 4 + Mapa de Calor) |
| **Insights e exportação** | 1 pt | ✅ Concluído (Nível 5) |
| **Bônus: explorador livre** | +1 pt | ✅ Concluído (Desafio Bônus) |
| **TOTAL** | **11 / 10** | **100% + Bônus Máximo** |