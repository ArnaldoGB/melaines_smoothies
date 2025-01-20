import requests
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Título do app
st.title("Customize Your Smoothie!:cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Entrada para o nome do pedido
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

# Obter a sessão ativa do Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Obter as opções de frutas disponíveis
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
st.dataframe(data=my_dataframe, use_container_width=True)

# Adicionar dados da API SmoothieFroot
st.subheader(ingredients_list + 'Nutritio Information')
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + ingredients_list)
sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# Seleção de ingredientes
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe['FRUIT_NAME'],  # Use apenas a coluna 'FRUIT_NAME' para o multiselect
    max_selections=5
)

# Verificar se há ingredientes selecionados
if ingredients_list:
    st.write("Selected Ingredients: ", ingredients_list)

    # Concatenar os ingredientes em uma string separada por vírgulas
    ingredients_string = ", ".join(ingredients_list)
    st.write("Ingredients String: ", ingredients_string)
    
    # Comando SQL para inserir na tabela
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{name_on_order}')
    """
    st.write("SQL Statement: ", my_insert_stmt)

    # Botão para submeter o pedido
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        try:
            # Executar o comando SQL no Snowflake
            session.sql(my_insert_stmt).collect()
            st.success("Your Smoothie is ordered!", icon="✅")
        except Exception as e:
            st.error(f"An error occurred: {e}")


