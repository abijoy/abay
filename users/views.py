from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse 
from django.contrib.auth import login
from .forms import CustomUserCreationForm

# Create your views here.
def dashboard(request):
    return render(request, 'users/dashboard.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        return render(request, 'users/register.html', {'form': form})
    form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})