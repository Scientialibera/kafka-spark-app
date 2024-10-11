from fastapi import FastAPI
from backend.api.register_device import router as register_device_router  # Import the router

app = FastAPI()

# Include the router for register_device
app.include_router(register_device_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Streaming API!"}