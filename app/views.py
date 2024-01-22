from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from users.forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse

from django.db.models import Max
from .models import (
    Product, Auction, ProductImage, Notification
)
from .forms import ProductForm, AuctionForm

from django.contrib import messages

# to manage auction datetime
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

from django.shortcuts import get_object_or_404

# import stuffs for pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# local time zone
localtz = pytz.timezone('Asia/Dhaka')

def index(request):
	# if request.user.is_authenticated:
	return redirect(reverse('app:dashboard'))
	# else:
	# 	if request.method == 'POST':
	# 		form = CustomUserCreationForm(request.POST)
	# 		# username = form['email'].value()
	# 		if form.is_valid():
	# 			user = form.save()


	# 		# try:
	# 		# 	u = User.objects.create_user(username=username)
	# 		# 	u.save()
	# 		# except IntegrityError as e:
	# 		# 	#get the user if user email exists
	# 		# 	print("email already exits. Taking to login...")
	# 		# 	u = User.objects.get(username=username)

	# 		# user = authenticate(username=username, password=password)
	# 		login(request, u)
	# 		return redirect('/app/dashboard/')
		
	# 	else:
	# 		form = RegisterUserForm()

	# 	return render(request, 'app/index.html', {'form':form})

def logout_user(request):
	logout(request)
	return redirect('/app/')

# @login_required
def dashboard(request):
	user = request.user
	
	products_all = Product.objects.all().order_by('-auc_end_time',)
	products_by_user = []
	
	if request.user.is_authenticated:
		products_by_user = Product.objects.filter(created_by=request.user).order_by('-creation_date')

	paginator = Paginator(products_all, 6)
	page = request.GET.get('page', 1)

	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	curr_datetime = datetime.now()
	context = {'user': user, 'products_by_user': products_by_user, 'page_obj': page_obj, 'curr_datetime': curr_datetime}
	return render(request, 'app/dashboard.html',context)

@login_required
def add_product(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
		form = ProductForm(request.POST)
		images = request.FILES.getlist('images')
		if form.is_valid():
			p = form.save(commit=False)
			p.created_by = request.user
			p.save()

			# now save the product images
			try:
				for image in images:
					image = ProductImage.objects.create(image=image)
					image.product = p
					image.save()
			except Exception as e:
				print(e)
			messages.add_message(request, messages.INFO,
				f'Your Product is up for bidding !!!')
			# return redirect(reverse('app:user_dashboard'))
			data = {
				'message': 'SUCCESS',
				'success_url': f'/product/detail/{p.id}/'
			}
			return JsonResponse(data)
	else:
		form = ProductForm()
	return render(request, 'app/add_product.html', {'form': form})

@login_required
def product_detail(request, id):
	request.session['winner'] = 'yet to decide'
	request.session['edit_access'] = False

	

	try:
		p = Product.objects.get(id=id)
	except Product.DoesNotExist:
		return render(request, 'app/error_404.html')

	local_dt = timezone.localtime(p.auc_end_time, pytz.timezone('Asia/Dhaka'))
	print(local_dt)
	print(datetime.now(localtz))
	print(local_dt > datetime.now(localtz))
	if p.created_by == request.user:
		request.session['edit_access'] = True
	bids = Auction.objects.filter(product=p).order_by('-amount')
	logged_in_user_bid = Auction.objects.filter(product=p, placed_by=request.user).first()

	min_bid_price = p.min_bid_price
	if bids:
		min_bid_price = bids[0].amount

	context = {
		'product': p,
		'bids': bids,
		'logged_in_user_bid': logged_in_user_bid,
		'min_bid_price': min_bid_price+1,
	}

	local_datetime = timezone.now() + timedelta(hours=6)
	if p.auc_end_time < local_datetime:
		biggest_bid = Auction.objects.filter(product=p).aggregate(Max('amount'))
		amount = biggest_bid['amount__max']
		# print(biggest_bid)
		if amount:
			winner = Auction.objects.get(amount=amount).placed_by
			request.session['winner'] = winner.username
		else:
			request.session['winner'] = None

	return render(request, 'app/product_detail.html', context)

@login_required
def product_edit(request, id):
	try:
		p = Product.objects.get(id=id)
	except Product.DoesNotExist:
		return render(request, 'app/error_404.html')
	if p.created_by == request.user:
		if request.method == 'POST':
			form = ProductForm(request.POST, request.FILES, instance=p)
			if form.is_valid():
				form.save()
				messages.add_message(request, messages.INFO,
					f'Updates successfully applied!')
				return redirect(reverse('app:product_detail', kwargs={'id': p.id}))
		else:
			form = ProductForm(instance=p)
		return render(request, 'app/add_product.html', {'form': form})
	return redirect(reverse('app:product_detail', kwargs={'id': p.id}))


@login_required(login_url='/app/')
def product_delete(request, id):

	# check if the product exists, if exists get an instance of it
	try:
		p = Product.objects.get(id=id)
		product_name = p.name
	except Product.DoesNotExist:
		return render(request, 'app/error_404.html')

	# check if someone else is trying to DELETE other than OP
	if request.user == p.created_by:
		p.delete()
		messages.add_message(request, messages.WARNING,
			f'Your Item [{product_name}] successfully deleted!')
		return redirect(reverse('app:user_dashboard'))
	
	# throw error page if someone else is trying to DELETE other than OP  
	return render(request, 'app/error_404.html')


@login_required
def auction(request, p_id):
	product = Product.objects.get(id=p_id)
	min_bid = product.min_bid_price
	# redirect if the OP of this item trying to bid
	if request.user == product.created_by:
		return redirect(reverse('app:product_detail', 
			kwargs={'id': product.id,}
			))

	# if auction time still ON
	if product.auc_end_time > timezone.now():
		bid = Auction.objects.filter(product=product, placed_by=request.user)

		if request.method == 'POST':
			if bid:
				form = AuctionForm(request.POST, instance=bid[0])
				bid = form.save(commit=False)
				if bid.amount < product.min_bid_price:
					messages.add_message(request, messages.WARNING,
						f'Your bid must be greater than {product.min_bid_price}')
					return redirect(reverse('app:auction', kwargs={'p_id': p_id}))
				messages.add_message(request, messages.INFO,
					f'Updates have been applied!')
				bid.save()
			else:
				form = AuctionForm(request.POST)
				if form.is_valid():
					bid = form.save(commit=False)
					if bid.amount < product.min_bid_price:
						messages.add_message(request, messages.WARNING,
							f'Your bid must be greater than {product.min_bid_price}')
						return redirect(reverse('app:auction', kwargs={'p_id': p_id}))
					bid.product = product
					bid.placed_by = request.user
					bid.save()
					messages.add_message(request, messages.INFO,
						f'Your bid is placed! keep your eyes on this item.')
			return redirect(reverse('app:product_detail', kwargs={'id': p_id}))

		else:
			if bid:
				form = AuctionForm(instance=bid[0])
				request.session['mode'] = 'Update'
			else:
				form = AuctionForm()
				request.session['mode'] = 'Add'
		return render(request, 'app/auction.html', {'form': form, 'min_bid': min_bid})
	
	else:
		messages.add_message(request, messages.WARNING,
			f'Bidding on This Item is Ended. See Results')
		return redirect(reverse('app:product_detail', 
			kwargs={'id': product.id,}
			))

@login_required
def bids(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest' :
		if request.method == 'POST':
			bid_amount = float(request.POST.get('bid_amount'))
			product_id = int(request.POST.get('product_id'))
			product = Product.objects.filter(id=product_id).first()

			# check if bid already exists. If exists then update
			existed_bid = Auction.objects.filter(product=product, placed_by=request.user).first()
			highest_bid = Auction.objects.filter(product=product).order_by('-amount').first()

			if existed_bid:
				if bid_amount > float(existed_bid.amount):
					existed_bid.amount = bid_amount
					existed_bid.placed_datetime = timezone.now()
					existed_bid.save()
					messages.add_message(request, messages.SUCCESS,
						f'Successfully updated your bid.'	  
					)

					data = {
						'message': 'SUCCESS',
						'success_url': f'/product/detail/{product_id}/'
					}
					return JsonResponse(data)

				else:
					messages.add_message(request, messages.WARNING,
						f'Update bid should be higher than current bid amount.')
					
					data = {
						'message': 'FAILED',
						'success_url': f'/product/detail/{product_id}/'
					}
					return JsonResponse(data)
			else:
				try:
					if highest_bid:
						if bid_amount <= highest_bid.amount :
							messages.add_message(request, messages.WARNING,
								f'Bid amount should be higher than the current price of the product')
							
							data = {
								'message': 'FAILED',
								'success_url': f'/product/detail/{product_id}/'
							}
							return JsonResponse(data)
						else:
							a = Auction.objects.create(
								product=product,
								amount=bid_amount,
								placed_by=request.user
							)
							a.save()
							print(a)
							data = {
								'message': 'SUCCESS',
								'success_url': f'/product/detail/{product_id}/'
							}
							return JsonResponse(data)
					else:
						a = Auction.objects.create(
							product=product,
							amount=bid_amount,
							placed_by=request.user
						)
						a.save()
						print(a)
						data = {
							'message': 'SUCCESS',
							'success_url': f'/product/detail/{product_id}/'
						}
						return JsonResponse(data)
				except Exception as e:
					print(e)
					data = {
						'message': 'FAILED',
						'success_url': f'/product/detail/{product_id}/'
					}
					return JsonResponse(data)
			
		# elif request.method == 'PATCH':
		# 	print(request.pa)
	else:
		return render(request, 'app/bids_list.html')
	

def bids_list(request, product_id):
	product = get_object_or_404(Product, pk=product_id)
	bids = Auction.objects.filter(product=product).order_by('-amount')
	bid_running = product.is_bid_running
	winner = ''
	if not bid_running and bids:
		winner = bids[0].placed_by
	context = {
		'product': product,
		'bids': bids,
		'bid_running': bid_running,
		'winner': winner,
	}

	return render(request, 'app/bids_list.html', context=context)


@login_required
def notifications(request):
	notifications_all = Notification.objects.filter(user=request.user).order_by('-created_at')
	context = {
		'notifications': notifications_all
	}
	return render(request, 'app/notifications.html', context=context)

@login_required
def user_dashboard(request):
	products_by_user = Product.objects.filter(created_by=request.user).order_by('-auc_end_time', '-creation_date')
	bidded_items = Auction.objects.filter(placed_by=request.user).order_by('product')
	
	paginator = Paginator(products_by_user, 6)
	page = request.GET.get('page', 1)

	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	context = {'bidded_items':bidded_items, 'page_obj': page_obj}
	return render(request, 'app/user_dashboard.html',context)
	

