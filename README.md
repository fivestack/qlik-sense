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
- urllib3
- uuid
- marshmallow

# Installation

This package is hosted on PyPI:

```shell script
pip install qlik_sense
```

# Examples

Use this library to reload a Qlik Sense app:
```python

from qlik_sense import Client

user = {
    'directory': 'DIRECTORY',
    'username': 'USERNAME',
    'password': 'PASSWORD'
}
qs = Client(schema='https', host='local_host', port=80, user=user)
app = qs.app.get_by_name_and_stream(app_name='My App', stream_name='My Stream')
qs.app.reload(app)
```

# Acknowledgements

This package was inspired by Rafael Sanz's work:

https://github.com/rafael-sanz/qsAPI/blob/master/qsAPI.py

I would like to acknowledge the work he spent to figure out all of the logistics of Qlik Sense's APIs.
I used modified versions of his Controller (Client) and QRS/QPS (___Service) classes in this library.

# Full Documentation

For the full documentation, please visit: https://qlik_sense.readthedocs.io/en/latest/