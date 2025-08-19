# -----------------------------------------------------------
# File: myapp/views.py
#
# Note: You should replace 'myapp' with the name of your app.
# -----------------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate

def signup_view(request):
    """
    Handles user registration. If the request method is POST, it attempts
    to save the new user. If successful, it logs the user in and redirects
    to the login page.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # You can log the user in automatically after signup if you want
            # login(request, user)
            return redirect('login') # Redirect to the login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    """
    Handles user authentication. If the request method is POST, it attempts
    to authenticate the user. If successful, it logs the user in and
    redirects them to the next page.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Get the username and password from the form
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home/') # You should change this to your desired post-login URL
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})