from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy   #позволяет получить URL по параметру "name" в path()
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login') #login — параметр 'name' в path()
    template_name = 'signup.html'

