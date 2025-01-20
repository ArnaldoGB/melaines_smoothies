import requests
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import pandas as pd

# Título do app
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Entrada para o nome do pedido
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

# Obter a sessão ativa do Snowflake
try:
    cnx = st.connection("snowflake")
    session = cnx.session()
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")
    st.stop()

# Obter as opções de frutas disponíveis
try:
    fruit_options_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME")).to_pandas()
    st.dataframe(data=fruit_options_df, use_container_width=True)
except Exception as e:
    st.error(f"Failed to retrieve fruit options: {e}")
    st.stop()

# Seleção de ingredientes
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options_df['FRUIT_NAME'],  # Use apenas a coluna 'FRUIT_NAME' para o multiselect
    max_selections=5
)

# Verificar se há ingredientes selecionados
if ingredients_list:
    st.write("Selected Ingredients: ", ingredients_list)

    # Concatenar os ingredientes em uma string separada por vírgulas
    ingredients_string = ", ".join(ingredients_list)
    st.write("Ingredients String: ", ingredients_string)

    # Chamada de API para obter informações adicionais sobre um ingrediente
    try:
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        if smoothiefroot_response.status_code == 200:
            smoothiefroot_data = pd.DataFrame([smoothiefroot_response.json()])
            st.dataframe(data=smoothiefroot_data, use_container_width=True)
        else:
            st.warning("Failed to fetch additional fruit data. Check the API.")
    except Exception as e:
        st.error(f"An error occurred while calling the API: {e}")

    # Comando SQL para inserir na tabela
    my_insert_stmt = """
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES (%s, %s)
    """
    st.write("SQL Statement: ", my_insert_stmt)

    # Botão para submeter o pedido
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        try:
            # Executar o comando SQL no Snowflake de forma segura
            session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
            st.success("Your Smoothie is ordered!", icon="✅")
        except Exception as e:
            st.error(f"An error occurred while submitting your order: {e}")
