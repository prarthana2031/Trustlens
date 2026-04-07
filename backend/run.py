from app.main import app
import uvicorn
import os

if __name__ == "__main__":
    # Get port from Render (important)
    port = int(os.environ.get("PORT", 10000))
    
    # Run FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=port)