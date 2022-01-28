from django.db.models import fields
from django.forms import CheckboxSelectMultiple, ModelForm, widgets
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.utils.html import mark_safe

from .models import *

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'password1', 'password2']

class CreateUserInfoForm(ModelForm):
	class Meta:
		model = UserInfo
		fields = ['name' , 'email' , 'phone' , 'address']
		widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
    	}

class CreateNovelForm(ModelForm):
	class Meta:
		model = Novel
		fields = ['title' , 'description' , 'thumbnail' , 'tags' , 'status']
		widgets = {
			'title' : forms.TextInput(attrs={'class':'form-control'}),
			'description' : forms.TextInput(attrs={'class':'form-control'}),
			'tags' : forms.TextInput(attrs={'class':'form-control'}),
		}

		def __init__(self, *args, **kwargs):
			super(CreateNovelForm, self).__init__(*args, **kwargs)
			self.fields["tags"].widget = forms.CheckboxSelectMultiple()
			self.fields["tags"].queryset = Tag.objects.all()

	tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        # choices=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
        # widget=forms.CheckboxInput(attrs={'class': 'checkbox-inline'}),
    )

class CreateChapterForm(ModelForm):
	class Meta:
		model = Chapter
		fields = ['title' , 'number' , 'content']
		widgets = {
			'title' : forms.TextInput(attrs={'class':'form-control'}),
			'number' : forms.NumberInput(attrs={'class':'form-control'}),
			'content' : forms.TextInput(attrs={'class':'form-control'}),
		}

class CreateRatingForm(ModelForm):
	class Meta:
		model = Rating
		fields = ['rate']

class CreateChangePassForm(forms.Form):
	oldPassword = forms.CharField(widget=forms.PasswordInput)
	newPassword1= forms.CharField(widget=forms.PasswordInput)
	newPassword2= forms.CharField(widget=forms.PasswordInput)
