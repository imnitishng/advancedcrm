from django import forms

from .models import User

class UserListForm(forms.Form):
    selection = forms.BooleanField(required=True)

class UserListModelForm(forms.ModelForm):
    selection = forms.BooleanField(required=True)
    class Meta:
        model = User
        fields = ['name', 'email_address']