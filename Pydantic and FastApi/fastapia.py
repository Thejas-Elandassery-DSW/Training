from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
app = FastAPI()


class Intern(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    supervisor: str

@app.get("/")
def root():
    return {"message": "Hello World"}

student_list = []

@app.post("/create-intern")
def create_item(student: Intern):
    student_list.append(student)
    return student_list

@app.get("/student")
def list_items(id: int):
    for each in student_list:
        if each.id == id:
            return each
    raise HTTPException(status_code=404,detail=f"Student not found with id: {id}")
@app.get("/list-all-students")
def list_items():
    return student_list

# @app.get("/items/{item_id}")
# def get_item(item_id: int):
#     if item_id<len(items):
#         return items[item_id]
#     raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    