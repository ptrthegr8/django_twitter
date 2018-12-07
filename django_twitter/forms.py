from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())


class SignupForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())


class TweetForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(TweetForm, self).__init__(*args, **kwargs)
        self.fields['user'].choices = [(user.id, user.username)]
    user = forms.ChoiceField(widget=forms.Select)
    text = forms.CharField(widget=forms.Textarea)

