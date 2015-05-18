# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from decimal import Decimal
import logging
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from lizard_fewsjdbc.models import Threshold
from lizard_map.models import WorkspaceEditItem
from lizard_map.adapter import adapter_layer_arguments

logger = logging.getLogger(__name__)


class ThresholdUpdateForm(forms.Form):
    """Form for handling updates for threshold instances."""
    # id is something like threshold-1-value (<model>-<id>-<field_name>)
    id = forms.CharField(max_length=50)
    # value can be value for name, value, color
    value = forms.CharField(max_length=50)

    def clean_id(self):
        """Split incoming id in its 3 parts

        Ids should come in as e.g. threshold-1-value, where 1 is the Threshold
        instance id and value is the field name that is updated.

        """
        id = self.cleaned_data.get('id')
        parts = id.split('-')
        self.cleaned_data['threshold_id'] = int(parts[1])
        field_name = parts[2]
        self.cleaned_data['field_name'] = field_name
        return id  # return unchanged

    def clean(self):
        value = self.cleaned_data.get('value')
        if self.cleaned_data['field_name'] == 'value':
            # cast threshold value to Decimal
            value = value.replace(",", ".")  # use . as decimal separator
            self.cleaned_data['value'] = Decimal(value)
        elif self.cleaned_data['field_name'] == 'color':
            value = value.strip('#')  # strip #
            pattern = re.compile(r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
            result = pattern.match(value)
            if not result:
                logger.error(_("Color must be in hexadecimal"
                               "format, e.g. FF05A9, got %s") % value)
                # return the default color
                self.cleaned_data['value'] = '000000'
            else:
                self.cleaned_data['value'] = value.upper()
        return self.cleaned_data


class ThresholdCreateForm(forms.ModelForm):

    workspace_item_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(ThresholdCreateForm, self).__init__(*args, **kwargs)
        # add parsleyjs attributes for client side validation
        parsley_attrs = {'data-required': 'true', 'data-notblank': 'true'}
        name_attrs = {}
        name_attrs.update(parsley_attrs)
        self.fields['name'].widget.attrs = name_attrs
        value_attrs = {}
        value_attrs.update(parsley_attrs)
        value_attrs.update({'data-parsley-type': 'number'})
        self.fields['value'].widget.attrs = value_attrs
        color_attrs = {}
        color_attrs.update(parsley_attrs)
        color_attrs.update({'data-regexp': '[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3}'})
        self.fields['color'].widget.attrs = color_attrs

    class Meta:
        model = Threshold
        fields = ('name', 'value', 'color', 'location_id')
        widgets = {
            'location_id': forms.HiddenInput,
            'value': forms.TextInput,  # Otherwise parsley js requires an int...
        }

    def save(self, commit=True):
        workspace_item = WorkspaceEditItem.objects.get(
            pk=self.cleaned_data['workspace_item_id'])
        layer_arguments = adapter_layer_arguments(
            workspace_item.adapter_layer_json)
        parameter_id = layer_arguments['parameter']
        filter_id = layer_arguments['filter']
        instance = super(ThresholdCreateForm, self).save(commit=False)
        instance.filter_id = filter_id
        instance.parameter_id = parameter_id
        if commit:
            instance.save()
        return instance
