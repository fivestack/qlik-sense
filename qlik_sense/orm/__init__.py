"""
The ORM layer provides functionality specific to the Qlik Sense APIs. In other words, you should be able to
rip out the ORM and replace it with something else, such as a fake for testing purposes, and the rest of the
application should continue to work. That means that all api calls for the entire application are routed
through this layer.
"""
from .controller import Controller
from .app import AppSession
