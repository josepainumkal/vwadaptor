import os
from marshmallow import Schema, fields, pprint

from flask import current_app as app
from flask import url_for

class ResourceUrl(fields.Field):
    def _serialize(self, value, attr, obj):
        if value is None:
            return ''
        return value.title()

class ModelProgressSchema(Schema):
    id = fields.Integer()
    event_name = fields.String()
    event_description = fields.String()
    progress_value = fields.Float()
    modelrun_id = fields.Integer()
    created_at = fields.DateTime()


class ModelResourceSchema(Schema):
    id = fields.Integer()
    resource_type = fields.String()
    resource_size = fields.Integer()
    #resource_name = fields.String()
    modelrun_id = fields.Integer()
    resource_name = fields.Function(lambda obj: os.path.basename(obj.resource_location))
    resource_url = fields.Function(lambda obj: 
        url_for('modelresource.download_resource_by_name',name=os.path.basename(obj.resource_location),_external=True))
    created_at = fields.DateTime()
    #def make_object(self, data):
    #    return ModelResource(**data)

class ModelRunSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    model_name = fields.String()
    created_at = fields.DateTime()
    resources = fields.Nested(ModelResourceSchema,many=True)
    progress_events = fields.Nested(ModelProgressSchema,many=True)
    progress_state = fields.String()
    progress_value = fields.Float()
    user_id = fields.Integer()


class UserSchema(Schema):
    id = fields.Integer()
    username = fields.String()
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    created_at = fields.DateTime()
    modelruns = fields.Nested(ModelRunSchema,many=True)
