from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Accept-Language": "en-US,en;q=0.5"
}

def get_product(url):
    response = requests.get(url=url, headers=headers)
    if (response.status_code != 200):
        return None
    soup = BeautifulSoup(response.text, 'lxml')
    product_name = soup.find('div', class_="product-about__right-inner").find_all('h1', class_="title__font")[0].text.strip()
    if (product_name is None):
        return None
    print(product_name) 

get_product("https://hard.rozetka.com.ua/ua/asus-dual-rtx4060ti-o8g-evo/p415015629/")