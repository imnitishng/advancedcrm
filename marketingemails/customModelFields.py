from django.db import models


class CommaSepField(models.Field):
    'Implements comma-separated storage of lists'

    def __init__(self, seperator=',', *args, **kwargs):
        self.separator = seperator
        kwargs['max_length'] = 10000
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.separator != ",":
            kwargs['separator'] = self.separator
        del kwargs["max_length"]
        return name, path, args, kwargs

    def db_type(self, connection):
        return 'CommaSeparatedListField'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        if not isinstance(value, str):
            return [str(value)]
        else:
            if value and value[0] == '[':
                return value
            else:
                return value.split(self.separator)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if value is None:
            return value
        return list(value.split(self.separator))

    def get_prep_value(self, value):
        if not value:
            return value   
        listToSave = []
        for s in value:
            if len(s):
                listToSave.append(s)            
        return self.separator.join(listToSave)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


def parse_hashmap(input):
    campaign_ids = input.split(' ')[::2]
    counts = input.split(' ')[1::2]
    hash_map = {}
    for i in range(min(len(campaign_ids), len(counts))):
        hash_map[campaign_ids[i]] = int(counts[i])
    return hash_map

class HashmapField(models.Field):
    'Implement a python dictionary'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 20000
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return  name, path, args, kwargs

    def db_type(self, connection):
        return 'DictionaryField'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return parse_hashmap(value)

    def to_python(self, value):
        if isinstance(value, dict):
            return value
        return parse_hashmap(value)

    def get_prep_value(self, value):
        if not value:
            return ''
        listToSave = []
        for k, v in value.items():
            listToSave.append(f'{k} {v}')
        return ' '.join(listToSave)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)