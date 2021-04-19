# import the standard Django Forms
# from built-in library
from django import forms
from django.forms import widgets
import sys
sys.path.append('covid19IndiaAnalysis/covid19/')
import project

class DateInput(forms.DateInput):
    input_type = 'date'

# creating a form
class InputForm(forms.Form):
    typeChoices = (
        ('Cumulative', 'Cumulative'),
        ('Daily ', 'Daily'),
        ('7-dayMV ','7-day Moving Average')
    )
    categoryChoices = (
        ('Confirmed','Confirmed'),
        ('Recovered','Recovered'),
        ('Deceased','Deceased'),
        ('Active', 'Active'),
        ('Tested','Tested'),
        ('Vaccinations', 'Vaccinations'),
        ('Positivity Pct', 'Positivity %'),
        ('TestingPerMillion', 'Number of Tests Per Million')
    )
    arrStates = project.get_state_select();
    arrStates[:, [0, 1]] = arrStates[:, [1, 0]]
    chartChoices = (
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart')
    )
    #first_name = forms.CharField(max_length=200)
    #last_name = forms.CharField(max_length=200)
    #roll_number = forms.IntegerField(
    #    help_text="Enter 6 digit roll number"
    #)
    #password = forms.CharField(widget=forms.PasswordInput())
    state = forms.ChoiceField(choices=arrStates)
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())
    categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                    choices=categoryChoices)
    type = forms.ChoiceField(widget=forms.RadioSelect,
                                    choices=typeChoices)
    typeOfChart = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=chartChoices)

class StateCompForm(forms.Form):
        typeChoices = (
            ('Cumulative', 'Cumulative'),
            ('Daily ', 'Daily'),
            ('7-dayMV ', '7-day Moving Average')
        )
        categoryChoices = (
            ('Confirmed', 'Confirmed'),
            ('Recovered', 'Recovered'),
            ('Deceased', 'Deceased'),
            ('Active', 'Active'),
            ('Tested', 'Tested'),
            ('Vaccinations', 'Vaccinations'),
            ('Positivity Pct', 'Positivity %'),
            ('TestingPerMillion', 'Number of Tests Per Million')
        )
        arrStates = project.get_state_select();
        arrStates[:, [0, 1]] = arrStates[:, [1, 0]]
        chartChoices = (
            ('line', 'Line Chart'),
            ('bar', 'Bar Chart')
        )
        # first_name = forms.CharField(max_length=200)
        # last_name = forms.CharField(max_length=200)
        # roll_number = forms.IntegerField(
        #    help_text="Enter 6 digit roll number"
        # )
        # password = forms.CharField(widget=forms.PasswordInput())
        state1 = forms.ChoiceField(choices=arrStates)
        state2 = forms.ChoiceField(choices=arrStates)
        start_date = forms.DateField(widget=DateInput())
        end_date = forms.DateField(widget=DateInput())
        category = forms.ChoiceField(choices=categoryChoices)
        type = forms.ChoiceField(widget=forms.RadioSelect,
                                 choices=typeChoices)
        typeOfChart = forms.ChoiceField(widget=forms.RadioSelect,
                                        choices=chartChoices)



    # Logic for raising error if end_date < start_date
def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        print(start_date, end_date)
        if (start_date is not None) & (end_date is not None):
            if end_date < start_date:
                raise forms.ValidationError("End date should be greater than start date.")


class Top10StatesForm(forms.Form):
    typeChoices = (
        ('Cumulative', 'Cumulative'),
        ('Daily ', 'Daily'),
        ('7-dayMV ', '7-day Moving Average')
    )
    categoryChoices = (
        ('Confirmed', 'Confirmed'),
        ('Recovered', 'Recovered'),
        ('Deceased', 'Deceased'),
        ('Active', 'Active'),
        ('Tested', 'Tested'),
        ('Vaccinations', 'Vaccinations'),
        ('Positivity Pct', 'Positivity %'),
        ('TestingPerMillion', 'Number of Tests Per Million')
    )

    # first_name = forms.CharField(max_length=200)
    # last_name = forms.CharField(max_length=200)
    # roll_number = forms.IntegerField(
    #    help_text="Enter 6 digit roll number"
    # )
    # password = forms.CharField(widget=forms.PasswordInput())
    as_of_date = forms.DateField(widget=DateInput())
    category = forms.ChoiceField(choices=categoryChoices)
    type = forms.ChoiceField(widget=forms.RadioSelect,
                             choices=typeChoices)
