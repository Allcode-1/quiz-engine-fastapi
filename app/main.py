from fastapi import FastAPI
from app.api.endpoints import users, quizzes, auth, categories

app = FastAPI(title="Quiz Engine")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])

@app.get("/")
def root():
    return {"message": "Quiz Engine API is running"}