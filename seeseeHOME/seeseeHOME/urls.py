from django.conf.urls import patterns, include, url
from django.contrib import admin
from seeseeHOME.views import Home

from django.contrib.auth.decorators import login_required
admin.autodiscover()

from users.views import Login
from users.views import Logout
from users.views import AccountView
from users.views import SignUp

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'seeseeHOME.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', Home.as_view(), name="home"),
    url(r'^login/', Login.as_view(), name="login"),
    url(r'^logout/', Logout.as_view(), name="logout"),
    url(r'^account/', login_required(AccountView.as_view()), name="account"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('users.urls',namespace='users')),
    url(r'^signup/', SignUp.as_view(), name="signup"),
)
