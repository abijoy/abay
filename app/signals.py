from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    pre_save,
    pre_delete,
    post_delete,
    m2m_changed,
)
from django.utils import timezone
from .models import Auction, Notification


@receiver(post_save, sender=Auction)
def auction_post_save(sender, instance, created, *args, **kwargs):
    print('--------- SIGNAL ----------')
    if not created:
        product = instance.product
        other_bids = Auction.objects.filter(product=product).exclude(placed_by=instance.placed_by)
        other_users = []
        for bid in other_bids:
            if bid.amount < instance.amount:
                other_users.append(bid.placed_by)
        
        print(other_users)
        # Now notify the other users who just got outbid
        for user in other_users:
            try:
                n = Notification.objects.create(
                    user=user,
                    bid = instance,
                    product=product,
                    bid_amount = instance.amount
                )

                # could be send email here as notificaiton medium
                # ...
            except Exception as e:
                print(e)
    





