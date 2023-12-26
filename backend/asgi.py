import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import subprocess
 
# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
 
# Initialize Django
django.setup()
 
# Run the scheduler in a separate process
#subprocess.Popen(["python", "scheduler.py"])
 
# Import your routing setup after Django setup
import myapp.routing  # Replace 'myapp' with your app name
 
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            myapp.routing.websocket_urlpatterns
        )
    ),
})