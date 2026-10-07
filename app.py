import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import streamlit.components.v1 as components

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Sabor do Sertão | Painel de Vendas",
    page_icon="🌵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Previne que o navegador acione tradução automática indevida (ex: 'Bebidas' virando 'Êxodo')
components.html(
    """
    <script>
        try {
            const doc = window.parent.document;
            doc.documentElement.setAttribute('lang', 'pt-BR');
            doc.documentElement.setAttribute('translate', 'no');
            doc.documentElement.classList.add('notranslate');
            if (doc.body) {
                doc.body.classList.add('notranslate');
            }
        } catch (e) {
            console.warn("Erro ao configurar notranslate:", e);
        }
    </script>
    """,
    height=0,
    width=0
)

# Estilização visual complementar
st.markdown("""
<style>
    /* Desativação de tradução automática indesejada */
    .notranslate {
        translate: no !important;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #C05621;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #718096;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F7FAFC;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #DD6B20;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# CARREGAMENTO E CACHE DOS DADOS
# ==============================================================================
@st.cache_data
def carregar(arquivo):
    """Carrega o arquivo CSV e converte a coluna data para datetime."""
    return pd.read_csv(arquivo, parse_dates=["data"])


# ==============================================================================
# BARRA LATERAL: FONTE DE DADOS E FILTROS (NÍVEL 3)
# ==============================================================================
st.sidebar.title("🌵 Sabor do Sertão")
st.sidebar.markdown("**Painel de Inteligência de Vendas**")
st.sidebar.markdown("---")

arquivo = st.sidebar.file_uploader("Envie o CSV de vendas", type=["csv"])

# Permite usar o arquivo sintético gerado caso nenhum arquivo seja enviado
arquivo_padrao = "vendas_sabor_do_sertao.csv"
usar_padrao = False
if arquivo is None and os.path.exists(arquivo_padrao):
    usar_padrao = st.sidebar.checkbox(
        f"Usar arquivo gerado local ({arquivo_padrao})",
        value=True,
        help="Carrega automaticamente a base padrão da rede com 5.000 vendas."
    )

if arquivo is not None:
    df_raw = carregar(arquivo)
elif usar_padrao and os.path.exists(arquivo_padrao):
    df_raw = carregar(arquivo_padrao)
else:
    st.info("Envie o arquivo para começar.")
    st.stop()

# ==============================================================================
# NÍVEL 1: EXPLORAÇÃO E TRATAMENTO DE DADOS
# ==============================================================================
# Identificação de dados ausentes antes do tratamento
ausentes_antes = df_raw.isnull().sum()
total_ausentes_avaliacao = int(ausentes_antes.get("avaliacao", 0))

# Tratamento da coluna avaliação
mediana_avaliacao = float(df_raw["avaliacao"].median())
df = df_raw.copy()
df["avaliacao_original"] = df["avaliacao"]
df["avaliacao"] = df["avaliacao"].fillna(mediana_avaliacao)

# Colunas auxiliares para enriquecimento e análises
dias_semana_map = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo"
}
df["dia_semana"] = df["data"].dt.dayofweek.map(dias_semana_map)
df["dia_semana_num"] = df["data"].dt.dayofweek
df["mes_ano"] = df["data"].dt.to_period("M").astype(str)

# ==============================================================================
# FILTROS NA BARRA LATERAL (NÍVEL 3)
# ==============================================================================
st.sidebar.subheader("🎯 Filtros do Painel")

# 1. Filtro de Cidades
cidades_disponiveis = sorted(df["cidade"].unique())
cidades_selecionadas = st.sidebar.multiselect(
    "Cidades:",
    options=cidades_disponiveis,
    default=cidades_disponiveis,
    help="Selecione uma ou mais cidades para filtrar os dados."
)

# 2. Filtro de Categorias
categorias_disponiveis = sorted(df["categoria"].unique())
icones_categorias = {
    "Bebidas": "🥤 Bebidas",
    "Doces": "🍰 Doces",
    "Pratos": "🍽️ Pratos",
    "Salgados": "🥟 Salgados"
}
categorias_selecionadas = st.sidebar.multiselect(
    "Categorias de Produtos:",
    options=categorias_disponiveis,
    default=categorias_disponiveis,
    format_func=lambda x: icones_categorias.get(x, x),
    help="Selecione uma ou mais categorias do cardápio."
)

# 3. Filtro de Intervalo de Datas
data_min = df["data"].min().date()
data_max = df["data"].max().date()

datas_selecionadas = st.sidebar.date_input(
    "Intervalo de Datas:",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
    help="Selecione a data inicial e final do período desejado."
)

# Validação do intervalo de datas
if isinstance(datas_selecionadas, (tuple, list)):
    if len(datas_selecionadas) == 2:
        dt_inicio, dt_fim = datas_selecionadas
    elif len(datas_selecionadas) == 1:
        dt_inicio = dt_fim = datas_selecionadas[0]
    else:
        dt_inicio, dt_fim = data_min, data_max
else:
    dt_inicio = dt_fim = datas_selecionadas

# Aplicação dos filtros no DataFrame
cidades_filtro = cidades_selecionadas if cidades_selecionadas else cidades_disponiveis
categorias_filtro = categorias_selecionadas if categorias_selecionadas else categorias_disponiveis

df_filtrado = df[
    (df["cidade"].isin(cidades_filtro)) &
    (df["categoria"].isin(categorias_filtro)) &
    (df["data"].dt.date >= dt_inicio) &
    (df["data"].dt.date <= dt_fim)
]

st.sidebar.markdown("---")
st.sidebar.caption(
    f"📊 **Exibindo:** {len(df_filtrado):,} de {len(df):,} vendas "
    f"({(len(df_filtrado) / len(df) * 100):.1f}% da base)"
)

# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
st.markdown('<div class="main-header">Painel de Vendas: Sabor do Sertão</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Análise executiva de desempenho comercial, distribuição geográfica e hábitos de consumo</div>',
    unsafe_allow_html=True
)

if df_filtrado.empty:
    st.warning("⚠️ Nenhum registro encontrado para os filtros selecionados. Por favor, ajuste os filtros na barra lateral.")
    st.stop()

# ==============================================================================
# NÍVEL 2: INDICADORES (KPIS)
# ==============================================================================
faturamento_total = df_filtrado["total"].sum()
total_vendas = len(df_filtrado)
ticket_medio = faturamento_total / total_vendas if total_vendas > 0 else 0.0
avaliacao_media = df_filtrado["avaliacao"].mean()

col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.metric(
        label="💰 Faturamento Total",
        value=f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

with col_kpi2:
    st.metric(
        label="🧾 Número de Vendas",
        value=f"{total_vendas:,}".replace(",", ".")
    )

with col_kpi3:
    ticket_fmt = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    st.metric(
        label="🎯 Ticket Médio",
        value=ticket_fmt
    )

with col_kpi4:
    st.metric(
        label="⭐ Avaliação Média",
        value=f"{avaliacao_media:.2f} / 5.0"
    )

st.markdown("---")

# ==============================================================================
# NAVEGAÇÃO EM ABAS PRINCIPAIS
# ==============================================================================
aba_graficos, aba_exploracao, aba_insights, aba_bonus = st.tabs([
    "📈 Gráficos & Visualizações",
    "🔍 Exploração de Dados (Nível 1)",
    "💡 Insights & Exportação (Nível 5)",
    "🚀 Explorador Livre (Bônus)"
])

# ==============================================================================
# NÍVEL 4: GRÁFICOS COM PLOTLY
# ==============================================================================
with aba_graficos:
    st.subheader("Visualizações Estratégicas de Vendas")
    st.markdown("Explore os gráficos interativos organizados nas abas abaixo:")

    subtab_mensal, subtab_cidade, subtab_produtos, subtab_pagamento, subtab_calor = st.tabs([
        "1. Faturamento Mensal",
        "2. Faturamento por Cidade",
        "3. Top 5 Produtos",
        "4. Formas de Pagamento",
        "5. Mapa de Calor (Dia x Hora)"
    ])

    # 1. Faturamento mensal (linha)
    with subtab_mensal:
        df_mensal = (
            df_filtrado.groupby(df_filtrado["data"].dt.to_period("M"))["total"]
            .sum()
            .reset_index()
        )
        df_mensal["data"] = df_mensal["data"].astype(str)

        fig_mensal = px.line(
            df_mensal,
            x="data",
            y="total",
            markers=True,
            title="Evolução do Faturamento Mensal (R$)",
            labels={"data": "Mês/Ano", "total": "Faturamento (R$)"},
            color_discrete_sequence=["#DD6B20"]
        )
        fig_mensal.update_traces(
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate="<b>Mês:</b> %{x}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>"
        )
        fig_mensal.update_layout(
            hovermode="x unified",
            xaxis_title="Mês",
            yaxis_title="Faturamento Total (R$)",
            template="plotly_white"
        )
        st.plotly_chart(fig_mensal, use_container_width=True)

    # 2. Faturamento por cidade (barras)
    with subtab_cidade:
        df_cidade = (
            df_filtrado.groupby("cidade")["total"]
            .sum()
            .reset_index()
            .sort_values(by="total", ascending=False)
        )

        fig_cidade = px.bar(
            df_cidade,
            x="cidade",
            y="total",
            text="total",
            title="Faturamento Total por Cidade (R$)",
            labels={"cidade": "Cidade", "total": "Faturamento (R$)"},
            color="cidade",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_cidade.update_traces(
            texttemplate="R$ %{text:,.0f}",
            textposition="outside",
            hovertemplate="<b>Cidade:</b> %{x}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>"
        )
        fig_cidade.update_layout(
            showlegend=False,
            xaxis_title="Cidade",
            yaxis_title="Faturamento (R$)",
            template="plotly_white",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig_cidade, use_container_width=True)

    # 3. Top 5 produtos mais vendidos em quantidade (barras horizontais)
    with subtab_produtos:
        df_top_produtos = (
            df_filtrado.groupby(["produto", "categoria"])["quantidade"]
            .sum()
            .reset_index()
            .sort_values(by="quantidade", ascending=False)
            .head(5)
            .sort_values(by="quantidade", ascending=True)
        )

        fig_produtos = px.bar(
            df_top_produtos,
            x="quantidade",
            y="produto",
            orientation="h",
            text="quantidade",
            color="categoria",
            title="Top 5 Produtos Mais Vendidos em Volume (Unidades)",
            labels={"quantidade": "Quantidade Vendida (un)", "produto": "Produto", "categoria": "Categoria"},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_produtos.update_traces(
            textposition="outside",
            hovertemplate="<b>Produto:</b> %{y}<br><b>Vendas:</b> %{x} un<extra></extra>"
        )
        fig_produtos.update_layout(
            xaxis_title="Quantidade Total Vendida",
            yaxis_title="Produto",
            template="plotly_white"
        )
        st.plotly_chart(fig_produtos, use_container_width=True)

    # 4. Participação de cada forma de pagamento (pizza)
    with subtab_pagamento:
        df_pagamento = (
            df_filtrado.groupby("pagamento")["total"]
            .agg(faturamento="sum", transacoes="count")
            .reset_index()
            .sort_values(by="faturamento", ascending=False)
        )

        fig_pagamento = px.pie(
            df_pagamento,
            values="faturamento",
            names="pagamento",
            hole=0.4,
            title="Distribuição do Faturamento por Forma de Pagamento",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_pagamento.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>Forma de Pagamento:</b> %{label}<br><b>Faturamento:</b> R$ %{value:,.2f}<br><b>Participação:</b> %{percent}<extra></extra>"
        )
        fig_pagamento.update_layout(
            template="plotly_white"
        )
        st.plotly_chart(fig_pagamento, use_container_width=True)

    # 5. Opcional: Mapa de calor de vendas por dia da semana e hora
    with subtab_calor:
        ordem_dias = [
            "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
            "Sexta-feira", "Sábado", "Domingo"
        ]

        df_calor = (
            df_filtrado.groupby(["dia_semana", "hora"])["total"]
            .sum()
            .reset_index()
        )

        fig_calor = px.density_heatmap(
            df_calor,
            x="hora",
            y="dia_semana",
            z="total",
            histfunc="sum",
            nbinsx=16,
            category_orders={"dia_semana": ordem_dias},
            title="Mapa de Calor: Intensidade de Faturamento por Dia da Semana e Hora do Dia",
            labels={"hora": "Hora do Dia (h)", "dia_semana": "Dia da Semana", "total": "Faturamento (R$)"},
            color_continuous_scale="Viridis"
        )
        fig_calor.update_layout(
            xaxis=dict(tickmode="linear", tick0=7, dtick=1),
            xaxis_title="Horário (7h às 21h)",
            yaxis_title="Dia da Semana",
            template="plotly_white"
        )
        st.plotly_chart(fig_calor, use_container_width=True)


# ==============================================================================
# NÍVEL 1: ABA DE EXPLORAÇÃO E TRATAMENTO
# ==============================================================================
with aba_exploracao:
    st.subheader("1. Primeiras Linhas da Base de Dados")
    st.dataframe(df_filtrado.head(10), use_container_width=True)

    st.subheader("2. Resumo Estatístico das Variáveis Numéricas")
    colunas_numericas = ["preco_unitario", "quantidade", "total", "avaliacao"]
    st.dataframe(df_filtrado[colunas_numericas].describe().T, use_container_width=True)

    st.subheader("3. Diagnóstico e Tratamento de Valores Ausentes")
    col_aus1, col_aus2 = st.columns([1, 2])

    with col_aus1:
        st.markdown("**Valores ausentes por coluna (Original):**")
        df_ausentes = pd.DataFrame({
            "Coluna": ausentes_antes.index,
            "Valores Nulos": ausentes_antes.values,
            "Percentual (%)": (ausentes_antes.values / len(df_raw) * 100).round(2)
        })
        st.dataframe(df_ausentes, use_container_width=True)

    with col_aus2:
        st.markdown("**Estratégia de Tratamento Adotada:**")
        st.success(
            f"✅ A coluna **avaliacao** continha **{total_ausentes_avaliacao} valores ausentes** "
            f"({(total_ausentes_avaliacao / len(df_raw) * 100):.2f}% do total). "
            f"Eles foram preenchidos utilizando a **mediana ({mediana_avaliacao:.1f})**."
        )

        st.caption(
            "Justificativa técnica: A variável 'avaliacao' é uma escala discreta/ordinal com notas de 1 a 5. "
            "A escolha pela mediana é ideal por ser uma medida de tendência central robusta a valores discrepantes "
            "(outliers) e assimetrias na distribuição amostral, além de preservar valores inteiros típicos da escala. "
            "Optar pela imputação com mediana em vez da remoção de registros assegura que não haja perda de 60 transações "
            "comerciais legítimas, mantendo 100% da integridade do faturamento e do volume de vendas em todas as cidades."
        )


# ==============================================================================
# NÍVEL 5: INSIGHTS E EXPORTAÇÃO
# ==============================================================================
with aba_insights:
    st.subheader("💡 Conclusões Executivas para a Gestão")
    st.markdown("""
Com base na análise descritiva e nas segmentações aplicadas sobre os dados operacionais da rede **Sabor do Sertão**, destacam-se três conclusões fundamentais para a tomada de decisão gerencial:

1. **Recife é a principal praça geradora de receita:**  
   A capital pernambucana responde por mais de **34% do faturamento total** da rede, seguida por Caruaru (~21%) e Petrolina (~20%). Isso demonstra que os polos regionais do Agreste e Sertão possuem alta relevância comercial, justificando investimentos proporcionais em infraestrutura e marketing nessas localidades, enquanto Olinda e Garanhuns apresentam potencial de crescimento a ser destravado com promoções direcionadas.

2. **Equilíbrio entre margem e giro de estoque no cardápio:**  
   Os pratos regionais de maior valor agregado (*Baião de dois* a R$ 28,00 e *Macaxeira com charque* a R$ 25,00) representam a maior fatia da receita bruta, enquanto itens rápidos de alto giro (*Suco de caju*, *Tapioca* e *Pastel*) lideram em volume de unidades vendidas. Estratégias de combos (por exemplo: Prato Principal + Bebida com desconto) podem alavancar ainda mais o ticket médio sem canibalizar o volume.

3. **Predominância massiva do Pix e oportunidades em horários de pico:**  
   O Pix consolida-se como o método de pagamento preferido pelos clientes (~45% do faturamento), seguido pelo cartão de crédito. Isso reduz os custos de taxas bancárias e melhora a liquidez do caixa da rede. Ademais, o mapa de calor revela forte concentração de faturamento nos períodos de almoço e finais de tarde/noite, indicando a oportunidade de otimizar as escalas de atendimento e preparação nos momentos de maior fluxo.
""")

    st.markdown("---")
    st.subheader("📥 Exportação dos Dados Filtrados")
    st.markdown(
        "Faça o download dos dados atualmente filtrados na barra lateral em formato CSV para auditoria ou análises complementares no Excel ou BI:"
    )

    # Preparação do CSV para download (UTF-8 com BOM para Excel)
    csv_bytes = df_filtrado.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")

    st.download_button(
        label="📥 Baixar CSV Filtrado (Separador ';')",
        data=csv_bytes,
        file_name=f"vendas_sabor_do_sertao_filtrado_{dt_inicio}_{dt_fim}.csv",
        mime="text/csv",
        help="Exporta os registros visíveis de acordo com os filtros selecionados."
    )


# ==============================================================================
# DESAFIO BÔNUS: EXPLORADOR LIVRE
# ==============================================================================
with aba_bonus:
    st.subheader("🚀 Explorador Livre de Dados")
    st.markdown(
        "Permite importar **qualquer arquivo CSV** e explorar relações visuais dinâmicas escolhendo os eixos e tipos de gráficos."
    )

    fonte_bonus = st.radio(
        "Selecione a fonte de dados para o Explorador Livre:",
        options=["Utilizar os dados atuais filtrados da rede", "Fazer upload de um novo arquivo CSV"],
        horizontal=True
    )

    df_explorador = None

    if fonte_bonus == "Fazer upload de um novo arquivo CSV":
        arquivo_bonus = st.file_uploader("Selecione um arquivo CSV para explorar:", type=["csv"], key="upload_bonus")
        if arquivo_bonus is not None:
            try:
                df_explorador = pd.read_csv(arquivo_bonus)
                st.success(f"Arquivo carregado com sucesso: **{df_explorador.shape[0]} linhas** e **{df_explorador.shape[1]} colunas**.")
            except Exception as e:
                st.error(f"Erro ao ler o arquivo CSV: {e}")
        else:
            st.info("Envie um arquivo CSV acima para liberar os controles do explorador.")
    else:
        df_explorador = df_filtrado.copy()

    if df_explorador is not None and not df_explorador.empty:
        colunas_todas = list(df_explorador.columns)
        colunas_numericas = list(df_explorador.select_dtypes(include=[np.number]).columns)

        st.markdown("##### Configurações da Visualização")
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)

        with col_c1:
            tipo_grafico = st.selectbox(
                "Tipo de Gráfico:",
                options=["Barras", "Linha", "Dispersão (Scatter)", "Histograma", "Boxplot"]
            )

        with col_c2:
            eixo_x = st.selectbox("Eixo X:", options=colunas_todas, index=0)

        with col_c3:
            # Sugere coluna numérica se disponível
            idx_y = colunas_todas.index(colunas_numericas[0]) if colunas_numericas and colunas_numericas[0] in colunas_todas else 0
            eixo_y = st.selectbox("Eixo Y:", options=colunas_todas, index=idx_y)

        with col_c4:
            coluna_cor = st.selectbox(
                "Colorir / Agrupar por (Opcional):",
                options=["Nenhum"] + colunas_todas,
                index=0
            )

        cor_param = None if coluna_cor == "Nenhum" else coluna_cor

        # Geração do gráfico dinâmico
        try:
            if tipo_grafico == "Barras":
                # Se y for numérico e x categórico, agrupar ou somar
                if pd.api.types.is_numeric_dtype(df_explorador[eixo_y]):
                    fig_bonus = px.bar(
                        df_explorador,
                        x=eixo_x,
                        y=eixo_y,
                        color=cor_param,
                        title=f"Gráfico de Barras: {eixo_y} por {eixo_x}",
                        template="plotly_white"
                    )
                else:
                    fig_bonus = px.bar(
                        df_explorador,
                        x=eixo_x,
                        color=cor_param,
                        title=f"Contagem por {eixo_x}",
                        template="plotly_white"
                    )

            elif tipo_grafico == "Linha":
                fig_bonus = px.line(
                    df_explorador,
                    x=eixo_x,
                    y=eixo_y,
                    color=cor_param,
                    title=f"Gráfico de Linha: {eixo_y} vs {eixo_x}",
                    template="plotly_white"
                )

            elif tipo_grafico == "Dispersão (Scatter)":
                fig_bonus = px.scatter(
                    df_explorador,
                    x=eixo_x,
                    y=eixo_y,
                    color=cor_param,
                    title=f"Dispersão: {eixo_y} vs {eixo_x}",
                    template="plotly_white"
                )

            elif tipo_grafico == "Histograma":
                fig_bonus = px.histogram(
                    df_explorador,
                    x=eixo_x,
                    y=eixo_y if pd.api.types.is_numeric_dtype(df_explorador[eixo_y]) else None,
                    color=cor_param,
                    title=f"Histograma de {eixo_x}",
                    template="plotly_white"
                )

            elif tipo_grafico == "Boxplot":
                fig_bonus = px.box(
                    df_explorador,
                    x=eixo_x,
                    y=eixo_y if pd.api.types.is_numeric_dtype(df_explorador[eixo_y]) else None,
                    color=cor_param,
                    title=f"Boxplot de {eixo_y} por {eixo_x}",
                    template="plotly_white"
                )

            st.plotly_chart(fig_bonus, use_container_width=True)

        except Exception as err:
            st.error(f"Não foi possível renderizar o gráfico com as colunas selecionadas: {err}")

        with st.expander("👁️ Ver amostra dos dados em tabela"):
            st.dataframe(df_explorador.head(50), use_container_width=True)
