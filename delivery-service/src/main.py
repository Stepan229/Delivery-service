import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware
from scheduler.scheduler import lifespan

from api.handlers import package_router

from logging_config import setup_logging

import logging
setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan, title="luchanos-oxford-university")


# create instance of the app
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(package_router, prefix="/package", tags=["package"])
app.include_router(main_api_router)







if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="127.0.0.1", port=8002)

