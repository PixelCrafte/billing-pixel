from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View

class HomeView(View):
    def get(self, request):
        return render(request, "billingapp/home.html")

class LoginView(View):
    def get(self, request):
        return render(request, "billingapp/login.html")