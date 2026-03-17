from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import diplomas

app = FastAPI(
    title="DiploChain Diploma Service",
    version="1.0.0",
    description="Manages diploma lifecycle and status",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(diplomas.router)

@app.on_event("startup")
