from fastapi import FastAPI
from app.db.session import get_session, init_db
from app.api.scrape import router as scrape_router
from app.api.email import router as email_router
from app.api.auth import router as auth_router
from app.api.email_management import router as email_management_router
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield



app = FastAPI(
    lifespan=lifespan,
    title="Email Marketing",
    description="This is a backend project for email marketing",
    version= "1.1",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://nextmail.thinkedgeconsultancy.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape_router)
app.include_router(email_router)
app.include_router(auth_router)
app.include_router(email_management_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Email Marketing! Version 1.1"}

if "__main__" == __name__:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
