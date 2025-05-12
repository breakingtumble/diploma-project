from pydantic import BaseModel, ConfigDict, RootModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role: Optional[str] = "user"

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    username: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email:    Optional[str] = None
    role:     Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(from_attributes=True)

class URLRequest(BaseModel):
    url: str

    model_config = ConfigDict(from_attributes=True)

class SubscriptionCreate(BaseModel):
    product_id: int

    model_config = ConfigDict(from_attributes=True)

class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    product_id: int

    model_config = ConfigDict(from_attributes=True)

# ─── PRODUCT SCHEMAS ─────────────────────────────────────────
class BasicProduct(BaseModel):
    id: int
    marketplace_key: Optional[str]
    url: str
    name: Optional[str]
    currency: Optional[str]

    current_price:    float
    price_difference: float
    deviation_string: str

    model_config = ConfigDict(from_attributes=True)

class DetailedProduct(BasicProduct):
    predicted_price: Optional[float] = None
    change_index: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class MarketplaceField(BaseModel):
    name: str
    html_div_class: str
    html_element_in_div_type: str
    html_element_in_div_class: list[str]

    model_config = ConfigDict(from_attributes=True)

class MarketplaceConfig(BaseModel):
    name: str
    fields: list[MarketplaceField]
    marketplace_url: list[str] | str

    model_config = ConfigDict(from_attributes=True)

class MarketplaceConfigurations(RootModel):
    root: list[MarketplaceConfig]

    model_config = ConfigDict(from_attributes=True)

class MarketplaceConfigUpdate(BaseModel):
    name: str
    fields: list[MarketplaceField]
    marketplace_url: list[str] | str

    model_config = ConfigDict(from_attributes=True)