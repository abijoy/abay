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
from django.shortcuts import get_object_or_404

# import stuffs for pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



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
	products_all = Product.objects.all().exclude(created_by=request.user).order_by('-creation_date')
	products_by_user = Product.objects.filter(created_by=request.user).order_by('-creation_date')

	paginator = Paginator(products_all, 6)
	page = request.GET.get('page', 1)

	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	context = {'user': user, 'products_by_user': products_by_user, 'page_obj': page_obj}
	return render(request, 'app/dashboard.html',context)

@login_required(login_url='/app/')
def add_product(request):
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			p = form.save(commit=False)
			p.created_by = request.user
			p.save()
			return redirect(reverse('dashboard'))
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

	if p.created_by == request.user:
		request.session['edit_access'] = True
	bids = Auction.objects.filter(product=p)
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
				# p = form.save(commit=False)
				# p.created_by = request.user
				# p.save()
				return redirect(reverse('dashboard'))
		else:
			form = ProductForm(instance=p)
		return render(request, 'app/add_product.html', {'form': form})
	return redirect(reverse('product_detail', kwargs={'id': p.id}))

@login_required(login_url='/app/')
def product_delete(request, p_id):
	pass

@login_required(login_url='/app/')
def auction(request, p_id):
	product = Product.objects.get(id=p_id)
	if request.user == product.created_by:
		return redirect(reverse('product_detail', 
			kwargs={'id': product.id,}
			))
	if product.auc_end_time > timezone.now():
		bid = Auction.objects.filter(product=product, placed_by=request.user)

		if request.method == 'POST':
			if bid:
				form = AuctionForm(request.POST, instance=bid[0])
				form.save()
			else:
				form = AuctionForm(request.POST)
				if form.is_valid():
					bid = form.save(commit=False)
					bid.product = product
					bid.placed_by = request.user
					bid.save()
			return redirect(reverse('product_detail', kwargs={'id': p_id}))

		else:
			if bid:
				form = AuctionForm(instance=bid[0])
			else:
				form = AuctionForm()
		return render(request, 'app/auction.html', {'form': form})
	else:
		messages.add_message(request, messages.WARNING,
			f'Bidding on This Item is Ended. See Results')
		return redirect(reverse('product_detail', 
			kwargs={'id': product.id,}
			))