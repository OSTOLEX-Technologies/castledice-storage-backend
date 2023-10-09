from app import app
from controllers import game_controllers

@app.get("/")
async def root():
    return {"message": "Hello World"}
