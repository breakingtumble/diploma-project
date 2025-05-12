from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, DateTime
from backend.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")

class Product(Base):
    __tablename__ = 'products'
    id               = Column(Integer, primary_key=True, index=True)
    marketplace_key  = Column(String)
    url              = Column(String, unique=True, index=True)
    name             = Column(String)
    currency         = Column(String)

class ParsedProduct(Base):
    __tablename__ = 'parsed_products'
    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey('products.id'))
    price_proceeded  = Column(Numeric)
    etl_date         = Column(DateTime)

class ProductPricePrediction(Base):
    __tablename__ = 'product_price_predictions'
    id               = Column(Integer, primary_key=True, index=True)
    product_id       = Column(Integer, ForeignKey('products.id'))
    predicted_price  = Column(Numeric)
    change_index     = Column(Numeric)
    etl_date         = Column(DateTime)

class UserProductSubscription(Base):
    __tablename__ = 'users_products_subscriptions'
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))