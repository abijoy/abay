from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
from datetime import datetime


# TODO: Category table should be added

class Product(models.Model):
	# TODO: One-to-One link to the Category items
	name = models.CharField(max_length=200, verbose_name='Product Name',)
	description = models.TextField(null=True, blank=True)
	photo = models.ImageField(null=True, blank=True, upload_to='uploads/%Y-%m-%d', default='default.png')
	min_bid_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Minimum Bidding Price')
	auc_end_time = models.DateTimeField(verbose_name='Bid Ends at ')
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	creation_date = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['auc_end_time']
	
	@property
	def is_bid_running(self):
		from datetime import timedelta
		local_dt = timezone.now() + timedelta(hours=6)
		return self.auc_end_time > local_dt

	def __str__(self):
		return self.name

class Auction(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	placed_by = models.ForeignKey(User, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	placed_datetime = models.DateTimeField(auto_now_add=True)