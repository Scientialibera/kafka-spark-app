from fastapi import FastAPI
from backend.api.register_device import router as register_device_router
from backend.api.send_stream import router as send_stream_router
from backend.api.get_live_stats import router as get_live_stats_router
from backend.api.get_historical_stats import router as get_historical_stats_router
from backend.api.kafka_topics import router as kafka_topics_router
from backend.tests.streaming.stream import router as test_streaming_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Include all routers
app.include_router(register_device_router)
app.include_router(send_stream_router)
app.include_router(get_live_stats_router)
app.include_router(get_historical_stats_router)
app.include_router(kafka_topics_router)
app.include_router(test_streaming_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Sports Streaming API is running."}
