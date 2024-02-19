import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    page_title="População USA Dashboard",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded")

#alt.themes.enable("dark")

# LOADING DATA
df_reshaped = pd.read_csv("us-population-2010-2019-reshaped.csv")

# ADDING A SIDEBAR FOR FILTERINGS
with st.sidebar:
    st.title("População americana em Dashboard")
    anos_lista = list(df_reshaped.year.unique()) [::-1]  #Criando a lista de anos que aparecerão no selectbox

    ano_selecionado = st.selectbox('Selecione o ano',anos_lista, index=len(anos_lista)-1) # Ao selecionar um ano da lista, gravá-lo na variável
    df_ano_selecionado = df_reshaped[df_reshaped.year == ano_selecionado]  # Fazendo o df inteiro baseado no filtro realizado (ano)
    df_ano_selecionado_sorted = df_ano_selecionado.sort_values(by="population", ascending=False) # Descendente por ano

    #Lista de cores de temas. Há inúmeras! Aqui só algumas.
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    cor_tema_selecionado = st.selectbox('Selecione a cor do tema', color_theme_list)   # Tema escolhido

# DEFININDO FUNÇÕES PARA OS DIVERSOS MAPAS DO DASHBOARD. UMA FUNÇÃO PARA CADA MAPA
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Ano", titleFontSize=15, titlePadding=8, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=15, titlePadding=8, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap

col = st.columns((1.5, 4.5, 3), gap='medium')

# Mapa no choropleth també na coluna 1
def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth(input_df, locations=input_id, color=input_column, locationmode="USA-states",
                               color_continuous_scale=input_color_theme,
                               range_color=(0, max(df_ano_selecionado.population)),
                               scope="usa",
                               labels={'population':'Population'}
                              )
    choropleth.update_layout(
        template='plotly_white',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=350
    )
    return choropleth


with col[1]:
    st.markdown("#### População Total")
    choropleth = make_choropleth(df_ano_selecionado, 'states_code', 'population', cor_tema_selecionado)
    st.plotly_chart(choropleth, use_container_width=True)

    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', cor_tema_selecionado)
    st.altair_chart(heatmap, use_container_width=True)


with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_ano_selecionado_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                    "states": st.column_config.TextColumn(
                        "States",
                    ),
                    "population": st.column_config.ProgressColumn(
                        "Population",
                        format="%f",
                        min_value=0,
                        max_value=max(df_ano_selecionado_sorted.population),
                     )}
                 )
    with st.expander('About', expanded=True):
        st.write('''
            - Data: [U.S. Census Bureau](<https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html>).
            - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
            - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
            ''')
