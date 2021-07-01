from django import forms

class Data(forms.Form ):
    select = forms.IntegerField
    question = forms.CharField
    recommend = forms.CharField
    ability = forms.BooleanField