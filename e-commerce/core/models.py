from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGOY_CHOICE=(
    ('L','Laptop'),
    ('S','Smartphone'),
    ('T','Tablet'),
    ('H','Heahphones'),
    ('C','Camera'),
    ('A','Accesories'),
)


ADDRESS_CHOICE=(
    ('B','Billing'),
    ('S','Shipping')
)

class Item(models.Model):
    title=models.CharField(max_length=20)
    price=models.FloatField()
    discount_price=models.FloatField(blank=True,null=True)
    image=models.ImageField()
    category=models.CharField(choices=CATEGOY_CHOICE,max_length=1)
    slug=models.SlugField()
    description=models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product",kwargs={
            'slug':self.slug
        })
        
    def get_add_to_cart_url(self):
        return reverse("add-to-cart",kwargs={
            'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart",kwargs={
            'slug':self.slug
        })
    def get_remove_single_item_from_cart(self):
        return reverse("remove-single-item-from-cart",kwargs={
            'slug':self.slug
        })

class OrderItem(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered=models.BooleanField(default=False)
    quantity=models.IntegerField(default=1)
    item=models.ForeignKey(Item,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.item.price * self.quantity

    def get_total_discount_price(self):
        if self.item.discount_price>1:
            return self.item.discount_price * self.quantity
        return False
    def get_amount_saved(self):
        return self.get_total_price() - self.get_total_discount_price()
    def get_final_price(self):
        if self.get_total_discount_price:
            return self.get_total_discount_price()
        return self.get_total_price()


class Order(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    order_date=models.DateTimeField()
    ref_code=models.CharField(max_length=20)
    ordered=models.BooleanField(default=False)
    payment=models.ForeignKey('Payment',on_delete=models.SET_NULL,blank=True,null=True)
    shipping_address=models.ForeignKey('Address',related_name='shipping_address',on_delete=models.SET_NULL,blank=True,null=True)
    billing_address=models.ForeignKey('Address',related_name='billing_address',on_delete=models.SET_NULL,blank=True,null=True)
    being_delivared=models.BooleanField(default=False)
    received=models.BooleanField(default=False)
    refaund_request=models.BooleanField(default=False)
    refaund_granted=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total
class Address(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    street_address=models.CharField(max_length=100)
    appartment_address=models.CharField(max_length=100)
    zip=models.CharField(max_length=100)
    country=CountryField(multiple=False)
    address_type=models.CharField(max_length=1, choices=ADDRESS_CHOICE)
    default=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    class Meta:
        verbose_name_plural='Addresses'

class Payment(models.Model):
    stripe_charge_id=models.CharField(max_length=50)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True)
    amount=models.FloatField()
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Refund(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    reason=models.TextField()
    accepted=models.BooleanField(default=False)
    email=models.EmailField()


    def __str__(self):
        return f"{self.pk}"