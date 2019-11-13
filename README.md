# Qlik Sense

**This library is a python client for the Qlik Sense APIs**

---

# Overview

This library allows users to more easily work with Qlik Sense applications in a larger python workflow. While Qlik's
APIs could be used directly, this streamlines the process.

#### Disclaimer:

This library, and its maintainer, have no affiliation with QlikTech. Qlik support agreement does not cover
support for this application.

# Requirements

- Python 3.7+
- requests
- requests_ntlm
- requests_negotiate_sspi
- urllib3
- uuid
- marshmallow

# Installation

This package is hosted on PyPI:

```shell script
pip install qlik_sense
```

# Examples

Use this library to work with Qlik Sense apps:
```python

from qlik_sense import NTLMClient

qs = NTLMClient(host='url/to/qlik/sense/server')
app = qs.app.get_by_name_and_stream(app_name='My App', stream_name='My Stream')
qs.app.reload(app=app)
```

# Full Documentation

For the full documentation, please visit: https://qlik_sense.readthedocs.io/en/latest/
