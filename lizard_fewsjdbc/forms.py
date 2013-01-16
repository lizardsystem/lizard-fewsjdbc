# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from decimal import Decimal

from django import forms

from lizard_fewsjdbc.models import Threshold
from lizard_map.models import WorkspaceEditItem
from lizard_map.adapter import adapter_layer_arguments


class ThresholdUpdateForm(forms.Form):
    """Form for handling updates for threshold instances."""
    id = forms.CharField(max_length=50)
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
            self.cleaned_data['value'] = Decimal(value)
        return self.cleaned_data


class ThresholdCreateForm(forms.ModelForm):

    workspace_item_id = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = Threshold
        fields = ('name', 'value', 'location_id')
        widgets = {
            'location_id': forms.HiddenInput,
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
