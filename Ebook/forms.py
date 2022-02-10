from django.db.models import fields
from django.forms import CheckboxSelectMultiple, ModelForm, widgets
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.utils.html import mark_safe
from sympy import ExactQuotientFailed

from .models import *

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'password1', 'password2']
		widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            # 'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            # 'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
    	}
	def __init__(self,*args,**kwargs):
		super(CreateUserForm, self).__init__(*args, **kwargs)
		self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
		self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})	

class CreateUserInfoForm(ModelForm):
	class Meta:
		model = UserInfo
		fields = ['name' , 'email' , 'avatar', 'birthday' , 'hobby', 'job', 'self_introduction']
		widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control'}),
            'hobby': forms.TextInput(attrs={'class': 'form-control'}),
			'job': forms.TextInput(attrs={'class': 'form-control'}),
			'self_introduction': forms.TextInput(),
    	}
	# birthday = forms.DateField(input_formats='%d-%m-%Y',widget=forms.DateInput(attrs={'class': 'form-control'},format='%d-%m-%Y'))
	def __init__(self,*args,**kwargs):
		print("init of form")
		super(CreateUserInfoForm,self).__init__(*args,**kwargs)
		print("initial create form")
		# try:
		instance = getattr(self, 'instance', None)
		# except:
			# instance = None
		# print(instance)
		if instance and instance.pk:
			self.fields['email'].widget.attrs['readonly'] = True

class CreateNovelForm(ModelForm):
	class Meta:
		model = Novel
		fields = ['title' , 'description' , 'thumbnail' , 'tags' , 'status']
		widgets = {
			'title' : forms.TextInput(attrs={'class':'form-control'}),
			'description' : forms.TextInput(),
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

# class CreateChangePassForm(forms.Form):
# 	oldpassword = forms.CharField(widget=forms.PasswordInput)
# 	newpassword= forms.CharField(widget=forms.PasswordInput)
# 	newpassword_confirmation= forms.CharField(widget=forms.PasswordInput)
