from datetime import datetime

from cassandra.util import uuid_from_time
from marshmallow import fields, validate, post_load

from .validator import BaseValidator


def make_initital_cursor():
    return datetime.utcnow().timestamp()


class CursorPaginatorQuery(BaseValidator):
    cursor = fields.Float(validate=validate.Range(min=0, min_inclusive=False), load_default=make_initital_cursor)
    size = fields.Int(validate=validate.Range(min=10, max=100), load_default=10)

    @post_load
    def make_paginator_params(self, data, **kwargs):
        return {
            "cursor": uuid_from_time(datetime.fromtimestamp(data["cursor"])),
            "size": data["size"],
        }
