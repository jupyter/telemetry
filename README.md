# Telemetry

[![circleci](https://circleci.com/gh/jupyter/telemetry?style=shield)](https://circleci.com/gh/jupyter/telemetry)
[![codecov](https://codecov.io/gh/jupyter/telemetry/branch/master/graph/badge.svg)](https://codecov.io/gh/jupyter/telemetry)

Telemetry for Jupyter Applications and extensions.

## Usage

### Use with PyDantic

```python

from pydantic import BaseModel

class MyEvent(BaseModel):

    class Config:
        title = 'My Event'
        schema_extra = {
            '$id': 'my.event',
            'version': 1
        }


```