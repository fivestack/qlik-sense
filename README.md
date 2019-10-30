# Qlik Sense

**This library provides tools to interact with Qlik Sense's APIs natively in python.**

---

# Overview

This library allows users to work with Qlik Sense applications in a larger python workflow more easily. While Qlik's
API could be used directly, this streamlines the process.

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

from qlik_sense.example_app import api

qs = api.QlikSense(host='HOST_NAME', certificate='CERT_FILE_PATH')

app = qs.get_app_by_name_and_stream(app_name='Rate Monitor', stream_name='Actuarial')
qs.reload_app(app)
```

# Acknowledgements

This package was inspired by Rafael Sanz's work:

https://github.com/rafael-sanz/qsAPI/blob/master/qsAPI.py

I would like to acknowledge the work he spent to figure out all of the logistics of Qlik Sense's APIs.
I redeployed a modified version of his Controller and QRS (Sessions here) classes in the ORM for this library
and built functionality around them.

# Full Documentation

For the full documentation, please visit: https://qlik_sense.readthedocs.io/en/latest/