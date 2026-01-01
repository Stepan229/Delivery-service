import typer
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from starlette_exporter import handle_metrics
from starlette_exporter import PrometheusMiddleware
from scheduler.scheduler import start_scheduler
from scheduler.jobs import add_cost_delivery
from endpoints.package import package_router
from endpoints.health_check import health_check_router
import asyncio
from core.settings import API_HOST, API_PORT
from services.logging_config import setup_logging

import logging
setup_logging()



cli = typer.Typer()

logger = logging.getLogger(__name__)

app = FastAPI(title="luchanos-oxford-university")


# create instance of the app
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# create the instance for the routes
main_api_router = APIRouter()

# set routes to the app instance
main_api_router.include_router(package_router, prefix="/package", tags=["package"])
main_api_router.include_router(health_check_router, prefix="/health", tags=["health"])
app.include_router(main_api_router)



@cli.command()
def run_api(
    host: str = typer.Option(API_HOST, "--host", "-h"),
    port: int = typer.Option(API_PORT, "--port", "-p")
):
    logger.info("API запущено")
    uvicorn.run(app, host=host, port=port)


@cli.command()
def run_scheduler():
    start_scheduler()

@cli.command()
def run_add_cost_delivery():
    asyncio.run(add_cost_delivery())

if __name__ == "__main__":
    cli()


