from django import forms

class ProductFilterForm(forms.Form):
    category = forms.CharField(required=False)
    size = forms.CharField(required=False)
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)