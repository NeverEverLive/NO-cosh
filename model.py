from pydantic import BaseModel, Field, EmailStr


class OrderSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(default=None)
    price: int = Field(default=None)

    class Config:
        schema_extra = {
            "order_demo": {
                "title": "some title", 
                "price": 123, 
            }
        }


class UserSchema(BaseModel):
    id: int = Field(default=None)
    login: str = Field(default=None)
    password: str = Field(default=None)
    name: str = Field(default=None)
    latitude: float = Field(default=None)
    longitude: float = Field(default=None)
    role: str = Field(default=None)
    balance: float = Field(default=None)
    phone: str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo": {
                "login": "test",
                "password": "123",
                "name": "test",
                "latitude": 123,
                "longitude": 123,
                "role": "Seller",
                "phone": "123" 
            }
        }


class UserLoginSchema(BaseModel):
    id: int = Field(default=None)
    login: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        the_schema = {
            
            "user_demo": {
                "name": "Bek",
                "email": "help@example.com",
                "price": "123" 
            }
        }


class BlackListSchema(BaseModel):
    id: int = Field(default=None)
    access_token: str = Field(default=None)
    access_date: int = Field(default=None)
    refresh_token: int = Field(default=None)
    refresh_date: int = Field(default=None)
    userID: int = Field(default=None)


class Category(BaseModel):
    id: int = Field(default=None)
    category_name: str = Field(default=None)
    description: str = Field(default=None)
    picture: str = Field(default=None)
    
    # id: int
    # category_name: str
    # description: str
    # picture: str

    class Config:
        orm_mode = True