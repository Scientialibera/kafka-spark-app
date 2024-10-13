from fastapi import FastAPI
from backend.api.register_device import router as register_device_router
from backend.api.send_stream import router as send_stream_router

app = FastAPI()

# Include all routers
app.include_router(register_device_router)
app.include_router(send_stream_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Streaming API!"}
