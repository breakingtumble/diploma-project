from ConfigurationLoader import ConfigurationLoader
from MarketplaceParser import MarketplaceParser
import csv

csvFile = None
with open('data/data.csv', mode='r') as file:
    csvFile = csv.DictReader(file, fieldnames=['marketplace_key', 'url'])

for row in csvFile:
    print(csvFile['url'])
config = ConfigurationLoader("configuration/config_new.json", "configuration/required_fields_new.json").get_configuration_object()
print(config)

parser = MarketplaceParser(config)

print(parser.parse_product_by_url('https://rozetka.com.ua/'))
