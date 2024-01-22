from django.db import models
from django.conf import settings

from django.utils import timezone
from datetime import datetime


# TODO: Category table should be added
class Category(models.Model):
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True)

	def __str__(self) -> str:
		return self.name
	

PRODUCT_CONDITION_CHOICES = [
	('new', 'New'),
	('open_box', 'Open box'),
	('used', 'Used'),
]


class Product(models.Model):
	name = models.CharField(max_length=200, verbose_name='Product Name',)
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
	condition = models.CharField(max_length=30, choices=PRODUCT_CONDITION_CHOICES, verbose_name='Product Condition')
	description = models.TextField(null=True, blank=True)
	# photo = models.ImageField(null=True, blank=True, upload_to='uploads/%Y-%m-%d', default='default.png')
	min_bid_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Minimum Bidding Price')
	auc_end_time = models.DateTimeField(verbose_name='Bid Ends at ')
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	creation_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['auc_end_time']
	
	@property
	def is_bid_running(self):
		from datetime import timedelta
		local_dt = timezone.now() + timedelta(hours=6)
		return self.auc_end_time > local_dt
	
	@property
	def time_left(self):
		return self.auc_end_time - timezone.now()


	def __str__(self):
		return self.name

class Auction(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='auctions')
	placed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	placed_datetime = models.DateTimeField(auto_now_add=True)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, default=None, null=True, blank=True, related_name='product_images')
    image = models.ImageField(upload_to='uploads')


NOTIFICATION_TYPES = [
	('outbid', 'Out Bid'),
	('win', 'Win')
]

class Notification(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	bid = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name='bids')
	bid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	seen = models.BooleanField(default=False)
	type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES, default='outbid', null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

