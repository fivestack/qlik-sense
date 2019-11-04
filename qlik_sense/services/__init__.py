from .app import AppService
from .stream import StreamService
from .user import UserService

"""
Unsupported Methods:

    - qrs/app/content: GET
    - qrs/app/content/count: GET
    - qrs/app/content/full: GET
    - qrs/app/content/table: POST
    - qrs/app/content/{app.id}: GET
    - qrs/app/content/{app.id}/fileextensionwhitelist: GET

    - qrs/app/datasegment: GET
    - qrs/app/datasegment/count: GET
    - qrs/app/datasegment/full: GET
    - qrs/app/datasegment/previewprivileges: POST
    - qrs/app/datasegment/table: POST
    - qrs/app/datasegment/{app.id}: GET

    - qrs/app/hublist: GET
    - qrs/app/hublist/full: GET

    - qrs/app/internal: GET
    - qrs/app/internal/count: GET
    - qrs/app/internal/full: GET
    - qrs/app/internal/previewprivileges: POST
    - qrs/app/internal/table: POST
    - qrs/app/internal/{app.id}: GET

    - qrs/app/object: GET
    - qrs/app/object/count: GET
    - qrs/app/object/full: GET
    - qrs/app/object/previewprivileges: POST
    - qrs/app/object/table: POST
    - qrs/app/object/{app.id}: GET, PUT, DELETE
    - qrs/app/object/{app.id}/approve: POST
    - qrs/app/object/{app.id}/publish: PUT
    - qrs/app/object/{app.id}/unapprove: POST
    - qrs/app/object/{app.id}/unpublish: PUT
"""