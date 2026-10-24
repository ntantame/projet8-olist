from django.shortcuts import render
from django.shortcuts import render

def dashboard_view(request):
    return render(request, 'dashboard.html')

def agent_view(request):
    return render(request, 'agent.html')

# Create your views here.
