from pydantic import BaseModel , EmailStr, validator

class User(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr

    @validator('age')
    def age_greater_than_18(cls, v):
        if v < 18:
            raise ValueError('age must be greater than 18')
        return v

user = User(id=123, name='Thejas', age=20, email="asd@gmail.com")
print(user)

#For json conversion
jsons = user.json()
print(jsons)

#For dict conversion
dicts = user.dict()
print(dicts)

#From json to pydantic model
user2 = User.parse_raw(jsons)
user2.name = 'Thejas2'
print(user2)