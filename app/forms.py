from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# for using django admin datetime picker in forms
from django.contrib.admin import widgets
from .models import Product, Auction

from django.utils import timezone
class RegisterUserForm(UserCreationForm):
    def __init__(self, *args, **kargs):
        super(RegisterUserForm, self).__init__(*args, **kargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        del self.fields['password1']
        del self.fields['password2']

    email = forms.EmailField(required=True, label='', widget=forms.EmailInput(
        attrs={'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ('email',)


class ProductForm(forms.ModelForm):
    
    
	# def __init__(self, *args, **kwargs):
	# 	super(ProductForm, self).__init__(*args, **kwargs)
	# 	self.fields['trans_date'].initial = 
    class Meta:
        model = Product
        fields = '__all__'
        exclude = ('created_by',)
        widgets = {
            'auc_end_time': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class':'datetimefield', 'type': 'datetime-local', 'min': timezone.now().date()})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auc_end_time'].input_formats = ('%Y-%m-%dT%H:%M',) 

    def clean_datetime_field(self):
        data = self.cleaned_data['auc_end_time']
       
        # Format datetime as required for datetime-local
        return data.strftime('%Y-%m-%dT%H:%M')


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['amount']
