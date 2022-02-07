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
		fields = ['name' , 'email' , 'birthday' , 'hobby', 'job', 'self_introduction']
		widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.TextInput(attrs={'class': 'form-control'}),
            'hobby': forms.TextInput(attrs={'class': 'form-control'}),
			'job': forms.TextInput(attrs={'class': 'form-control'}),
			'self_introduction': forms.TextInput(attrs={'class': 'form-control'}),
    	}
	def __init__(self,*args,**kwargs):
		print("init of form")
		super(CreateUserInfoForm,self).__init__(*args,**kwargs)
		print("initial create form")
		instance = getattr(self, 'instance', None)
		print("instance : ",instance)
		if instance and instance.pk:
			self.fields['name'].widget.attrs['readonly'] = True
			self.fields['email'].widget.attrs['readonly'] = True

class CreateNovelForm(ModelForm):
	class Meta:
		model = Novel
		fields = ['title' , 'description' , 'thumbnail' , 'tags' , 'status']
		widgets = {
			'title' : forms.TextInput(attrs={'class':'form-control'}),
			'description' : forms.TextInput(attrs={'class':'form-control'}),
			'tags' : forms.TextInput(attrs={'class':'form-control'}),
		}

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
