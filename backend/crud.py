from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from backend import models, schemas
from web_parsing.product import Product
from backend.auth import hash_password
from web_parsing.configuration_loader import MarketplaceConfiguration

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password),
        email=user.email,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, db_user: models.User, user_in: schemas.UserUpdate):
    data = user_in.dict(exclude_unset=True)
    for field, val in data.items():
        setattr(db_user, field, val)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: models.User):
    db.delete(db_user)
    db.commit()

def get_product_by_url(db: Session, url: str):
    return db.query(models.Product).filter(models.Product.url == url).first()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()

def create_product_from_entity(db: Session, entity, url: str) -> models.Product:
    prod = models.Product(
        marketplace_key=entity.get_marketplace_key(),
        url=url,
        name=entity.get_name(),
        currency=entity.get_currency()
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod

def create_parsed_product(db: Session, product_id: int, price: float, etl_date: datetime):
    pp = models.ParsedProduct(
        product_id=product_id,
        price_proceeded=price,
        etl_date=etl_date
    )
    db.add(pp)
    db.commit()
    db.refresh(pp)
    return pp

def get_subscribed_products(db: Session, user_id: int):
    return (
        db.query(models.Product)
          .join(
             models.UserProductSubscription,
             models.Product.id == models.UserProductSubscription.product_id
          )
          .filter(models.UserProductSubscription.user_id == user_id)
          .all()
    )

def get_subscription(db: Session, user_id: int, product_id: int):
    return (
        db.query(models.UserProductSubscription)
          .filter(
            models.UserProductSubscription.user_id  == user_id,
            models.UserProductSubscription.product_id == product_id
          )
          .first()
    )

def create_subscription(db: Session, user_id: int, product_id: int):
    sub = models.UserProductSubscription(user_id=user_id, product_id=product_id)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def delete_subscription(db: Session, subscription: models.UserProductSubscription):
    db.delete(subscription)
    db.commit()

def get_price_stats(db: Session, product_id: int):
    latest = (
        db.query(models.ParsedProduct)
          .filter(models.ParsedProduct.product_id == product_id)
          .order_by(desc(models.ParsedProduct.etl_date))
          .first()
    )
    if not latest:
        return 0.0, 0.0, "Product price didn't change"

    current = float(latest.price_proceeded)
    prev = (
        db.query(models.ParsedProduct)
          .filter(
             models.ParsedProduct.product_id == product_id,
             models.ParsedProduct.price_proceeded != latest.price_proceeded
          )
          .order_by(desc(models.ParsedProduct.etl_date))
          .first()
    )
    if not prev:
        return current, 0.0, "Product price didn't change"

    previous = float(prev.price_proceeded)
    diff = current - previous
    if diff > 0:
        msg = "Product price has risen"
    elif diff < 0:
        msg = "Product price has dropped"
    else:
        msg = "Product price didn't change"
    return current, diff, msg

def build_basic_product(db: Session, prod: models.Product) -> schemas.BasicProduct:
    current, diff, deviation = get_price_stats(db, prod.id)
    setattr(prod, "current_price", current)
    setattr(prod, "price_difference", diff)
    setattr(prod, "deviation_string", deviation)
    return schemas.BasicProduct.from_orm(prod)


def build_detailed_product(db: Session, prod: models.Product) -> schemas.DetailedProduct:
    basic = build_basic_product(db, prod)
    detailed = schemas.DetailedProduct.from_orm(prod)
    detailed.current_price    = basic.current_price
    detailed.price_difference = basic.price_difference
    detailed.deviation_string = basic.deviation_string
    return detailed

def get_basic_products_response(db: Session, skip: int = 0, limit: int = 100):
    return [build_basic_product(db, p) for p in get_products(db, skip, limit)]


def get_detailed_product_response_by_id(db: Session, product_id: int):
    # Get the basic product data
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None

    # Get the latest price
    latest_price = db.query(models.ParsedProduct)\
        .filter(models.ParsedProduct.product_id == product_id)\
        .order_by(models.ParsedProduct.etl_date.desc())\
        .first()

    # Get the previous price
    prev_price = db.query(models.ParsedProduct)\
        .filter(models.ParsedProduct.product_id == product_id)\
        .order_by(models.ParsedProduct.etl_date.desc())\
        .offset(1)\
        .first()

    # Get the latest price prediction
    latest_prediction = db.query(models.ProductPricePrediction)\
        .filter(models.ProductPricePrediction.product_id == product_id)\
        .order_by(models.ProductPricePrediction.etl_date.desc())\
        .first()

    if not latest_price:
        return None

    current_price = float(latest_price.price_proceeded)
    prev_price_value = float(prev_price.price_proceeded) if prev_price else current_price
    price_diff = current_price - prev_price_value
    deviation = (price_diff / prev_price_value * 100) if prev_price_value != 0 else 0

    # Generate text explanation based on price difference
    if price_diff > 0:
        deviation_text = "Product price has risen"
    elif price_diff < 0:
        deviation_text = "Product price has dropped"
    else:
        deviation_text = "Product price didn't change"

    # Format predicted price to 1 decimal place
    predicted_price = round(float(latest_prediction.predicted_price), 1) if latest_prediction else None
    # Format change index to 1 decimal place
    change_index = round(float(latest_prediction.change_index), 2) if latest_prediction else None

    return {
        "id": product.id,
        "marketplace_key": product.marketplace_key,
        "url": product.url,
        "name": product.name,
        "currency": product.currency,
        "current_price": current_price,
        "price_difference": price_diff,
        "deviation_string": f"{deviation:+.2f}%",
        "deviation_text": deviation_text,
        "predicted_price": predicted_price,
        "change_index": change_index
    }


def get_detailed_product_response_by_url(db: Session, url: str):
    prod = get_product_by_url(db, url)
    return prod and build_detailed_product(db, prod)

def truncate_name(name, max_length=50):
    return name if len(name) <= max_length else name[:max_length-3] + '...'

def get_basic_subscribed_products_response(db: Session, user_id: int):
    prods = (
        db.query(models.Product)
          .join(models.UserProductSubscription,
                models.Product.id == models.UserProductSubscription.product_id)
          .filter(models.UserProductSubscription.user_id == user_id)
          .all()
    )
    result = []
    for p in prods:
        current, diff, deviation = get_price_stats(db, p.id)
        percent = 0.0
        if current and diff:
            try:
                percent = round((diff / (current - diff)) * 100, 2)
            except ZeroDivisionError:
                percent = 0.0
        if diff > 0:
            status = "up"
        elif diff < 0:
            status = "down"
        else:
            status = "same"
        result.append({
            "id": p.id,
            "name": truncate_name(p.name),
            "price": p.current_price if hasattr(p, 'current_price') else current,
            "currency": getattr(p, 'currency', ''),
            "current_price": current,
            "price_difference": diff,
            "price_difference_percent": percent,
            "status": status
        })
    return result

def get_user_subscriptions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all subscriptions for a user with pagination"""
    return db.query(models.Product).join(models.UserProductSubscription).filter(
        models.UserProductSubscription.user_id == user_id
    ).offset(skip).limit(limit).all()

def get_user_subscriptions_count(db: Session, user_id: int) -> int:
    """Get total count of subscriptions for a user"""
    return db.query(models.Product).join(models.UserProductSubscription).filter(
        models.UserProductSubscription.user_id == user_id
    ).count()

def get_marketplace_configurations(db: Session):
    """Get all marketplace configurations"""
    config = db.query(MarketplaceConfiguration).first()
    if not config:
        return None
    return config.config_json.get('marketplace_configurations', [])

def update_marketplace_configuration(db: Session, config_name: str, updated_config: dict):
    """Update a specific marketplace configuration in the database"""
    config = db.query(MarketplaceConfiguration).first()
    if not config:
        return None
    
    # Get current configurations
    current_configs = config.config_json.get('marketplace_configurations', [])
    
    # Update the specific configuration
    updated_configs = []
    for cfg in current_configs:
        if cfg['name'] == config_name:
            updated_configs.append(updated_config)
        else:
            updated_configs.append(cfg)
    
    # Update the entire config_json field
    config.config_json['marketplace_configurations'] = updated_configs
    
    # Force SQLAlchemy to detect the change
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return updated_configs

def get_marketplace_configuration_by_name(db: Session, config_name: str):
    """Get a specific marketplace configuration by name"""
    config = db.query(MarketplaceConfiguration).first()
    if not config:
        return None
    
    configs = config.config_json.get('marketplace_configurations', [])
    for cfg in configs:
        if cfg['name'] == config_name:
            return cfg
    return None

def add_marketplace_configuration(db: Session, new_config):
    """Add a new marketplace configuration to the database"""
    import json
    print("[DEBUG] Incoming new_config:", new_config)
    config = db.query(MarketplaceConfiguration).first()
    if not config:
        print("[DEBUG] No config row found in DB.")
        return None
    configs = config.config_json.get('marketplace_configurations', [])
    print("[DEBUG] Current configs before append:", configs)
    for cfg in configs:
        if cfg['name'] == new_config.name:
            print(f"[DEBUG] Duplicate config name found: {new_config.name}")
            return None
    new_cfg_dict = new_config.model_dump()
    print("[DEBUG] Appending new config dict:", new_cfg_dict)
    configs.append(new_cfg_dict)
    print("[DEBUG] Configs after append:", configs)
    config.config_json['marketplace_configurations'] = configs
    db.add(config)
    db.commit()
    db.refresh(config)
    print("[DEBUG] Saved config_json:", config.config_json)
    return configs

def delete_marketplace_configuration(db: Session, config_name: str):
    """Delete a marketplace configuration by its name"""
    config = db.query(MarketplaceConfiguration).first()
    if not config:
        return False
    configs = config.config_json.get('marketplace_configurations', [])
    new_configs = [cfg for cfg in configs if cfg['name'] != config_name]
    if len(new_configs) == len(configs):
        return False  # No config with that name found
    config.config_json['marketplace_configurations'] = new_configs
    db.add(config)
    db.commit()
    db.refresh(config)
    return True
