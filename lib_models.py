import json
import os
from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field

#Basemodel: parent model for all models we created 
#Field : let us attach rules

app=FastAPI()

BASE_FOLDER= os.path.dirname(os.path.abspath(__file__))
print(BASE_FOLDER)

DATA_FILE=os.path.join(BASE_FOLDER,"books.json")
print(DATA_FILE)

initial_books = [ 

    {"id": 1, "title": "Wings of Fire", "author": "A. P. J. Abdul Kalam", "year": 1999, "available": True}, 

    {"id": 2, "title": "The Discovery of India", "author": "Jawaharlal Nehru", "year": 1946, "available": True}, 

    {"id": 3, "title": "Train to Pakistan", "author": "Khushwant Singh", "year": 1956, "available": False}, 

    {"id": 4, "title": "The God of Small Things", "author": "Arundhati Roy", "year": 1997, "available": True}, 

] 

def save_books():
    with open(DATA_FILE,"w",encoding="utf-8") as file:
        json.dump(books,file,indent=2)


def load_books():
    if not os.path.exists(DATA_FILE):
        starting_list=[]
        for book in initial_books:
            starting_list.append(dict(book))
        with open(DATA_FILE,"w",encoding="utf-8") as file:
            json.dump(starting_list,file,indent=2)

        return starting_list

    with open(DATA_FILE,"r",encoding="utf-8") as file:
        return json.load(file)
books=load_books()

#Models = shape of the api which api can take as i/p provide or as o/p

class Book(BaseModel):
#POST
    title: str = Field(min_length =1, max_length=100, example= "Malgudi Days")
    author: str = Field(min_length =1, max_length=50)
    year: int= Field(ge=0, le=2100)

@app.post("/books",summary = "Add a book")

def add_book(body : Book):

    for book in books:
        if (book["title"]==body.title and book["author"]==body.author):
            raise HTTPException(status_code=409, detail="This Book Already Exists")

#short notation
    new_id= max([book["id"] for book in books],default =0)+1
    book={"id": new_id,"title":body.title ,"author":body.author,"year":body.year}

    books.append(book)
    save_books()
    return book

#helper fn without an endpoint
def find_position(book_id):
    for position in range(len(books)):
        if books[position]["id"] == book_id:
            return position
    raise HTTPException(status_code=404, detail="Book not Found")


#get a book by id - path parameter
@app.get("/books/{book_id}", response_model=Book, summary="Get one book by its id")
def get_book(book_id : int):
    return books[find_position(book_id)]

#PUT /book/{book_id} - Replace a book completely

@app.put("/books/{book_id}",response_model=Book,summary="Replace a Book")

def replace_book(book_id : int, body : Book):
    position =find_position(book_id)

    books[position]= {"id":book_id,"title":body.title, "author": body.author,"year":body.year,"available": True}
    save_books()
    return books[position]

@app.get("/books", summary="List all Books")

#def list_books():
    #return books
def list_books(author : str |None =None, year_after : int =1700):
    result=[]
    for book in books:
        if author is not None and author.lower not in book["author"].lower():
            continue
        if book["year"] <= year_after:
            continue
        result.append(book)
    
    return result

#delete
@app.delete("/books/{book_id}",summary="Delete a Book")
def delete_book(book_id : int):
    books.pop(find_position(book_id))
    save_books()

#patch : partial update - /books/{book_id} = change some fields of book

class BookUpdate(BaseModel):
    title: str | None = Field(default = None,min_length =1, max_length=100, example= "Malgudi Days")
    author: str | None = Field(default = None,min_length =1, max_length=50)
    year: int | None= Field(default = None,ge=0, le=2100)

@app.patch("/books/{book_id}",summary="Change some fields of book")
def update_book(book_id : int, body: BookUpdate):
    position = find_position(book_id)

    print(body)

    changes = body.model_dump(exclude_none=True)

    print(changes)

    for key ,value in changes.items():
        books[position][key]=value
    
    save_books()
    
    return books[position]