from fastapi import FastAPI

from components.sekai_cheese import router as sekai_cheese_router

app = FastAPI()

# Add the router to the app
app.include_router(sekai_cheese_router)
