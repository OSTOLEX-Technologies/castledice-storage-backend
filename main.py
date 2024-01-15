from app import app
from controllers.users_controllers import router as users_router
from controllers.game_controllers import router as game_router
import exceptions_handlers

app.include_router(users_router)
app.include_router(game_router)


@app.get("/")
async def root():
    return {"message": "Castledice storage backend is running"}
