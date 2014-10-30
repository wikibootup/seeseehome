from django.http import HttpResponseRedirect,request

from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic import DetailView

from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate

from django.contrib import messages

from django.core.urlresolvers import reverse

from users.models import User

from users.forms import LoginForm
from users.forms import SignUpForm

from django.db import IntegrityError, OperationalError
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.core.validators import validate_email

class UsersIndexView(ListView):
    template_name = 'users/index.html'
    model = User

class UserShowView(DetailView):
    template_name = "users/show.html"
    model = User

class Login(FormView):
    template_name = "users/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        def msg_error(msg=""):
            messages.add_message(
                self.request,
                messages.ERROR,
                msg
            )
        
        def msg_success(msg=""):
            messages.add_message(
                self.request,
                messages.SUCCESS,
                msg
            )

        user_email_not_exist = "ERROR : the user email not exist"
        user_login_success = "Successfully Login"
        user_deactivated = "ERROR : Deactivated User"
        user_invalid = "ERROR : invalid email or password" 

        email = self.request.POST["email"]
        password = self.request.POST["password"]

        # User authentication
        try:
            user = authenticate(email=email, password=password)
        except ValidationError:
            msg_error(user_email_not_exist)
            return HttpResponseRedirect(reverse("login"))       
        else:
            next = ""
             
            if self.request.GET:
                next = self.request.GET['next']
                
            if user is not None:
                if user.is_active:
                    login(self.request, user)
                    msg_success(user_login_success)

                    if next == "":
                        return HttpResponseRedirect(reverse("home"))
                    else:
                        return HttpResponseRedirect(next)
                else:
                    msg_error(user_deactivated)
                    return HttpResponseRedirect(reverse("login"))
            else:
                msg_error(user_invalid)
                return HttpResponseRedirect(reverse("login"))
 
class Logout(RedirectView):
    def get_redirect_url(self):
        user_logout_failed = "ERROR : logout failed"
        user_logout_success = "Successfully Logout"

        try:
            logout(self.request)
        except:
            messages.add_message(
                self.request,
                messages.ERROR,
                user_logout_failed
            )
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.add_message(
                self.request,
                messages.SUCCESS,
                user_logout_success
            )
            return reverse("home")

class AccountView(DetailView):
    model = User
    template_name = 'users/account.html'

    context_object_name = "user_account"

    def get_object(self, queryset=None):
        return self.request.user

class SignUp(FormView):
    template_name = "users/signup.html"
    form_class = SignUpForm
    
    def form_valid(self, form):
        def msg_error(msg=""):
            messages.add_message(
                self.request,
                messages.ERROR,
                msg
            )

        def msg_success(msg=""):
            messages.add_message(
                self.request,
                messages.SUCCESS,
                msg
            )

        user_signup_success = "Successfully SignUp"
        user_invalid_email = "ERROR : invalid user email" 
        user_already_exist = "ERROR : The user email already exist"        
        user_invalid_password = "ERROR : invalid user password"

        email = self.request.POST["email"]
        password = self.request.POST["password"]
        
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            msg_error(user_invalid_email)
            return HttpResponseRedirect(reverse("signup"))       

        # Check Uniqueness of User
        try:
            User.objects.get(email=email)
        except ObjectDoesNotExist:
            pass
        else:
            msg_error(user_already_exist)
            return HttpResponseRedirect(reverse("signup"))

        # Validate password
        try:
            User.objects.validate_password(password)
        except ValidationError:
            msg_error(user_invalid_password)
            return HttpResponseRedirect(reverse("signup"))       
       
        # Create new user
        user = User.objects.create_user(email, password = password)
        msg_success(user_signup_success) 

        return HttpResponseRedirect(reverse("login"))
        # for celery, but not used in see homepage
        """
        # send Email, test should be programmed in tasks.py
        tasks.send_mail_to_new_user.delay(user)
        return HttpResponseRedirect(reverse("login"))
        """
