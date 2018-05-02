from django import forms


class SearchForm(forms.Form):

    # Elements inside SERVICES correspond to (option_value, option_text)
    SERVICES_CHOICES = (('', ''), ('DRUGS', 'Drug Support'), ('FOOD', 'Food'), ('HEALTH', 'Health Care'), ('SHOWER', 'Showers'))
    # TODO replace option_value for LOCATION_CHOICES with google api location strings
    LOCATION_CHOICES = (('', ''), ('SANTACRUZ', 'Santa Cruz'), ('WATSONVILLE', 'Watsonville'), ('SCOTTSVALLEY', 'Scotts Valley'),
                        ('FELTON', 'Felton'), ('BOULDERCREEK', 'Boulder Creek'), ('DAVENPORT', 'Davenport'))

    services = forms.ChoiceField(label='I need', widget=forms.Select, choices=SERVICES_CHOICES, required=False)
    locations = forms.ChoiceField(label='near', widget=forms.Select, choices=LOCATION_CHOICES, required=False)
