from .infrastructure.configuration.container import create_application
from .infrastructure.web.app import create_web_app

app = create_web_app(create_application())
