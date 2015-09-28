from voluptuous import Schema, Required, All, Length, Range, Url

modelresource_form_schema = Schema({
  Required('url'): All(unicode,Url()),
  Required('filename'):unicode,
  Required('resource_type'):unicode
})