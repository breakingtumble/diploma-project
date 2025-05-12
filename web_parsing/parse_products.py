from .configuration_loader import ConfigurationLoader
from .marketplace_parser import MarketplaceParser
from .product import Product
from sqlalchemy import create_engine
from datetime import datetime
import datetime
import psycopg2
import pandas as pd
import csv
import re
import time
import schedule
import os
from .utils import get_db_url

class ParsingObject:
    def __init__(self, guid, marketplace_key, url, etl_date):
        self.guid = guid
        self.marketplace_key = marketplace_key
        self.url = url
        self.etl_date = etl_date

def get_db_connection():
    return psycopg2.connect(
        dbname   = os.getenv("DB_NAME",     "parse_db"),
        user     = os.getenv("DB_USER",     "parser"),
        password = os.getenv("DB_PASSWORD", "123456"),
        host     = os.getenv("DB_HOST",     "localhost"),
        port     = os.getenv("DB_PORT",     "5432")
    )

def get_sqlalchemy_engine():
    db_user = os.getenv("DB_USER", "parser")
    db_pass = os.getenv("DB_PASSWORD", "123456")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "parse_db")

    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url)

def insert_data_to_db(df, table_name='parsed_products'):
    engine = get_sqlalchemy_engine()
    df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')

def load_data_from_csv(path='data/data.csv'):
    parsing_objects_list = list()
    with open(path) as f:
        file = csv.DictReader(f, fieldnames=['guid', 'marketplace_key', 'url'])
        for row in file:
            parsing_objects_list.append(ParsingObject(row['guid'], row['marketplace_key'], row['url']))
    return parsing_objects_list

def parse_and_transform_data(parsing_objects):
    config = ConfigurationLoader(
        get_db_url()
    ).get_configuration_object()
    parser = MarketplaceParser(config)
    products = []
    for object in parsing_objects:
        print(f"[DEBUG] Parsing product: id={object.guid}, url={object.url}")
        try:
            product = parser.parse_product_by_url(object.url)
            product.set_id(object.guid)
            product.set_etl_date(object.etl_date)
            print(f"[DEBUG] Parsed price (raw): {product._price}")
        except Exception as e:
            print(f"[DEBUG] Exception for url {object.url}: {e}")
            continue
        product_object = {
            'product_id': product._id,
            'price': product._price,
            'etl_date': product._etl_date
        }
        products.append(product_object)
    df = pd.DataFrame(products)
    if df.empty:
        print("[DEBUG] No products parsed into DataFrame.")
        return None
    def debug_extract_price(raw):
        price = extract_price(raw)
        print(f"[DEBUG] Extracting price: raw='{raw}' -> price={price}")
        return price
    df['price_proceeded'] = df['price'].apply(debug_extract_price)
    df = df.drop(columns=['price'])
    desired_order = ['product_id', 'price_proceeded', 'etl_date']
    df = df[desired_order]
    return df


def extract_price(raw):
    if pd.isna(raw):
        return None
    
    text = str(raw).replace('\u00A0', '').strip()

    number_text = re.sub(r'[^\d.,]', '', text)

    if number_text.count(',') > 1:
        number_text = number_text.replace(',', '')
    elif number_text.count(',') == 1 and number_text.count('.') == 0:
        number_text = number_text.replace(',', '.')
    else:
        number_text = re.sub(r'(?<=\d)[\s,](?=\d{3}\b)', '', number_text)
    
    try:
        price = float(number_text)
    except ValueError:
        price = None

    return price

def main():
    conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, marketplace_key, url FROM products")
    now = datetime.datetime.now()
    etl_date = now.strftime("%Y-%m-%d %H:%M:%S")
    while True:
        rows = cursor.fetchmany(1000)
        objects_to_parse = []
        if not rows:
            break
        for guid, key, url in rows:
            obj = ParsingObject(guid, key, url, etl_date)
            objects_to_parse.append(obj)
        df = parse_and_transform_data(objects_to_parse)
        if df is None:
            print("Parsing job wasn't finished as data was not parsed")
        insert_data_to_db(df)
        print("Parsing job is finished")

def job():
    try:
        main()
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error: {e}")

schedule.every().day.at("03:00").do(job)

if __name__ == "__main__":
    job()
    while True:
        schedule.run_pending()
        time.sleep(50)