# This file makes the web_parsing directory a Python package

from .product import Product
from .marketplace_parser import MarketplaceParser
from .configuration_loader import ConfigurationLoader

__all__ = ['Product', 'MarketplaceParser', 'ConfigurationLoader']
