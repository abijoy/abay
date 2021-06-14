from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
# for using django admin datetime picker in forms
from django.contrib.admin import widgets
from .models import Product, Auction


class RegisterUserForm(UserCreationForm):
	def __init__(self, *args, **kargs):
	    super(RegisterUserForm, self).__init__(*args, **kargs)
	    self.fields['password1'].required = False
	    self.fields['password2'].required = False
	    del self.fields['password1']
	    del self.fields['password2']

	email = forms.EmailField(required=True, label='', widget=forms.EmailInput(attrs={'placeholder':'Email'}))

	class Meta:
		model = User 
		fields = ('email',)

class ProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = '__all__'
		exclude = ('created_by',)
		widgets = {
			'auc_end_time': forms.DateTimeInput(format='%d/%m/%Y %H:%M', attrs={'type':'datetime-local'})
		}

class AuctionForm(forms.ModelForm):
	class Meta:
		model = Auction
		fields = ['amount']