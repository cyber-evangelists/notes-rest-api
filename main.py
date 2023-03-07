from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel, Field
from bson import ObjectId
import uvicorn

client = MongoClient("mongodb://localhost:27017/")
db = client["notes"]
collection = db["notes"]


app = FastAPI()


class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    description: str

@app.post("/notes")
async def create_note(note: Note):
    note_dict = note.dict()
    note_dict.pop("id")
    result = collection.insert_one(note_dict)
    note.id = str(result.inserted_id)
    return note

@app.get("/notes")
async def read_all_notes():
    notes = []
    for note_dict in collection.find():
        note_dict["id"] = str(note_dict.pop("_id"))
        notes.append(Note(**note_dict))
    return notes
    
@app.get("/notes/{note_id}")
async def read_note(note_id: str):
    #print(note_id)
    note_dict = collection.find_one({"_id":ObjectId(note_id)})
    #print(note_dict)
    if note_dict:
        note_dict["id"] = str(note_dict.pop("_id"))
        return Note(**note_dict)
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}")
async def update_note(note_id: str, note: Note):
    note_dict = note.dict()
    note_dict.pop("id", None)
    result = collection.update_one({"_id":ObjectId(note_id)}, {"$set": note_dict})
    if result.modified_count == 1:
        note.id = note_id
        return note
    else:
        raise HTTPException(status_code=404, detail="Note not found")

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    result = collection.delete_one({"_id":ObjectId(note_id)})
    if result.deleted_count == 1:
        return {"message": "Note deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Note not found")

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8000, log_level="info", reload=True)
    print("running")