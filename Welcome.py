import streamlit as st
st.set_page_config(layout='wide')
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

from PIL import Image


image = Image.open(f'./logo.png')
st.image(image, use_column_width=True)

st.write('---')
st.markdown('''
    Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, 
    when an unknown printer took a galley of type and scrambled it to make a type specimen book. 
    It has survived not only five centuries, but also the leap into electronic typesetting, 
    remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset 
    sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like 
    Aldus PageMaker including versions of Lorem Ipsum.
''')

