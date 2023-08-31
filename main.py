import sqlalchemy
from sqlalchemy import Column, Integer, String, MetaData
from databases import Database
from fastapi import FastAPI, Request

DATABASE_URL = "postgresql://postgres:1@localhost:5432/store"

database = Database(DATABASE_URL)
metadata = MetaData()

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine)

app = FastAPI()


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/books/")
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)


@app.post("/books/")
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}
