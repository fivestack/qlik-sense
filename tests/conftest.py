from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT.absolute()))

from qlik_sense import services, SSLClient, NTLMClient
from qlik_sense.models import app, stream, user
from qlik_sense.services import util
from qlik_sense.clients.base import Client
