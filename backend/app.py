from fastapi import FastAPI
from backend.api.register_device import router as register_device_router
from backend.api.send_stream import router as send_stream_router
from backend.api.get_live_stats import router as get_live_stats_router

app = FastAPI()

# Include all routers
app.include_router(register_device_router)
app.include_router(send_stream_router)
app.include_router(get_live_stats_router)

@app.get("/")
def read_root():
    return {"message": "Sports Streaming API is running."}
