import logging
import time
from datetime import datetime
from .product import Product
import requests
from bs4 import BeautifulSoup
import validators
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .configuration_loader import ConfigurationLoader
from .marketplace_configuration import MarketplaceConfiguration
from .utils import get_db_url
import re
import sys

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MarketplaceParser:
    def __init__(self, config_object):
        self.configuration_object = config_object
        print(f"[DEBUG] Initialized parser with config: {config_object}")  # Using print for immediate visibility
        logger.debug(f"Initialized parser with config: {config_object}")
    
    def parse_product_by_url(self, url):
        print(f"[DEBUG] Starting to parse URL: {url}")  # Using print for immediate visibility
        logger.debug(f"Starting to parse URL: {url}")
        marketplace_configuration, key = self.__find_configuration_by_url(url)
        print(f"[DEBUG] Found configuration for key: {key}")
        print(f"[DEBUG] Configuration: {marketplace_configuration}")
        logger.debug(f"Found configuration for key: {key}")
        logger.debug(f"Configuration: {marketplace_configuration}")
        
        try:
            validators.url(url)
        except Exception as e:
            print(f"[ERROR] Invalid URL: {url}")
            logger.error(f"Invalid URL: {url}")
            raise Exception("Url is invalid please, check it out: ", url)
        
        request_headers = self.__generate_headers()
        response = requests.get(url=url, headers=request_headers)
        if (response.status_code != 200):
            print(f"[ERROR] Failed to fetch URL. Status code: {response.status_code}")
            logger.error(f"Failed to fetch URL. Status code: {response.status_code}")
            raise Exception(f"Response code was: {response.status_code}, couldn't parse url: {url}")
        
        try:
            soup = BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            print(f"[ERROR] Failed to parse HTML: {e}")
            logger.error(f"Failed to parse HTML: {e}")
            print(e)
            
        marketplace_fields = marketplace_configuration['fields']
        print(f"[DEBUG] Fields to parse: {marketplace_fields}")
        logger.debug(f"Fields to parse: {marketplace_fields}")

        product = Product()
        product.set_marketplace_key(key)

        for field_config in marketplace_fields:
            field = field_config['name']
            print(f"[DEBUG] Processing field: {field}")
            logger.debug(f"Processing field: {field}")
            try:
                value = self.__get_field_value(soup, field_config, field)
                print(f"[DEBUG] Extracted value for {field}: {value}")
                logger.debug(f"Extracted value for {field}: {value}")
                
                if field == 'price':
                    price = self.__extract_price(value)
                    currency = self.__extract_currency(value)
                    print(f"[DEBUG] Extracted price: {price}, currency: {currency}")
                    logger.debug(f"Extracted price: {price}, currency: {currency}")
                    product.set_price(price)
                    product.set_currency(currency)
                if field == 'title':
                    product.set_name(value)
            except Exception as e:
                print(f"[ERROR] Error processing field {field}: {e}")
                logger.error(f"Error processing field {field}: {e}")
                continue
                
        print(f"[DEBUG] Final product: {product.__dict__}")
        logger.debug(f"Final product: {product.__dict__}")
        return product
    
    def __extract_price(self, text):
        if text is None:
            logger.debug("Price text is None")
            return None

        s = str(text).replace('\u00A0', '').strip()
        logger.debug(f"Price text after initial cleaning: {s}")
        
        num = re.sub(r'[^\d.,]', '', s)
        logger.debug(f"Price text after removing non-numeric: {num}")

        if num.count(',') > 1:
            num = num.replace(',', '')
        elif num.count(',') == 1 and num.count('.') == 0:
            num = num.replace(',', '.')
        else:
            num = re.sub(r'(?<=\d)[\s,](?=\d{3}\b)', '', num)
        
        logger.debug(f"Price text after number formatting: {num}")

        try:
            result = float(num)
            logger.debug(f"Successfully converted price to float: {result}")
            return result
        except ValueError as e:
            logger.error(f"Failed to convert price to float: {e}")
            return None

    def __extract_currency(self, text):
        if text is None:
            logger.debug("Currency text is None")
            return None

        s = str(text)
        logger.debug(f"Extracting currency from: {s}")

        sym_match = re.search(r'[\$\€\£\¥\₹\₽\₩\₪\฿\₫\₦\₴]', s)
        if sym_match:
            currency = sym_match.group()
            logger.debug(f"Found currency symbol: {currency}")
            return currency

        code_match = re.search(
            r'\b(?:USD|EUR|GBP|JPY|AUD|CAD|CHF|CNY|RUB|KRW|INR|UAH|PLN|NZD)\b',
            s, flags=re.IGNORECASE
        )
        if code_match:
            currency = code_match.group().upper()
            logger.debug(f"Found currency code: {currency}")
            return currency

        logger.debug("No currency found")
        return None
    
    def __get_field_value(self, object_to_parse, field_params, field_title):
        logger.debug(f"Getting value for field: {field_title}")
        logger.debug(f"Field parameters: {field_params}")
        
        div_class = field_params['html_div_class']
        element_in_div_type = field_params['html_element_in_div_type']
        element_in_div_classes = field_params['html_element_in_div_class']
        
        field_div = object_to_parse.find('div', class_=div_class)
        if field_div is None:
            logger.error(f"Div class '{div_class}' not found for field '{field_title}'")
            raise Exception(f"Div class for the '{field_title}' field couldn't be found, please check it.")
            
        field_div_element = None
        # Filter out empty strings from the classes list
        valid_classes = [cls for cls in element_in_div_classes if cls.strip()]
        if len(valid_classes) > 0:
            for element_in_div_class in valid_classes:
                field_div_element = field_div.find_all(element_in_div_type, class_=element_in_div_class)
                if len(field_div_element) != 0:
                    logger.debug(f"Found element with class: {element_in_div_class}")
                    break
        else:
            print(f"element_in_div_classes is empty or contains only empty strings")
            field_div_element = field_div.find_all(element_in_div_type)
                
        if len(field_div_element) == 0:
            logger.error(f"No elements found for field '{field_title}'")
            raise Exception(f"Element '{element_in_div_type}' inside '{div_class}' div for the '{field_title}' field couldn't be found, please check it.")
            
        field_value = field_div_element[0].text.strip()
        logger.debug(f"Extracted value: {field_value}")
        return field_value
        
    def __find_configuration_by_url(self, url):
        logger.debug(f"Finding configuration for URL: {url}")
        configurations = self.configuration_object
        logger.debug(f"Available configurations: {configurations}")
        
        for key in configurations:
            marketplace_urls = configurations[key]['marketplace_url']
            print(f"marketplace_urls: {marketplace_urls}")
            logger.debug(f"Checking URLs for {key}: {marketplace_urls}")  
            for marketplace_url in marketplace_urls:
                if marketplace_url in url:
                    print(f"{marketplace_url} is in {url}")
                    logger.debug(f"Found matching configuration: {key}")
                    return configurations[key], key
                    
        logger.error(f"No configuration found for URL: {url}")
        raise Exception(f"Couldn't find configuration for the following url: {url}")

    def __generate_headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
            "Accept-Language": "en-US,en;q=0.5"
        }
        return headers
