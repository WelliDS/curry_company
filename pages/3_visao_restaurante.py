# Libraries
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import re
import PIL
import folium
import streamlit as st
import plotly.graph_objects as go

from PIL import Image
from haversine import haversine
from streamlit_folium import folium_static

st.set_page_config ( page_title = "Visão Restaurantes", page_icon = "🍽", layout = 'wide' )

# ---------------------------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------------------------

def avg_std_time_on_traffic (df1):
                
    time_avg_delivery_city_traffic = ( df1.loc[:, ['ID', 'City', 'Time_taken(min)', 'Road_traffic_density',]]
                                          .groupby (['City', 'Road_traffic_density'])
                                          .agg({ 'Time_taken(min)' : ['mean','std']}) )

    #mudança nome das colunas 
    time_avg_delivery_city_traffic.columns = ['time_mean', 'time_std']

    #reset do index
    df_aux = time_avg_delivery_city_traffic.reset_index()

    fig = px.sunburst (df_aux, path=['City', 'Road_traffic_density'], values='time_mean',
           color='time_std', color_continuous_scale='RdBu',
           color_continuous_midpoint=np.average(df_aux['time_std'] ) )
    
    return fig

def time_avg_delivery_city_order (df1):
        
    #tabela (dataframe) com o tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.        
    time_avg_delivery_city_order = ( df1.loc[:, ['ID', 'City', 'Time_taken(min)', 'Type_of_order',]]
                                    .groupby (['City', 'Type_of_order'])
                                      .agg({ 'Time_taken(min)' : ['mean','std']}) )

    #mudança nome das colunas 
    time_avg_delivery_city_order.columns = ['time_mean', 'time_std']

    #reset do index
    df_aux = time_avg_delivery_city_order.reset_index()

    return df_aux

def avg_std_time_graph (df1):
                
    #Realizando a inclusão do gráfico de barras com o tempo médio de entrega por cidade e o desvio padrão
    df_aux = ( df1.loc[:, ['City', 'Time_taken(min)']].groupby (['City'])
                          .agg({ 'Time_taken(min)' : ['mean','std']}) )

    #mudança nome das colunas 
    df_aux.columns = ['time_mean', 'time_std']

    #reset do index
    df_aux = df_aux.reset_index()


    #Desenhando o gráfico

    fig = go.Figure()
    fig.add_trace ( go.Bar(name='Control', x=df_aux['City'], y=df_aux['time_mean'], error_y=dict(type='data', array=df_aux['time_std'])))     
    fig.update_layout (barmode='group')

    return fig


def avg_std_time_delivery (df1, festival, op):
            
    """
        Esta função calculo o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros:
            Input:
                - DF: Dataframe com os dados necessários para o cálculo
                - op: tipo de operação que será calculado:
                    'time_mean': Cálcula o tempo médio
                    'time_std': Cálcula o desvio padrão do tempo
                - festival: Se a entrega ocorreu no Festival:
                    'Yes' = Ocorreu entrega durante festival
                    'No' = Ocorreu entrega fora do festival
                
            Ouput:
                - DF: Dataframe com o resultado (2 colunas e 1 linha)

    """
    df_aux = ( df1.loc[:, ['ID','Time_taken(min)', 'Festival',]]
                .groupby (['Festival'])
                .agg({ 'Time_taken(min)' : ['mean','std']}) )

    #mudança nome das colunas 
    df_aux.columns = ['time_mean', 'time_std']

    #reset do index
    df_aux = df_aux.reset_index()

    #Selecionando apenas o tempo médio de entrega com festival
    df_aux = np.round (df_aux.loc[df_aux ['Festival'] == festival, op], 2)

    return df_aux


def distance (df1, fig):
    if fig == False:
        df1 ['distance'] = ( df1.loc [:, ["Restaurant_latitude", 'Restaurant_longitude', 
                                         "Delivery_location_latitude", 'Delivery_location_longitude']]
                                            .apply(lambda x: haversine (
                                            (x ['Restaurant_latitude'], x['Restaurant_longitude']), 
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1) )
        distance_rest_delivery_mean = np.round ( df1['distance'].mean(), 2)

        return distance_rest_delivery_mean

    else:
        df1 ['distance'] = ( df1.loc [:, ["Restaurant_latitude", 'Restaurant_longitude', 
                                  "Delivery_location_latitude", 'Delivery_location_longitude']]
                                .apply(lambda x: haversine (
                                (x ['Restaurant_latitude'], x['Restaurant_longitude']), 
                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1) )


        avg_distance = df1.loc[:, ['City', 'distance']].groupby (['City']).mean().reset_index()

        #Gráfico avg_distance
        # Criando um gráfico de pizza retirando uma fração
        fig = go.Figure ( data=[ go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.2,0])])
        return fig
        
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


st.header ('Marketplace - Visão Restaurantes')

#image_path = ( 'logowell.jpeg')
image = Image.open ( 'logowell.jpeg' )
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
        st.title (" :blue[Overall Metrics] :chart_with_upwards_trend:")
        
        col1, col2, col3, col4, col5, col6 = st.columns (6)
        with col1:
            delivers = df1.loc [:, 'Delivery_person_ID'].nunique()
            #st.markdown ('###### Delivers:')
            col1.metric ('Delivers:', delivers)
        
        with col2:
            distance_rest_delivery_mean = distance ( df1, fig=False )
            col2.metric ('Mean Distance', distance_rest_delivery_mean)
            
        with col3:
            df_aux = avg_std_time_delivery (df1, 'Yes', 'time_mean')
            col3.metric ( 'Delivery with Festival', df_aux )
                    
        with col4:
            df_aux = avg_std_time_delivery (df1, 'Yes', 'time_std')
            col4.metric ('Std with Festival', df_aux )
                       
        with col5:
            df_aux = avg_std_time_delivery (df1, 'No', 'time_mean')
            col5.metric ( 'Delivery without Festival', df_aux )
                        
        with col6:
            df_aux = avg_std_time_delivery (df1, 'No', 'time_std')
            col6.metric ('Std without Festival', df_aux)
            
     
    with st.container():
        
        col1, col2 = st.columns (2)
        
        
        with col1:
            col1.write ('##### _Média e Desvio Padrão entrega por Cidade_')
            fig = avg_std_time_graph (df1)
            st.plotly_chart (fig, use_container_width=True)
            

        
        with col2:
            col2.write ('##### _Média e Desvio Padrão entrega por Cidade e Refeição_')
            df_aux = time_avg_delivery_city_order (df1)
            st.dataframe(df_aux, use_container_width=True)
            
        
    st.markdown ( """---""" )
        
    with st.container():
        st.title (':blue[Distribuição do tempo] :stopwatch:')
        
        col1, col2 = st.columns (2, gap = 'large')
        
        with col1:
            col1.write ('#### _Tempo Médio entrega por Cidade_')
            fig = distance (df1, fig=True)
            st.plotly_chart (fig, use_container_width=True)
            
                        
        with col2:
            col2.write ('#### _Tempo Médio entrega por Cidade, tipo de tráfego e Desvio Padrão_')
            fig = avg_std_time_on_traffic (df1)
            st.plotly_chart (fig, use_container_width=True)
                      
        
        st.markdown ( """---""" )
        

        
   
    