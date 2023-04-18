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
from streamlit_folium import folium_static

st.set_page_config ( page_title = "Visão Empresa", page_icon = "📈", layout = 'wide' )

# ---------------------------------------------------------------------------------------------
# Funções
# ---------------------------------------------------------------------------------------------
def country_maps ( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um mapa na página, 
        MarketPlace-Visão Cliente > Visão Geográgica
        Input: Dataframe
        Output: Mapa (map)
    """
    #Order Metric
    # A localização central de cada cidade por tráfego e gerar um mapa
    df_aux = ( df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 
                'Delivery_location_longitude']]
                  .groupby (['City', 'Road_traffic_density'])
                  .median()
                  .reset_index() )

    #desenahndo o mapa    
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker ([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[["City", "Road_traffic_density"]]).add_to (map)

    folium_static (map, width=1024, height=600)
            
    return None


def order_share_by_week ( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um gráfico de linha na página, 
        MarketPlace-Visão Cliente > Visão Tática > Gráfico Qtde de pedido por entregador por semana
        Input: Dataframe
        Output: Gráfico Linhas (line)
    """
    
    #Qtde de pedidos por entregador por semana e gerar um gráfico de linha
    df_aux1 = df1.loc[:, ['ID', "week_of_year"]].groupby (['week_of_year']).count().reset_index()
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID', "week_of_year"]]
                   .groupby (['week_of_year'])
                   .nunique()
                   .reset_index() )

    df_aux = pd.merge(df_aux1, df_aux2, how= 'inner')
    df_aux ['order_by_deliver'] = df_aux ["ID"] / df_aux ["Delivery_person_ID"]
    fig5 = px.line (df_aux, x='week_of_year', y='order_by_deliver')
            
    return fig5


def order_by_week ( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um gráfico de linha na página, 
        MarketPlace-Visão Cliente > Visão Tática > Gráfico Qtde de pedidos por semana
        Input: Dataframe
        Output: Grafico Linhas (line)
    """
    
    #Quantidade de pedidos por semana e gráficos de linha
    df1 ["week_of_year"] = df1["Order_Date"].dt.strftime ("%U")  # "%U" a semana inicia no Domingo e "%W" a semana inicia na Segunda

    df_aux = df1.loc[:, ["ID", "week_of_year"]].groupby (["week_of_year"]).count().reset_index()

    #desenhando o gráfico de linha
    fig4 = px.line (df_aux, x='week_of_year', y='ID')
            
    return fig4



def traffic_order_city( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um gráfico de bolhas na página, 
        MarketPlace-Visão Cliente > Visão Gerencial > Gráfico Qtde de pedido por cidade e tipo de tráfego
        Input: Dataframe
        Output: Gráfico Scatter (bolha)
    """
    
    #Comparação do volume de pedidos por cidades e tipo de tráfego, com um gráfico de bolha
    df_aux = ( df1.loc[:, ["ID", "City", "Road_traffic_density"]]
                  .groupby (['City', 'Road_traffic_density'])
                  .count()
                  .reset_index() )

    #desenhando o gráfico de bolha
    fig3 = px.scatter (df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
                
    return fig3


def traffic_order_share( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um gráfico de pizza na página, 
        MarketPlace-Visão Cliente > Visão Gerencial > Gráfico Qtde de pedidos por tipo de tráfego
        Input: Dataframe
        Output: Gráfico Pizza (pie)
    """
    #Order Metric
    #Distribuição dos pedidos por tipo de tráfego e realizado um gráfico de pizza
    df_aux = ( df1.loc[:, ["ID", "Road_traffic_density"]]
                .groupby (["Road_traffic_density"])
                .count()
                .reset_index() )
    
    fig2 = px.pie (df_aux, values="ID", names= "Road_traffic_density")
                
    return fig2

                
def order_metric ( df1 ):
    """ Esta função tem a responsabilidade de realizar a inclusão de um gráfico de barras na página, 
        MarketPlace-Visão Cliente > Visão Gerencial > Gráfico Qtde de pedidos por dia
        Input: Dataframe
        Output: Gráfico barras (bar)
    """
    #Seleção de LInhas
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby (['Order_Date']).count().reset_index()

    #desenahndo o gráfico de barras
    fig1 =  px.bar (df_aux, x='Order_Date', y='ID')
            
    return fig1
        





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


st.header ('Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container ():
        # Order Metric
        fig1 = order_metric ( df1 )
        st.write ("### _Orders by Day_ :bar_chart:")
        st.plotly_chart (fig1, use_container_width=True)
        
        
    with st.container ():
        col1, col2 = st.columns ( 2 )
        with col1:
            fig2 = traffic_order_share( df1 )
            col1.write ("### _Order by Traffic_")
            #desenhando o gráfico de pizza
            st.plotly_chart (fig2, use_container_width=True)
              
        
        with col2:
            col2.write ("### _Order by City and Traffic_")
            fig3 = traffic_order_city ( df1 )
            st.plotly_chart (fig3, use_container_width=True)        

                     
with tab2:
    with st.container ():
        st.write ("### _Orders by Week_ :chart_with_downwards_trend:")
        fig4 = order_by_week ( df1 )
        st.plotly_chart (fig4, use_container_width=True)
        
        
    with st.container ():
        st.write ("### _Orders Deliver by Week_ :chart_with_downwards_trend:")
        fig5 = order_share_by_week (df1)
        #desenhando o gráfico de bolha
        st.plotly_chart (fig5, use_container_width=True)
            

with tab3:
    with st.container ():
        st.write ("### _Central Localization by City and Traffic_ :world_map:")
        country_maps ( df1 )
        
        
        