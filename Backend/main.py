from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import config

from routers.health      import router as health_router
from routers.predictions import router as predictions_router
from routers.query       import router as query_router
from routers.charts      import router as charts_router
from routers.unified     import router as unified_router
from routers.download    import router as download_router
from routers.merge       import router as merge_router

app = FastAPI(
    title       = "Credit Union AI Skill",
    description = "Unified skill for Credit Union ML agent",
    version     = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

app.include_router(health_router)
app.include_router(predictions_router)
app.include_router(query_router)
app.include_router(charts_router)
app.include_router(unified_router)
app.include_router(download_router)
app.include_router(merge_router)
