from django import forms

class SearchForm(forms.Form):
    your_name = forms.CharField(label='Test field', max_length=100)