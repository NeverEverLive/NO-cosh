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
    full_name: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo": {
                "name": "Bek",
                "email": "help@example.com",
                "price": "123" 
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    class Config:
        the_schema = {
            "user_demo": {
                "email": "help@example.com",
                "price": "123" 
            }
        }


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