from marshmallow.schema import Schema
from marshmallow.utils import EXCLUDE


class BaseValidator(Schema):
    class Meta:
        unknown = EXCLUDE
