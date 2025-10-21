#!/usr/bin/env python3
"""
Простой HTTP сервер для healthcheck на Railway
"""

import asyncio
import threading
from aiohttp import web
from loguru import logger


class HealthServer:
    """HTTP сервер для healthcheck"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.server = None
        self.runner = None
    
    def setup_routes(self):
        """Настройка маршрутов"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/', self.health_check)
        self.app.router.add_get('/status', self.health_check)
    
    async def health_check(self, request):
        """Healthcheck endpoint"""
        return web.json_response({
            "status": "ok",
            "service": "autonomous_trading_bot",
            "version": "2.0"
        })
    
    async def start(self):
        """Запуск сервера"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.server = web.TCPSite(
                self.runner, 
                '0.0.0.0', 
                self.port
            )
            
            await self.server.start()
            logger.info(f"Health server started on port {self.port}")
            
        except Exception as e:
            logger.error(f"Error starting health server: {e}")
            raise
    
    async def stop(self):
        """Остановка сервера"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Health server stopped")


async def run_health_server():
    """Запуск health сервера в отдельном потоке"""
    server = HealthServer()
    await server.start()
    
    # Держим сервер запущенным
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(run_health_server())
