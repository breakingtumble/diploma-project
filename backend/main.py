from typing import List, Optional
from datetime import timedelta
import logging
import sys

from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie, Query, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

from web_parsing.configuration_loader import ConfigurationLoader
from web_parsing.marketplace_parser import MarketplaceParser
from datetime import datetime

from backend import crud, models, schemas, auth, database

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware immediately after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Create router and OAuth2 scheme after middleware is added
api_router = APIRouter(prefix="/api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_current_user(
    header_token: str = Depends(oauth2_scheme),
    cookie_token: Optional[str] = Cookie(None),
    db: Session = Depends(database.get_db),
):
    token = header_token or cookie_token
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    decoded = auth.decode_access_token(token)
    if not decoded:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    username, role = decoded
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    user.role = role
    return user

def admin_required(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin privileges required")
    return current_user


@api_router.post("/register/", response_model=schemas.UserResponse)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already registered")
    return crud.create_user(db, user)


@api_router.post("/login")
def login_for_access_token(
    credentials: schemas.UserLogin,
    response: Response,
    db: Session = Depends(database.get_db),
):
    user = crud.get_user_by_username(db, credentials.username)
    if not user or not auth.verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")

    expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = auth.create_access_token(
        data={"username": user.username, "role": user.role},
        expires_delta=expires,
    )
    response.set_cookie(
        "access_token", token,
        httponly=True, samesite="lax",
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {"access_token": token, "token_type": "bearer"}


@api_router.get("/protected")
def protected_route(current_user: models.User = Depends(get_current_user)):
    return JSONResponse(
        {"username": current_user.username, "role": current_user.role},
        headers={"Cache-Control": "no-store"}
    )

@api_router.get(
    "/admin/users/",
    response_model=List[schemas.UserResponse],
    dependencies=[Depends(admin_required)]
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
):
    return crud.get_users(db, skip=skip, limit=limit)

@api_router.get(
    "/admin/users/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(admin_required)]
)
def read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@api_router.put(
    "/admin/users/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(admin_required)]
)
def edit_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(database.get_db),
):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return crud.update_user(db, db_user, user_update)


@api_router.delete(
    "/admin/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_required)]
)
def delete_user(user_id: int, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    crud.delete_user(db, db_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@api_router.post(
    "/products/by_url",
    response_model=schemas.DetailedProduct
)
def product_by_url(
    req: schemas.URLRequest,
    db: Session = Depends(database.get_db)
):
    logger.debug(f"Received request to parse product from URL: {req.url}")
    
    # DB lookup
    pr = crud.get_product_by_url(db, req.url)
    if pr:
        logger.debug(f"Found existing product in database with ID: {pr.id}")
        return crud.get_detailed_product_response_by_id(db, pr.id)

    # live parse
    try:
        logger.debug("Product not found in database, attempting live parse")
        config = ConfigurationLoader(
            database.DATABASE_URL,
            "web_parsing/configuration/config_new.json",
            "web_parsing/configuration/required_fields_new.json"
        ).get_configuration_object()
        logger.debug("Configuration loaded successfully")
        
        parser = MarketplaceParser(config)
        logger.debug("Parser initialized, starting product parsing")
        parsed = parser.parse_product_by_url(req.url)
        logger.debug(f"Product parsed successfully: {parsed.__dict__}")
    except Exception as e:
        msg = str(e)
        logger.error(f"Error during product parsing: {msg}")
        lower = msg.lower()
        if "invalid" in lower:
            code = status.HTTP_422_UNPROCESSABLE_ENTITY
        elif "response code was" in lower or "couldn't parse url" in lower:
            code = status.HTTP_502_BAD_GATEWAY
        elif "couldn't find configuration" in lower:
            code = status.HTTP_400_BAD_REQUEST
        else:
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=code, detail=msg)

    # save product & price
    logger.debug("Saving parsed product to database")
    prod = crud.create_product_from_entity(db, parsed, req.url)
    parsed_date = datetime.utcnow()
    crud.create_parsed_product(db, prod.id, parsed.get_price(), parsed_date)
    logger.debug(f"Product saved successfully with ID: {prod.id}")

    # return freshly saved detailed object
    result = crud.get_detailed_product_response_by_id(db, prod.id)
    if not result:
        logger.error("Failed to build product response after saving")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to build product response")
    logger.debug("Successfully returning detailed product response")
    return result

@api_router.get(
    "/products/{product_id}",
    response_model=schemas.DetailedProduct
)
def product_by_id(
    product_id: int,
    db: Session = Depends(database.get_db)
):
    pr = crud.get_detailed_product_response_by_id(db, product_id)
    if not pr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return pr

@api_router.get(
    "/products/",
    response_model=List[schemas.BasicProduct]
)
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    return crud.get_basic_products_response(db, skip, limit)

@api_router.get(
    "/subscriptions",
    response_model=List[schemas.BasicProduct],
    summary="List products you're subscribed to"
)
def list_user_subscriptions(
    user_id: Optional[int] = Query(None, description="(admin only) user ID whose subscriptions to fetch"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    if user_id is not None and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required to fetch others' subscriptions")
    target = user_id if (user_id and current_user.role == "admin") else current_user.id
    return crud.get_basic_subscribed_products_response(db, target)

@api_router.post(
    "/subscriptions",
    response_model=schemas.SubscriptionResponse,
    status_code=status.HTTP_201_CREATED
)
def subscribe_user(
    req: schemas.SubscriptionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session   = Depends(database.get_db)
):
    if not crud.get_product_by_id(db, req.product_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    if crud.get_subscription(db, current_user.id, req.product_id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Already subscribed")

    return crud.create_subscription(db, current_user.id, req.product_id)    

@api_router.delete(
    "/subscriptions",
    status_code=status.HTTP_200_OK,
    summary="Unsubscribe from a product"
)
def unsubscribe_user(
    product_id: int = Query(
        ..., 
        description="ID of the product to unsubscribe"
    ),
    user_id: Optional[int] = Query(
        None,
        description="(admin only) target user's ID; ignored for non-admins"
    ),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You may only unsubscribe your own subscriptions"
        )

    target_user_id = (
        user_id 
        if (current_user.role == "admin" and user_id is not None)
        else current_user.id
    )

    sub = crud.get_subscription(db, target_user_id, product_id)
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    crud.delete_subscription(db, sub)

    return {"message": "Subscription deleted successfully"}

@api_router.get("/products/{product_id}/price_history")
def get_price_history(product_id: int, period: str = "1m", db: Session = Depends(database.get_db)):
    from collections import defaultdict
    now = datetime.utcnow()
    if period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "1m":
        start_date = now - timedelta(days=30)
    elif period == "3m":
        start_date = now - timedelta(days=90)
    elif period == "1y":
        start_date = now - timedelta(days=365)
    elif period == "all":
        start_date = None
    else:
        start_date = now - timedelta(days=30)

    query = db.query(models.ParsedProduct).filter(models.ParsedProduct.product_id == product_id)
    if start_date:
        query = query.filter(models.ParsedProduct.etl_date >= start_date)
    query = query.order_by(models.ParsedProduct.etl_date)
    results = query.all()

    # Group by date (YYYY-MM-DD)
    grouped = defaultdict(list)
    for p in results:
        day = p.etl_date.date().isoformat()
        grouped[day].append((p.etl_date, float(p.price_proceeded)))

    out = []
    for day in sorted(grouped.keys()):
        day_prices = grouped[day]
        # Always keep the first price
        last_price = None
        for i, (dt, price) in enumerate(day_prices):
            if i == 0 or price != last_price:
                out.append({"date": dt.isoformat(), "price": price})
                last_price = price
        # If all prices are the same, only one will be kept

    # If only one date, return just that
    if len(out) == 0 and results:
        p = results[0]
        return [{"date": p.etl_date.isoformat(), "price": float(p.price_proceeded)}]
    return out

@app.get("/api/subscriptions")
async def get_subscriptions(
    current_user: models.User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(6, ge=1, le=50),
    db: Session = Depends(database.get_db)
):
    """Get all subscriptions for the current user with pagination"""
    skip = (page - 1) * per_page
    subscriptions = crud.get_user_subscriptions(db, current_user.id, skip=skip, limit=per_page)
    total = crud.get_user_subscriptions_count(db, current_user.id)
    
    return {
        "items": subscriptions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@api_router.get("/subscriptions/check")
def check_subscription(
    product_id: int = Query(..., description="ID of the product to check"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    sub = crud.get_subscription(db, current_user.id, product_id)
    return {"subscribed": sub is not None}

@api_router.get("/marketplace-configurations", response_model=schemas.MarketplaceConfigurations)
def get_marketplace_configurations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get all marketplace configurations"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access marketplace configurations"
        )
    
    configs = crud.get_marketplace_configurations(db)
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No marketplace configurations found"
        )
    return configs

@api_router.put("/marketplace-configurations/{config_name}", response_model=schemas.MarketplaceConfigurations)
def update_marketplace_configuration(
    config_name: str,
    updated_config: schemas.MarketplaceConfigUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Update a specific marketplace configuration"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update marketplace configurations"
        )
    
    result = crud.update_marketplace_configuration(db, config_name, updated_config.model_dump())
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with name '{config_name}' not found"
        )
    return result

@api_router.get("/marketplace-configurations/{config_name}", response_model=schemas.MarketplaceConfig)
def get_marketplace_configuration(
    config_name: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get a specific marketplace configuration by name"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access marketplace configurations"
        )
    
    config = crud.get_marketplace_configuration_by_name(db, config_name)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with name '{config_name}' not found"
        )
    return config

@api_router.post("/marketplace-configurations", response_model=schemas.MarketplaceConfigurations)
def add_marketplace_configuration(
    new_config: schemas.MarketplaceConfigUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Add a new marketplace configuration"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can add marketplace configurations"
        )
    result = crud.add_marketplace_configuration(db, new_config)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration with name '{new_config.name}' already exists"
        )
    return schemas.MarketplaceConfigurations(root=result)

@api_router.delete("/marketplace-configurations/{config_name}", status_code=204)
def delete_marketplace_configuration(
    config_name: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Delete a marketplace configuration by name"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete marketplace configurations"
        )
    deleted = crud.delete_marketplace_configuration(db, config_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration with name '{config_name}' not found"
        )
    return Response(status_code=204)

@api_router.get("/marketplace-configs/short")
def get_marketplace_configs_short(db: Session = Depends(database.get_db)):
    """Public endpoint to get all marketplace configuration names and their first marketplace_url."""
    configs = crud.get_marketplace_configurations(db)
    if not configs:
        return []
    result = []
    for cfg in configs:
        url = None
        if isinstance(cfg.get('marketplace_url'), list):
            url = cfg['marketplace_url'][0] if cfg['marketplace_url'] else None
        else:
            url = cfg.get('marketplace_url')
        result.append({
            'name': cfg.get('name'),
            'marketplace_url': url
        })
    return result

app.include_router(api_router)