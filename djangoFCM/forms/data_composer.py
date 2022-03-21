from django import forms
from django.db import models


class DynamicChoiceField(forms.ChoiceField):

    def valid_value(self, value):
        return True


class DataComposerForm(forms.Form):
    model = None
    max_recursion_level = 2
    group_state = forms.ChoiceField(choices=(('OR', 'OR'), ('AND', 'AND')))
    attribute = forms.ChoiceField(
        required=True
    )
    operator = forms.ChoiceField(
        required=True
    )
    value = forms.CharField(
        required=False,
    )
    value_select = DynamicChoiceField(
        choices=(),
        required=False,
    )

    value_select.widget.attrs.update({'class': '--hidden'})

    def get_attributes_as_choices(self):

        def get_model_fields(_model: models.Model, _recursion_level: int = 0, _previous_lookup: str = ''):
            if not _previous_lookup:
                _previous_lookup = _model.__name__
            _recursion_level = _recursion_level + 1
            result = []

            model_fields = _model._meta._get_fields()

            for _field in model_fields:
                _lookup = f'{_previous_lookup}.{_field.name}'

                if isinstance(_field, models.ForeignKey):
                    result.append(_lookup)

                    if _recursion_level <= self.max_recursion_level:
                        result.extend(get_model_fields(_field.related_model, _recursion_level, _lookup))
                elif isinstance(_field, models.ForeignObjectRel):
                    continue
                else:
                    result.append(_lookup)

            return result

        fields = get_model_fields(self.model)

        return tuple((field.replace('.', '__')[len(self.model.__name__) + 2:], field) for field in fields)

    @staticmethod
    def get_operators_as_choices():
        return ('is', 'is'),

    def clean(self):
        data = super(DataComposerForm, self).clean()
        value_select_value = data.pop('value_select', None)
        if value_select_value:
            data['value'] = value_select_value

        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attribute'].choices = self.get_attributes_as_choices()
        self.fields['operator'].choices = self.get_operators_as_choices()
