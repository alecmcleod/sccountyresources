
from django import forms
from phonenumber_field.formfields import PhoneNumberField


class SearchForm(forms.Form):

    # Elements inside SERVICES correspond to (option_value, option_text)
    SERVICES_CHOICES = (('', ''),
                        ('DRUGS', 'Drug Support'),
                        ('FOOD', 'Food'),
                        ('HEALTH', 'Health Care'),
                        ('SHOWER', 'Showers'))
    # TODO replace option_value for LOCATION_CHOICES with google api location
    # strings
    LOCATION_CHOICES = (
        ('', ''),
        ('Santa Cruz, CA', 'Santa Cruz'),
        ('Watsonville, CA', 'Watsonville'),
        ('Scotts Valley, CA', 'Scotts Valley'),
        ('Felton, CA', 'Felton'),
        ('Boulder Creek, CA', 'Boulder Creek'),
        ('Davenport, CA', 'Davenport'))

    services = forms.ChoiceField(
        label='I need',
        choices=SERVICES_CHOICES,
        required=True,
        label_suffix="",
        widget=forms.Select(
            attrs={
                'id': 'services'}))
    locations = forms.ChoiceField(
        label='near',
        choices=LOCATION_CHOICES,
        required=False,
        label_suffix="",
        widget=forms.Select(
            attrs={
                'id': 'locations'}))


class SubscribeForm(forms.Form):

    phone_number = PhoneNumberField(max_length=15, min_length=10,
                                    label='Enter Phone Number', required=True)


class ConfirmForm(forms.Form):

    code = forms.CharField(
        widget=forms.NumberInput,
        max_length=4,
        min_length=4,
        required=True)


class DistanceFilterForm(forms.Form):

    # First part of search filtering, allows user to select distance to filter
    # by
    DISTANCE_CHOICES = ((1, '1 mile'), (3, '3 miles'), (5, '5 miles'),
                        (10, '10 miles'), (100, 'Santa Cruz County'))
    within_distance = forms.ChoiceField(
        label='Within:',
        choices=DISTANCE_CHOICES,
        label_suffix="",
        widget=forms.Select(
            attrs={
                'id': 'within_distance',
                'onchange': 'this.form.submit();'}))
