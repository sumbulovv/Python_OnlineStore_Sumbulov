from django.contrib.auth import login
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.shortcuts import redirect
from django.views.generic import CreateView

from users.forms import CustomAuthenticationForm, CustomUserCreationForm


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginView(AuthLoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    

class LogoutView(AuthLogoutView):
    pass