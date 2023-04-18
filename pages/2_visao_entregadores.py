# Libraries
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import re
import PIL
import folium
import streamlit as st

from PIL import Image
from haversine import haversine

st.set_page_config ( page_title = "Visão Entregadores", page_icon = "🛵", layout = 'wide' )


# ---------------------------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------------------------

def top_delivers ( df1, top_asc ):
    df2 = ( df1.loc[:, ["Delivery_person_ID", "City", "Time_taken(min)"]]
               .groupby ([ 'City', 'Delivery_person_ID']).mean()
               .sort_values ( [ 'City', 'Time_taken(min)'], ascending = top_asc ).reset_index() )
            
            
 
    df_aux01 = df2.loc[df2[ 'City'] == "Metropolitian",:].head(10)
    df_aux02 = df2.loc[df2[ 'City'] == "Urban",:].head(10)
    df_aux03 = df2.loc[df2[ 'City'] == "Semi-Urban",:].head(10)

    df3 = pd.concat ( [df_aux01, df_aux02,df_aux03 ]).reset_index (drop = True)

    return df3


def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe 
        
        Tipos de Limpeza:
        1.Remover spaco da string (sem o for)
        2.Mudança do tipo da coluna de dados;
        3.Remoção dos espaços das variáveis de texto;
        4.Alteração/formatação da coluna de data;
        5.Limpeza da coluna de tempo (Time_taken(min)) - Remoção do texto da variável numérica
        
        Input: Dataframe
        Output: Dataframe
    """
    #Realizando a Limpeza do Dataset

    #Remover spaco da string (sem o for)
    df1.loc[:, ["ID"]] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, ["Delivery_person_ID"]] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:, ["Road_traffic_density"]] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, ["Type_of_order"]] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, ["Type_of_vehicle"]] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, ["Festival"]] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:, ["City"]] = df1.loc[:,'City'].str.strip()

    #Alterando a feature Delivery_person_Ratings de object para float
    df1 ["Delivery_person_Ratings"] = df1 ["Delivery_person_Ratings"].astype (float)

    #Retirando os 'NaN ' das features: "multiple_deliveries " e "Delivery_person_Age"
    #Após a retirada alterando de object para int

    limp_linha = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc [limp_linha, :]

    df1 ["Delivery_person_Age"] = df1 ["Delivery_person_Age"].astype (int)


    limp_linha = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc [limp_linha, :]
    df1 ["multiple_deliveries"] = df1 ["multiple_deliveries"].astype (int)


    limp_linha = df1['City'] != 'NaN'
    df1 = df1.loc [limp_linha, :]

    limp_linha = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc [limp_linha, :]


    limp_linha = df1['Festival'] != 'NaN'
    df1 = df1.loc [limp_linha, :]

    #alteração para date da coluna Order_Date
    df1 ['Order_Date'] = pd.to_datetime (df1['Order_Date'], format = "%d-%m-%Y")


    #limpando a coluna de Time_taken(min)

    df1['Time_taken(min)'] = df1 [ "Time_taken(min)"].apply( lambda x: x.split('(min) ')[1])

    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype (int)

    return df1

#-------------------------------------   Inicio da Estrutura Lógica do Código -------------------------------------------------------------
#-------------------------------------
# Import Dataset
#-------------------------------------

df = pd.read_csv ('train.csv')

# ----------------------------------
# Limpando os dados
# ----------------------------------

df1 = clean_code ( df )



# ==============================================================
# Sidebar (barra lateral) no Streamlit
# ==============================================================


st.header ('Marketplace - Visão Entregadores')

#image_path = ( 'logowell.jpeg')
image = Image.open ( 'logowell.jpeg')
st.sidebar.image ( image, width=200)


st.sidebar.markdown ( '# Cury Company' )
st.sidebar.markdown ( '### Fastest Delivery in Town' )
st.sidebar.markdown ( """---""" )

st.sidebar.markdown ('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime (2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11), 
    max_value=pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY' )

st.sidebar.markdown ( """---""" )

st.sidebar.markdown ('## Selecione a condição de Trânsito:')
traffic_options = st.sidebar.multiselect (
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default= ['Low', 'Medium', 'High', 'Jam'] )


st.sidebar.markdown ( """---""" )

st.sidebar.markdown ('## Selecione a condição climática:')
weather_options = st.sidebar.multiselect (
    'Quais as condições do clima',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default= ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'] )

st.sidebar.markdown ( """---""" )
st.sidebar.markdown ( '###### Powered by Wellington Silva' )

#Filtro de Data
linhas_selecionadas = df1 ['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#Filtro de Tipo de Tráfico
linhas_selecionadas = df1 ['Road_traffic_density'].isin (traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#Filtro de Tipo de Clima
linhas_selecionadas = df1 ['Weatherconditions'].isin (weather_options)
df1 = df1.loc[linhas_selecionadas, :]


# ==============================================================
# Layout no Streamlit
# ==============================================================

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '_',  ' _ '])

with tab1:
    with st.container():
        st.title (':blue[Overall Metrics] :chart_with_upwards_trend:')
        col1, col2, col3, col4 = st.columns (4, gap='large')
        
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:,"Delivery_person_Age"].max()
            col1.metric ('A maior idade é: ', maior_idade)
        
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:,"Delivery_person_Age"].min()
            col2.metric ('A menor idade é: ', menor_idade)
            
        with col3:
            # A melhor condição de veículo
            melhor_condicao = df1.loc[:,"Vehicle_condition"].max()
            col3.metric ('A melhor condição é:', melhor_condicao)
            
        with col4:
            # A pior condição de veículo
            pior_condicao = df1.loc[:,"Vehicle_condition"].min()
            col4.metric ('A pior condição é:', pior_condicao)
            
    with st.container():
        st.markdown ( """---""" )
        st.title (' :blue[Avaliações] :clipboard:')
        
        col1, col2 = st.columns (2)
        
        with col1:
            # Avaliação média por entregador
            col1.write ('##### _Avaliação Média por entregador_')
            avg_by_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                 .groupby (['Delivery_person_ID'])
                                 .mean()
                                 .reset_index() )
            col1.dataframe (avg_by_deliver, use_container_width=True)
            
        with col2:
            # Avaliação média e desvio padrão por tipo de trânsito
            col2.write ('##### _Avaliação Média por Trânsito_')
            
            #comando agrupado
            df_avg_std_rating_by_traffic = ( df1.loc[:, ["Delivery_person_Ratings", "Road_traffic_density"]]
                                                .groupby (['Road_traffic_density'])
                                                .agg({'Delivery_person_Ratings' : ['mean', 'std'] } ) )

            #mudança nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            #reset do index
            df_avg_std_rating_by_traffic.reset_index()
            
            col2.dataframe (df_avg_std_rating_by_traffic)
            
            # Avaliação média e desvio padrão por condição climática
            col2.write ('##### _Avaliação Média por condição climática_')
            
            #comando agrupado
            df_avg_std_rating_by_weather = ( df1.loc[:, ["Delivery_person_Ratings", "Weatherconditions"]]
                                                .groupby (['Weatherconditions'])
                                                .agg({'Delivery_person_Ratings' : ['mean', 'std'] } ) )

            #mudança nome das colunas
            df_avg_std_rating_by_weather.columns = ['weather_mean', 'weather_std']

            #reset do index
            df_avg_std_rating_by_weather.reset_index()
            
            col2.dataframe (df_avg_std_rating_by_weather)
            
            
            
    with st.container():
        st.markdown ( """---""" )
        st.title (':blue[Velocidade de entrega] :rocket:')
        
        col1, col2 = st.columns (2)
        
        with col1:
            # Os entregadores mais rápidos por cidade
            col1.write ('###### _Top entregadores mais rápidos_')
            df3 = top_delivers ( df1, top_asc = True )
            col1.dataframe (df3, use_container_width=True)
            
            
        with col2:
            # Os entregadores mais rápidos por cidade
            col2.write ('##### _Top entregadores mais lentos_')
            df3 = top_delivers ( df1, top_asc = False )
            col2.dataframe (df3)
            
            
        
                