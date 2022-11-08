from fastapi import FastAPI

from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.middleware.asyncexitstack import ASGIApp
from django.core.asgi import get_asgi_application

from django.conf import settings

app = FastAPI()

django_app = get_asgi_application()

@app.get('/')
async def root():
    return {'message': "Hello World"}

app.mount('/test', WSGIMiddleware(django_app))