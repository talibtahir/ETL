print("Hello Talib")
# Data Extract 
import oracledb

conn = oracledb.connect(
    user = "hr",
    password = "hr",
    host = "192.168.101.190",
    port = 1521,
    service_name = "finiprm"
)
cur = conn.cursor()
print("connected ")
cur.execute("""
        SELECT table_name
            from all_tables
            where owner = 'HR'
            """
)

for t in cur.fetchall():
    print(t[0])
import pandas as pd 

query = "select * from GLOBAL_SUPERSTORE2"
df = pd.read_sql(query, conn)
df.head()
df.sort_values(by='ORDER_ID', ascending=False)
df.dtypes
# Data Tranformation
df.isna().sum()
df["ROW_ID"] = df["ROW_ID"].astype(int) 
df.ORDER_ID
df.ORDER_DATE
df["ORDER_DATE"] = pd.to_datetime(df["ORDER_DATE"])
df["ORDER_DATE"].isna().sum()
df["SHIP_DATE"] = pd.to_datetime(df["SHIP_DATE"])
df.SHIP_DATE.isna().sum()
df["SHIP_MODE"] = df["SHIP_MODE"].astype(str)
df.columns 
df.POSTAL_CODE = df["POSTAL_CODE"].fillna(0)
df["SALES"] = (df["SALES"]
    .str.replace("$", '')
    .str.replace(",", '')
    .astype(float)
)
df.QUANTITY = df.QUANTITY.astype(int)
df.DISCOUNT = df.DISCOUNT.astype(float)

df["PROFIT"] = (df["PROFIT"]
    .str.replace("$", '')
    .str.replace(",", '')
    .astype(float)
    )
df['SHIPPING_COST'] = df['SHIPPING_COST'].astype(float)
df = df.drop('ORDER_ID', axis=1)
df = df.drop('CUSTOMER_ID', axis=1)
df = df.drop('PRODUCT_ID', axis=1)
# Data Preparation
df["TOTAL_PRICE"] = (df['SALES'] * df['QUANTITY'])
df[['TOTAL_PRICE']] 
df['BEST_SELLING'] = (
    df.groupby('PRODUCT_NAME')['QUANTITY']
      .transform('sum')
)

df[['PRODUCT_NAME','BEST_SELLING']].sort_values(by='BEST_SELLING', ascending=True)
df['COUNTRY_RANK'] = (df.groupby('COUNTRY')['TOTAL_PRICE']
                      .rank(method="dense", ascending=False))
(df[['COUNTRY','COUNTRY_RANK']].sort_values(by='COUNTRY_RANK')).head(10)
df['YEAR'] = df['ORDER_DATE'].dt.year
df['DAY_NAME'] = df['ORDER_DATE'].dt.day_name()
df['DELIVERY_DAYS'] = (df['SHIP_DATE'] - df['ORDER_DATE']).dt.days
df.DELIVERY_DAYS
df['COUNTRY_RANK'] = df['COUNTRY_RANK'].astype(str)
df['DATE_ID'] = df.index
df['PAYMENT_ID'] = df.index
df['PRODUCT_ID'] = df.index
df['CUSTOMER_ID'] = df.index
df
# Fact and Dimension Schema 
# * Dimension Table
df.columns
# 1 Customer Dimension
Customers = (
    df[[
        'CUSTOMER_ID',
        'CUSTOMER_NAME',
        'SEGMENT',
        'POSTAL_CODE',
        'CITY',
        'STATE',
        'COUNTRY',
        'REGION',
        'MARKET',
        'COUNTRY_RANK'
    ]]
    
)
Customers
Customers.dtypes
# 2. Product Dimention
dim_product = (
    df[[
        'PRODUCT_ID',
        'PRODUCT_NAME',
        'CATEGORY',
        'SUB_CATEGORY',
        'ORDER_PRIORITY',
        'BEST_SELLING',
        'QUANTITY',
        'SHIP_MODE'
    ]]
)

dim_product
df.columns
# 3.Date Dimantion
dim_date = (
    df[[
        'DATE_ID',
        'ORDER_DATE',
        'SHIP_DATE',
        'YEAR',
        'DAY_NAME',
        'DELIVERY_DAYS',
        'SHIPPING_COST',
        
    ]]
)
dim_date
dim_date['ORDER_DATE'] = dim_date['ORDER_DATE'].dt.to_pydatetime()
dim_date['SHIP_DATE'] = dim_date['SHIP_DATE'].dt.to_pydatetime()
# 4. Payments Dimention
dim_Payments = (
    df[[
        'PAYMENT_ID',
        'SALES',
        'PROFIT',
        'DISCOUNT',
        'TOTAL_PRICE'
    ]]
)
dim_Payments.head()
## Fact Table 
df.columns
Fact_table = (
    df[[
        'ROW_ID',
        'CUSTOMER_ID',
        'PRODUCT_ID',
        'DATE_ID',
        'PAYMENT_ID'
    ]]
)
Fact_table.head()
Customers.to_csv("CUSTOMERS.csv", index=False)
dim_date.to_csv("DATES.csv", index=False)
dim_product.to_csv("PRODUCTS.csv", index=False)
dim_Payments.to_csv("PAYMENTS.csv", index=False)
## Data load 
def table_exists(cur, table_name):
    cur.execute("""
        SELECT count(*)
        FROM all_tables
        where table_name = :table_name
        """, [table_name.upper()]
    )
    return cur.fetchone()[0] == 1
# cur.execute("drop table Customers")
# conn.commit()
# print("droped")
# cur.execute("drop table Dates")
# conn.commit()
# print("droped")
# cur.execute("drop table PAYMENTS")
# conn.commit()
# print("droped")
# cur.execute("drop table products")
# conn.commit()
# cur.execute("drop table fact")
# conn.commit()
cur.execute(
    """
select table_name 
from all_tables
where owner = 'HR'
"""
)
for t in cur.fetchall():
    print(t[0])
Customers
## 1 CUSTOMERS 
if not table_exists(cur, 'CUSTOMERS'):
    cur.execute("""
        CREATE TABLE CUSTOMERS (
                CUSTOMER_ID NUMBER(10) PRIMARY KEY,
                CUSTOMER_NAME VARCHAR2(100),
                SEGMENT VARCHAR2(50),
                POSTAL_CODE NUMBER(10),
                CITY VARCHAR2(50),
                STATE VARCHAR2(50),
                COUNTRY VARCHAR2(80),
                REGION VARCHAR2(50),
                MARKET VARCHAR2(50),
                COUNTRY_RANK FLOAT(10)
            
        )
        """)
    print("Table Created ")
else :
    print("Table Already Exist")
conn.commit()
cur.execute("""
    select table_name
            from all_tables
            where owner = 'HR'
""")

for t in cur.fetchall():
    print(t[0])
Customers['CUSTOMER_ID'] = Customers['CUSTOMER_ID'].astype('int')
Customers.POSTAL_CODE = Customers.POSTAL_CODE.astype('int')
Customers.COUNTRY_RANK = Customers.COUNTRY_RANK.astype('float')
Customers_records = list(Customers.itertuples(index=False, name=None))

if not table_exists(cur, 'CUSTOMERS'):
    cur.executemany("""
    INSERT INTO CUSTOMERS(
                    CUSTOMER_ID, CUSTOMER_NAME, SEGMENT,
                    POSTAL_CODE, CITY, STATE, COUNTRY,
                    REGION, MARKET, COUNTRY_RANK
                    )
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10)
                    """, Customers_records)
    conn.commit()
    print("Customers Data Loaded")
else:
    print("Data Alredy loaded")
## 2 DATES
dim_date.dtypes
dim_date.shape
if not table_exists(cur, "DATES"):
    cur.execute("""
    CREATE TABLE DATES(
                DATE_ID NUMBER(10) PRIMARY KEY, 
                ORDER_DATE DATE, SHIP_DATE DATE,
                YEAR NUMBER(4), DAY_NAME VARCHAR2(10), 
                DELIVERY_DAYS VARCHAR2(30), 
                SHIPPING_COST FLOAT(30))"""
                )
    print("Table Created")
else:
    print("Table Already Exist")
    
date_records = list(dim_date.itertuples(index=False, name= None))

if not table_exists(cur, 'DATES'):
    cur.executemany("""
    INSERT INTO DATES( DATE_ID, ORDER_DATE, SHIP_DATE,
                    YEAR, DAY_NAME, DELIVERY_DAYS, SHIPPING_COST)
                    VALUES (:1, :2, :3, :4, :5, :6, :7)""",
                    date_records)
    conn.commit()
    print("Dates Table loaded")
else:
    print("Data Already loaded")

## 3 PAYMENTS 
dim_Payments
dim_Payments.columns
dim_Payments.dtypes
if not table_exists(cur, 'PAYMENTS'):
    cur.execute("""
    CREATE TABLE PAYMENTS(
                PAYMENT_ID NUMBER(10) PRIMARY KEY,
                SALES FLOAT(20),
                PROFIT FLOAT(20),
                DISCOUNT FLOAT(20),
                TOTAL_PRICE FLOAT(20))""")
    print("Table Created")

else:
    print("Table Already Created")
pay_records = list(dim_Payments.itertuples(index=False, name= None))

if not table_exists(cur, 'PAYMENTS'):
    cur.executemany("""
        INSERT INTO PAYMENTS(
                    PAYMENT_ID, SALES, 
                    PROFIT, DISCOUNT,
                    TOTAL_PRICE)
                    VALUES (:1, :2, :3, :4, :5)""", pay_records)
    conn.commit()
    print("Payments Table Loaded")
else:
    print("Data Already loaded")
# 4 produsts
dim_product
dim_product.columns
dim_product.dtypes
if not table_exists(cur, 'PRODUCTS'):
    cur.execute("""
    CREATE TABLE PRODUCTS(
                PRODUCT_ID NUMBER(30) PRIMARY KEY,
                PRODUCT_NAME VARCHAR2(500),
                CATEGORY VARCHAR2(50),
                SUB_CATEGORY VARCHAR2(50),
                ORDER_PRIORITY VARCHAR2(50),
                BEST_SELLING NUMBER(30),
                QUANTITY NUMBER(30),
                SHIP_MODE VARCHAR2(50))""")
    print("Table Created")
else:
    print("Table Alreadt Exixt")
product_records = list(dim_product.itertuples(index=False, name= None))

if not table_exists(cur, 'PRODUCTS'):
    cur.executemany("""
        INSERT INTO PRODUCTS(
                    PRODUCT_ID,
                    PRODUCT_NAME,
                    CATEGORY,
                    SUB_CATEGORY,
                    ORDER_PRIORITY,
                    BEST_SELLING,
                    QUANTITY,
                    SHIP_MODE
                    )
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8)""", product_records)
    conn.commit()
    print("Product Data Loaded")
else:
    print("Data Already loaded")
# 5 Fact load
Fact_table.columns
Fact_table.dtypes
if not table_exists(cur, 'FACT'):
    cur.execute("""
    CREATE TABLE FACT(
                ROW_ID NUMBER(10) PRIMARY KEY,
                CUSTOMER_ID NUMBER(10),
                PRODUCT_ID NUMBER(10),
                DATE_ID NUMBER(10),
                PAYMENT_ID NUMBER(10))""")
    print("Table Created")
else:
    print("Table Already Created")
fact_records = list(Fact_table.itertuples(index=False, name=None))

if not table_exists(cur, 'FACT'):
    cur.executemany("""
        INSERT INTO FACT(
                    ROW_ID, CUSTOMER_ID, PRODUCT_ID, DATE_ID, PAYMENT_ID
                    )
                    VALUES (:1, :2, :3, :4, :5)""", fact_records)
    conn.commit()
    print("Fact Data Loaded")
else:
    print("Data Already loaded")