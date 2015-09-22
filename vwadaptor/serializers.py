from marshmallow import Schema, fields, pprint

class ModelResourceSchema(Schema):
    id = fields.Integer()
    resource_type = fields.String()
    resource_size = fields.Integer()
    resource_name = fields.String()
    modelrun_id = fields.Integer()
    
    #def make_object(self, data):
    #    return ModelResource(**data)

class ModelRunSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    model_name = fields.String()
    created_at = fields.DateTime()
    resources = fields.Nested(ModelResourceSchema,many=True)
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
