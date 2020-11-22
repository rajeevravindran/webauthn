from django.urls import path

from . import views

urlpatterns = [
    path('register_webauthn_user', views.register_webauthn_user, name='register_webauthn_user'),
    path('verify_register_webauthn_user', views.verify_register_webauthn_user, name='verify_register_webauthn_user'),
    path('login_webauthn_user_begin_assertion',
         views.login_webauthn_user_begin_assertion, name='login_webauthn_user_begin_assertion'),
    path('login_webauthn_user_assertion_verify',
         views.login_webauthn_user_assertion_verify, name='login_webauthn_user_assertion_verify'),
]