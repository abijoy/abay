from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterUserForm
from django.contrib.auth.models import User
from django.db import IntegrityError

from django.db.models import Max
from .models import Product, Auction
from .forms import ProductForm, AuctionForm

from django.contrib import messages

# to manage auction datetime
from django.utils import timezone
from datetime import datetime
import pytz

from django.shortcuts import get_object_or_404

# import stuffs for pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# local time zone
localtz = pytz.timezone('Asia/Dhaka')

def index(request):
	if request.user.is_authenticated:
		return redirect(reverse('dashboard'))
	else:
		if request.method == 'POST':
		        form = RegisterUserForm(request.POST)
		        username = form['email'].value()
		        try:
		        	u = User.objects.create_user(username=username)
		        	u.save()
		        except IntegrityError as e:
		        	#get the user if user email exists
		        	print("email already exits. Taking to login...")
		        	u = User.objects.get(username=username)

		        # user = authenticate(username=username, password=password)
		        login(request, u)
		        return redirect('/app/dashboard/')
		            
		else:
			form = RegisterUserForm()

		return render(request, 'app/index.html', {'form':form})

def logout_user(request):
	logout(request)
	return redirect('/app/')

@login_required(login_url='/app/')
def dashboard(request):
	user = request.user
	
	products_all = Product.objects.all().order_by('-auc_end_time',)

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

@login_required(login_url='/app/')
def add_product(request):
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save(commit=False)
			p.created_by = request.user
			p.save()
			messages.add_message(request, messages.INFO,
				f'Your Product is up for bidding !!!')
			return redirect(reverse('user_dashboard'))
	else:
		form = ProductForm()
	return render(request, 'app/add_product.html', {'form': form})

@login_required(login_url='/app/')
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
	context = {'product': p, 'bids': bids,}
	if p.auc_end_time < timezone.now():
		biggest_bid = Auction.objects.filter(product=p).aggregate(Max('amount'))
		amount = biggest_bid['amount__max']
		# print(biggest_bid)
		if amount:
			winner = Auction.objects.get(amount=amount).placed_by
			request.session['winner'] = winner.username
		else:
			request.session['winner'] = None

	return render(request, 'app/product_detail.html', context)

@login_required(login_url='/app/')
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
				return redirect(reverse('product_detail', kwargs={'id': p.id}))
		else:
			form = ProductForm(instance=p)
		return render(request, 'app/add_product.html', {'form': form})
	return redirect(reverse('product_detail', kwargs={'id': p.id}))


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
		return redirect(reverse('user_dashboard'))
	
	# throw error page if someone else is trying to DELETE other than OP  
	return render(request, 'app/error_404.html')


@login_required(login_url='/app/')
def auction(request, p_id):
	product = Product.objects.get(id=p_id)
	min_bid = product.min_bid_price
	# redirect if the OP of this item trying to bid
	if request.user == product.created_by:
		return redirect(reverse('product_detail', 
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
					return redirect(reverse('auction', kwargs={'p_id': p_id}))
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
						return redirect(reverse('auction', kwargs={'p_id': p_id}))
					bid.product = product
					bid.placed_by = request.user
					bid.save()
					messages.add_message(request, messages.INFO,
						f'Your bid is placed! keep your eyes on this item.')
			return redirect(reverse('product_detail', kwargs={'id': p_id}))

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
		return redirect(reverse('product_detail', 
			kwargs={'id': product.id,}
			))

@login_required(login_url='/app/')
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
	

