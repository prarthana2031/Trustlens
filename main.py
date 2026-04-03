from fastapi import FastAPI
import os

app = FastAPI()

#Environment variables

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

@app.get("/")
def root():
    return {"message": "Working!",
            "supabase_loaded":SUPABASE_URL is not None}




