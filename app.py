from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import motor.motor_asyncio  # Use motor for async MongoDB operations
from fastapi import HTTPException

from fastapi.middleware.cors import CORSMiddleware


# MongoDB setup
uri = "mongodb+srv://ahamedbasith:4wT8JLcZjWkzPRPI@clusterweb.s5tsj.mongodb.net/?retryWrites=true&w=majority&appName=ClusterWeb"
client = motor.motor_asyncio.AsyncIOMotorClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.portfolio
collection = db.content

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://<frontend-server>"],  # Replace with the URL of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Content(BaseModel):
    html_content: str

@app.post("/update_content/")
async def update_content(html_content: str = Form(...)):
    try:
        result = await collection.update_one(
            {"_id": "content"},
            {"$set": {"html_content": html_content}},
            upsert=True
        )
        if result.modified_count or result.upserted_id:
            return {"message": "Content updated successfully"}
        return {"message": "No changes were made"}
    except Exception as e:
        print(f"Error updating MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Failed to update content mongodb error")


@app.get("/portfolio", response_class=HTMLResponse)
async def portfolio():
    document = await collection.find_one({"_id": "content"})
    if document:
        html_content = document["html_content"]
        return HTMLResponse(content=html_content)
    raise HTTPException(status_code=404, detail="Content not found")
