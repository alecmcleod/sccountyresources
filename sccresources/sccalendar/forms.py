from django import forms


class SearchForm(forms.Form):

    # Elements inside SERVICES correspond to (option_value, option_text)
    SERVICES_CHOICES = (('', ''), ('DRUGS', 'Drug Support'), ('FOOD', 'Food'), ('HEALTH', 'Health Care'), ('SHOWER', 'Showers'))
    # TODO replace option_value for LOCATION_CHOICES with google api location strings
    LOCATION_CHOICES = (('', ''), ('Santa Cruz, CA', 'Santa Cruz'), ('Watsonville, CA', 'Watsonville'), ('Scotts Valley, CA', 'Scotts Valley'),
                        ('Felton, CA', 'Felton'), ('Boulder Creek, CA', 'Boulder Creek'), ('Davenport, CA', 'Davenport'))

    services = forms.ChoiceField(label='I need', choices=SERVICES_CHOICES, required=False, label_suffix="", widget=forms.Select(attrs={'id': 'services'}))
    locations = forms.ChoiceField(label='near', choices=LOCATION_CHOICES, required=False, label_suffix="", widget=forms.Select(attrs={'id':'locations'}))
