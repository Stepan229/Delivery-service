import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware


from api.handlers import package_router

from logging_config import setup_logging

import logging
setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

# sentry configuration
# sentry_sdk.init(
#     dsn="https://localhost/",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production,
#     traces_sample_rate=1.0,
# )

#########################
# BLOCK WITH API ROUTES #
#########################

# create instance of the app
app = FastAPI(title="luchanos-oxford-university")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(package_router, prefix="/package", tags=["package"])
app.include_router(main_api_router)

print("App started", str(package_router))
if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(app, host="127.0.0.1", port=8000)