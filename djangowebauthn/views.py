from django.shortcuts import render
from secrets import token_urlsafe
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import webauthn
from termprojectwebauthn.settings import DEBUG
from .helpers import token_urlsafe_without_stripping
from .models import WebAuthnProfile, User
import json
import traceback

# Create your views here.

@csrf_exempt
def register_webauthn_user(request):
    username = request.POST["username"]
    user_display_name = request.POST["user_display_name"]
    current_site_details = get_current_site(request)
    webauthn_challenge = token_urlsafe_without_stripping(32)
    webauthn_ukey = token_urlsafe_without_stripping(20)
    request.session["challenge"] = webauthn_challenge.rstrip('=')  # For byte comparison,strip= before saving in session
    request.session["webauthn_ukey"] = webauthn_ukey
    request.session["username"] = username
    request.session["user_display_name"] = user_display_name
    return JsonResponse(webauthn.WebAuthnMakeCredentialOptions(
        challenge=webauthn_challenge,
        rp_name=current_site_details.name.split(":")[0],
        rp_id=current_site_details.domain.split(":")[0],
        user_id=webauthn_ukey,
        username=username,
        display_name=user_display_name,
        icon_url="https://rajeevkr.me/assets/img/portfolio/IMG_20180302_232843.jpg",
        # attestation='indirect'
    ).registration_dict
                        )


@csrf_exempt
def verify_register_webauthn_user(request):
    current_site_details = get_current_site(request)
    webauthn_ukey = request.session["webauthn_ukey"]
    registration_response = json.loads(request.POST["signedCredentials"])
    webauthn_challenge = request.session["challenge"]
    origin = request.build_absolute_uri('/').strip("/")
    if DEBUG:  # For angular dev server frontend - need to remove this later
        origin = origin.replace("8000", "4200").replace("http", "https")
    webauthn_verify_challege = webauthn.WebAuthnRegistrationResponse(
        rp_id=current_site_details.domain.split(":")[0],
        origin=origin,
        registration_response=registration_response,
        challenge=webauthn_challenge,
        self_attestation_permitted=True,
        none_attestation_permitted=True,
        uv_required=False
    )
    try:
        verified_webauthn_credentials = webauthn_verify_challege.verify()
    except Exception as e:
        return JsonResponse({
            "error": f"Registration failed due to {e}"
        }, status=400)
    django_user = User()
    username = request.session["username"]
    user_display_name = request.session["user_display_name"]
    django_user.username = username
    django_user.save()
    newwebauthnprofile = WebAuthnProfile()
    newwebauthnprofile.user = django_user
    newwebauthnprofile.credential_id = str(verified_webauthn_credentials.credential_id, 'utf-8')
    newwebauthnprofile.user_public_key = str(verified_webauthn_credentials.public_key, 'utf-8')
    newwebauthnprofile.display_name = user_display_name
    newwebauthnprofile.webauthn_ukey = webauthn_ukey
    newwebauthnprofile.save()
    return JsonResponse(newwebauthnprofile.hackyDict())

@csrf_exempt
def login_webauthn_user_begin_assertion(request):
    current_site_details = get_current_site(request)
    username = request.POST["username"]
    webauthn_user = WebAuthnProfile.objects.filter(user__username=username).first()
    if webauthn_user is None:
        return JsonResponse({"error": "User doesn't exist"})
    assertion_challenge = token_urlsafe_without_stripping(32)
    request.session["challenge"] = assertion_challenge.rstrip('=')
    generated_webauthn_user = webauthn.WebAuthnUser(
        user_id=webauthn_user.webauthn_ukey,
        username=webauthn_user.user.username,
        display_name=webauthn_user.display_name,
        credential_id=webauthn_user.credential_id,
        icon_url="https://rajeevkr.me/assets/img/portfolio/IMG_20180302_232843.jpg",
        public_key=webauthn_user.user_public_key,
        sign_count=webauthn_user.signature_counter,
        rp_id=current_site_details.domain.split(":")[0]
    )
    generated_webauthn_user_assertion = webauthn.WebAuthnAssertionOptions(generated_webauthn_user, assertion_challenge)
    return JsonResponse(generated_webauthn_user_assertion.assertion_dict)


@csrf_exempt
def login_webauthn_user_assertion_verify(request):
    current_site_details = get_current_site(request)
    assertion_challenge = request.session["challenge"]
    assertion_client_response = json.loads(request.POST["signedAssertionCredentials"])
    webauthn_user = WebAuthnProfile.objects.filter(credential_id=assertion_client_response["id"]).first()
    origin = request.build_absolute_uri('/').strip("/")
    if DEBUG:  # For angular dev server frontend - need to remove this later
        origin = origin.replace("8000", "4200").replace("http", "https")
    if webauthn_user is None:
        return JsonResponse({"error" : "Invalid User"})
    generated_webauthn_user = webauthn.WebAuthnUser(
        user_id=webauthn_user.webauthn_ukey,
        username=webauthn_user.user.username,
        display_name=webauthn_user.display_name,
        icon_url="https://rajeevkr.me/assets/img/portfolio/IMG_20180302_232843.jpg",
        credential_id=webauthn_user.credential_id,
        public_key=webauthn_user.user_public_key,
        sign_count=webauthn_user.signature_counter,
        rp_id=current_site_details.domain.split(":")[0]
    )
    generated_webauthn_user_assertion_response = webauthn.WebAuthnAssertionResponse(
        webauthn_user=generated_webauthn_user,
        assertion_response=assertion_client_response,
        challenge=assertion_challenge,
        origin=origin,
        uv_required=False
    )
    try:
        signature_counter = generated_webauthn_user_assertion_response.verify()
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error" : f"Login assertion failed due to {e}"}, status=400)
    webauthn_user.signature_counter = signature_counter
    webauthn_user.save()
    return JsonResponse(webauthn_user.hackyDict())



