from aiogram import Router

from .channel_info import router as channel_info_router
from .report import router as report_router
from .start import router as start_router
from .subscribe import router as subscribe_router


def get_main_router() -> Router:
    router = Router()
    router.include_router(start_router)
    router.include_router(subscribe_router)
    router.include_router(report_router)
    router.include_router(channel_info_router)
    return router
