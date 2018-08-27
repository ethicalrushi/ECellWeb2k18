from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from .forms import UserForm, UserProfileInfoForm, ContactForm
from django import forms
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.forms.models import model_to_dict
import jwt
import json
import http.client
from sendotp import sendotp
from server.decorators.login import login_req
from server.decorators.decoder import decoder
from decouple import config
from django.conf import settings as conf_settings
from social_django.models import UserSocialAuth
from .models import WebMsg
import multiprocessing
from . import send_mail
from random import randint
import requests

def event_detail(request, event_id):
    return render(request, 'website/event_detail.html')

def homepage(request):
    return render(request, 'website/index.html')

def gallerypage(request):
	return render(request, 'website/gallery.html')

def privacy_policy_page(request):
	return render(request, 'website/privacy_policy.html')

def terms_page(request):
	return render(request, 'website/terms.html')

@csrf_exempt
def message(request):
	post = json.loads(request.body.decode('UTF-8'))
	msg = WebMsg(name=post['name'],email=post['email'],msg=post['msg'])
	print(post)
	msg.save()

	return JsonResponse({'success':True,'message':'Your response has been recorded successfully'})

@csrf_exempt
def applogin(request, *args, **kwargs):
	error_msg = {}
	error_msg['success'] = False

	if request.method=='POST':
		req_data = json.loads(request.body.decode('UTF-8'))
		email = req_data['email']
		password = req_data['password']

		try:
			obj = User.objects.filter(email=email)
			username = obj[0].username
			print(username)
			user = authenticate(username=username, password=password)
			print(user)
		except User.DoesNotExist:
			error_msg['message'] = "Please create an account to continue"
			return JsonResponse(error_msg)
		except Exception as e:
			print(e)
			error_msg['message'] = "Please try again later"
			return JsonResponse(error_msg)
		
		if user:
			user.profile.status=1;
			login(request,user)
			payload = {
				'id' : user.id,
				'email': user.email,
			}

			jwt_token = jwt.encode(payload,conf_settings.SECRET_KEY)
			token = jwt_token.decode('utf-8')
			return JsonResponse({
				'success' : True,
				'message' : 'authentication successfull',
				'first_name' : user.first_name,
				'last_name' : user.last_name,
				'token' : token
			})

		else:
			print("Invalid credentials")
			error_msg['message'] = "Invalid Credentials"
			return JsonResponse(error_msg)
	return render(request,'login.html')

@csrf_exempt
def appregister(request):

	registered = False
	if request.method == "POST":
		print(request.body.decode('UTF-8'))

		req_data = request.body.decode('UTF-8')
		# req_data = req_data.decode('utf-8')
		# req_data = ast.literal_eval(req_data)
		req_data = json.loads(req_data)
		email = req_data['email']
		password = req_data['password']
		contact_no = str(req_data['contact_no'])
		#Checking Duplicate records of Email or contact no
		conno = req_data['contact_no']
		if(Profile.objects.filter(contact_no=conno).exists()):
			return JsonResponse({
				'success':False,
				'message':'Contact No. must be unique',
			})
		print('First check')
		checkemail = req_data['email']
		if(User.objects.filter(email=checkemail).exists()):
			return JsonResponse({
				'success':False,
				'message':'email must be unique',
			})

		print('Second check')
		#Saving Data in Variables
		first = req_data['first_name']
		last = req_data['last_name']
		user = User.objects.create_user(
			username=first+last+conno,
			first_name=first,
			last_name=last,
			email=email,
			password=password,
			is_active=False
			)
		#user = user.save(commit=False)
		# user.username = first+last+conno
		# user = user.save()
		# user.set_password(password)
		# user.is_active=False;
		user.save()

		#User created, Creating a linked Profile of user
		#user.profile.avatar = req_data['avatar']
		user.profile.contact_no = req_data['contact_no']
		#user.profile.facebook = req_data['facebook']
		#user.profile.linkedin = req_data['linkedin']
		user.profile.status=0
	
		#p = multiprocessing.Process(target=send_mail,args=(email,user,))
		#p.start()
		# send_mail(email, user)

		# current_site = get_current_site(request)
		# mail_subject = "Activate your Ecell account"
		# message = render_to_string('acc_active_email.html',{
		# 	'user':user,
		# 	'domain':current_site.domain,
		# 	'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
		# 	'token':account_activation_token.make_token(user),
		# })
		# to_email = user.email
		# email = EmailMessage(mail_subject,message,to=[to_email])
		# email.send()


		# import http.client



		# conn = http.client.HTTPConnection("api.msg91.com")


		# stringmsg = "http://api.msg91.com/api/sendhttp.php?sender=ECellR&route=4&mobiles=91"
		# stringmsg=stringmsg+conno
		# stringmsg=stringmsg+"&authkey=152650AGXn8tEe5b6d6a39&country=91&message="
		
		# msg = "Your otp is: "
		# msg=msg+otp
		# msg = str(msg)
		# print(msg)
		# stringmsg=stringmsg+ms
		otp = str(randint(1000,9999))
		url = "http://www.merasandesh.com/api/sendsms"
		message = "Your OTP for E-Cell NIT Raipur APP is "+otp+""
		querystring = {"username":"E_SUMMIT","password":"Summit125@","senderid":"SUMMIT","message": message ,"numbers": contact_no,"unicode":"0"}

		response = requests.request("GET", url, params=querystring)

		print(response.text)
		user.profile.otp = otp
		user.profile.save()
		# res = conn.getresponse()
		# data = res.read()
		# print(data.decode("utf-8"))
		print(otp)
		payload = {
			'id' : user.id,
			'email': user.email,
		}

		jwt_token = jwt.encode(payload,conf_settings.SECRET_KEY)
		token = jwt_token.decode('utf-8')
		# print(token)
		return JsonResponse({
			'success' : True,
			'message' : 'Registration successfull',
			'token' : token
		})
	else:
		return JsonResponse({
				'success' :False,
				'message' : 'form method error',
			})

@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.profile.status=1
        user.is_active = True
        user.save()
        return JsonResponse({'success':True,'message':'Account Activated Successfully'})
    else:
        return JsonResponse({'success':False,'message':'Activation link is invalid!'})


@csrf_exempt
def weblogin(request):
	error_msg = {
		'success' : False,
		'message' : 'Invalid credentials'
		}
	if request.method == 'POST':
		# if 'username' in request.session:
		# 	print("USER IN SESSION")
		# 	return
		req_data = json.loads(request.body.decode('UTF-8'))
		email = req_data['email']
		password = req_data['password']
		print(email,password)

		try:
			obj = User.objects.filter(email=email)
			username = obj[0].username
		except:
			return JsonResponse(error_msg)

		user = authenticate(username=username, password=password)
		login(request,user)
		request.session['username'] = username
		return JsonResponse({
			'success' : True,
			'message' : 'authentication successfull',

		})
	else:
		print(request.user)
		return render(request,'login.html')



@csrf_exempt
def webregister(request):

	if request.method == 'POST':
		req_data = json.loads(request.body.decode('UTF-8'))
		email = req_data['email']
		password = req_data['password']
		#print(req_data)

		if User.objects.filter(email=email).exists():
			return JsonResponse({'success':False,'message':'Email already exists'})
		else:
			user = User()
			user.username = email
			user.email = email
			user.set_password(password)
			user.save()
			user.profile.contact_no = req_data['contactno']


			user.profile.save()

			return JsonResponse({
				'success' : True,
				'message' : 'registration successfull'
			})
	else:
		return render(request,'reg.html')


def logout_view(request):
	logout(request)
	return JsonResponse({'success':True,
						 'message':'User logged out successsfully'})

@csrf_exempt
def retry_otp(request):
	response = {}
	if request.method == "POST":
		req_data = request.body.decode('UTF-8')
		# req_data = req_data.decode('utf-8')
		# req_data = ast.literal_eval(req_data)
		req_data = json.loads(req_data)
		email = req_data['email']
		password = req_data['password']
		contact_no = str(req_data['contact_no'])
		if User.objects.filter(email=email).exists():
			user = User.objects.get(email=email)
			otp = str(randint(1000,9999))
			url = "http://www.merasandesh.com/api/sendsms"
			message = "Your OTP for E-Cell NIT Raipur APP is "+otp+""
			querystring = {"username":"E_SUMMIT","password":"Summit125@","senderid":"SUMMIT","message": message ,"numbers": contact_no,"unicode":"0"}

			response_otp = requests.request("GET", url, params=querystring)

			print(response_otp.text)
			user.profile.otp = otp
			user.profile.save()
			# res = conn.getresponse()
			# data = res.read()
			# print(data.decode("utf-8"))
			print(otp)
			payload = {
				'id' : user.id,
				'email': user.email,
			}

			jwt_token = jwt.encode(payload,conf_settings.SECRET_KEY)
			token = jwt_token.decode('utf-8')
			# print(token)
			response['success'] = True
			response['message'] = "OTP resent"
			response['token'] = token
		else:
			response['success'] = False
			response['message'] = "Please try to sign up after few minutes"
	else:
		response['success'] = False
		response['message'] = "Method not allowed"
	return JsonResponse(response)
			

@csrf_exempt
@decoder
def verify_otp(request, *args, **kwargs):
	print("OTP verification requested")
	current_userid = kwargs['user_id']
	current_user = User.objects.get(id=current_userid)
	profile = Profile.objects.get(user=current_user)
	contact_no = profile.contact_no
	contact_no = str(contact_no)
	contact_no = int(contact_no)
	totp = profile.otp
	totp = str(totp)
	print("API call successful")
	if request.method == 'POST':
		req_data = json.loads(request.body.decode('UTF-8'))
		otp = req_data['otp']
		if(totp == otp):
			profile = Profile.objects.get(user=current_user)
			profile.contact_no = str(contact_no)
			profile.status = True
			current_user.is_active = True
			current_user.save()

			profile.save()
			print("OTP Verified")
			return JsonResponse({'success':True,'message':'OTP verified successfully'})
		else:
			print("OTP not verified")
			return JsonResponse({'success':False,'message':'Invalid OTP'})
	print("Method not valid")
	return JsonResponse({'success':False,'message':'Invalid method'})

def social_settings(request):
	user = request.user
	try:
		facebook_login = user.social_auth.get(provider='facebook')
		payload = {
					'id' : facebook_login.extra_data.id,
					'email': user.username,
				}

		jwt_token = jwt.encode(payload,conf_settings.SECRET_KEY)
		token = jwt_token.decode('utf-8')
		return JsonResponse({
			'success' : True,
			'message' : 'authentication successfull',
			'token' : token
		})

	except:
		facebook_login = None
		return JsonResponse({
			'success' : False,
			'message' : 'authentication failed',

		})


@login_req
def password(request):
	if request.user.has_usable_password():
		PasswordForm = PasswordChangeForm
	else:
		PasswordForm = AdminPasswordChangeForm

	if request.method == 'POST':
		form = PasswordForm(request.user, request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request,'Your password was succesfully updated!')
			return redirect('password')

		else:
			messages.error(request,'Please correct the error below.')
	else:
		form = PasswordForm(request.user)
	return render(request,'password.html',{'form':form,})