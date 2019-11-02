from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent

sys.path.insert(0, str(PROJECT_ROOT.absolute()))

from qlik_sense import services
from qlik_sense.models import app, stream, user
from qlik_sense.services import util

import logging

from qlik_sense import Client

fake_client = Client(
    scheme='http',
    host='local_host',
    port=80,
    log_name='qlik_sense_client_test',
    verbosity=logging.DEBUG
)