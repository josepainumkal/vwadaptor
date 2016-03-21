import importlib
class ModelRunner(object):
    def __init__(self,schemas,model_name):
        self.model_name = model_name
        #schemas = load_schemas()
        self.schema = schemas[model_name]

    def get_schema(self):
        return self.schema

    def get_resource_info(self,type='inputs'):
        return self.schema['resources'][type]

    def get_resource_names(self,type='inputs'):
        return self.schema['resources'][type].keys()

    def get_resource_to_caller_map(self,type='inputs'):
        resources = self.schema['resources'][type]
        resource_map = {}
        for r in resources:
            resource_map[r] = resources[r]['mapsTo']
        return resource_map

    def get_resource_map(self,type='inputs'):
        return self.schema['resources'][type]
    def get_resource_type_from_map(self,maps_to,type='inputs'):
        res = self.schema['resources'][type]
        for i in res:
            if res[i]['mapsTo']==maps_to:
                return i

    def get_execution_target(self):
        execution = self.schema['execution']['target']
        return execution['module'],execution['method']

    def get_model_runner(self):
        module_name, method = self.get_execution_target()
        module = importlib.import_module(module_name)
        return module,getattr(module, method)
