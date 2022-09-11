import streamlit as st
import sqlite3
import pandas as pd
import json
from PIL import Image
from datetime import datetime
from glob import glob
st.set_page_config(layout='wide')
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

class DatabaseManagement:
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
        self._create_usertable()

    def _create_usertable(self):
        sql = """
            CREATE TABLE IF NOT EXISTS 
            userstable(
                category TEXT,
                brand TEXT,
                product TEXT,
                full_name TEXT, 
                phone_number TEXT, 
                email TEXT, 
                proposed_bid INT, 
                action_date TIMESTAMP
                )
        """
        self.cursor.execute(sql)

    def add_record(self, category, brand, product, proposed_bid, full_name, phone_number, email, action_date):
        sql = f"""
            INSERT INTO userstable(
                category,
                brand,
                product,
                full_name,  
                phone_number, 
                email, 
                proposed_bid, 
                action_date
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_tuple = (category, brand, product, full_name, phone_number, email, proposed_bid, action_date)
        self.cursor.execute(sql, data_tuple)
        self.conn.commit()

    def convert_into_csv(self):
        sql = """
            SELECT * FROM userstable
        """
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        data = pd.read_sql(sql, self.conn)
        data.to_excel('data.xlsx')

    # def view_table(self):
    #     sql = """
    #         SELECT * FROM userstable
    #     """
    #     self.cursor.execute(sql)
    #     data = self.cursor.fetchall()
    #     data = pd.read_sql(sql, self.conn)
    #     return data

# Initialize state
if 'bidded' not in st.session_state:
    st.session_state.bidded = False
if 'confirmed' not in st.session_state:
    st.session_state.confirmed = False

def resetSession():
    st.session_state.bidded = False
    st.session_state.confirmed = False

def callback():
    # "Make a bid" was clicked
    st.session_state.bidded = True

def confirmation():
    # "Confirm" was clicked
    st.session_state.confirmed = True

def StatusCheck():
    # mentioned fields must be filled in
    items = ['proposed_bid', 'full_name', 'phone_number', 'email']
    
    # check if any of the fields is empty
    filled_ok = all([len(st.session_state[key]) for key in items])

    # check if proposed_bid in numeric format
    proposed_bid_check = st.session_state.proposed_bid.isnumeric()

    proposed_bid_min_amount_check = int(st.session_state.proposed_bid) >= int(product['price'])
    
    if (filled_ok==False and st.session_state.confirmed==True):
        st.error('Please fill in all required fields.')
        return False

    elif (filled_ok==True 
                and st.session_state.confirmed==True 
                and proposed_bid_check==False):
        st.error('Incorrect bid amount format')

    elif (filled_ok==True 
                and st.session_state.confirmed==True 
                and proposed_bid_check==True
                and proposed_bid_min_amount_check==False):
        st.error('Bid Amount must be equal to start price or greater.')

    elif (filled_ok==True 
                and st.session_state.confirmed==True 
                and proposed_bid_check==True
                and proposed_bid_min_amount_check==True):
        st.success('Confirmed')
        return True
        

with st.sidebar:
    db = DatabaseManagement()

    catalogue_data = pd.read_excel('./data/catalogue_data.xlsx')

    with st.expander('Product Selection'):
        category = st.selectbox('Category', catalogue_data.category.unique(), on_change=resetSession)
        brand = st.selectbox('Brand', catalogue_data[catalogue_data.category==category].brand.unique(), on_change=resetSession)
        product_code = st.selectbox('Product', catalogue_data[(catalogue_data.category==category) & (catalogue_data.brand==brand)].product_code.unique(), on_change=resetSession)

    product = catalogue_data[(catalogue_data.category==category) 
                             & (catalogue_data.brand==brand)
                             & (catalogue_data.product_code==product_code)]
    

    if (st.button('Make a bid', on_click=callback) or st.session_state.bidded):
        proposed_bid = st.text_input('Place Your bid amount (AZN)', value='0', key='proposed_bid')
        full_name = st.text_input('Full Name', key='full_name')
        phone_number = st.text_input('Phone Number', key='phone_number')
        email = st.text_input('Email Address', key='email')
        st.button(label='Confirm', on_click=confirmation)
    
        check_result = StatusCheck()

        if check_result==True:
            db.add_record(category, brand, product_code, int(proposed_bid), full_name, phone_number, email, datetime.now())

db.convert_into_csv()        

st.header(product.product_name.values[0])

col1, col2, col3, col4 = st.columns(4)
col1.markdown("### Size")
col1.markdown(f"##### {product['size'].values[0]}")

col2.markdown("### Color")
col2.markdown(f"##### {product.color.values[0]}")

col3.markdown("### Material")
col3.markdown(f"##### {product.material.values[0]}")

col4.markdown(f'<h1 style="color:#EF4136;font-size:30px;text-align: center; padding: 7px">Start price</h1>', unsafe_allow_html=True)
col4.write(f'<h1 style="color:#EF4136;font-size:24px;text-align: center;padding: 5px">{product.price.values[0]} ₼</h1>', unsafe_allow_html=True)

# Working with pictures
files = glob(f'./photos/{product_code}*')
columns = ', '.join([f'col{i}' for i in range(1, len(files)+1)])

if len(files)>1:
    exec(f'{columns} = st.columns({len(files)})')
    for i, file in enumerate(files, start=1):
        image = Image.open(file)
        exec(f'col{i}.image(image, use_column_width=True)')
else:
    image = Image.open(files[0])
    st.image(image, use_column_width=True)