from app import app  # Replace with the actual module where your Flask app is defined
from asgiref.wsgi import WsgiToAsgi

asgi_app = WsgiToAsgi(app)
