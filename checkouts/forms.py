from django import forms

class OrderDateFilterForm(forms.Form):
    filter_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
