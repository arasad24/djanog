from django.shortcuts import render,get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,DetailView,View
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from .forms import CheckoutForm,RefundForm
from .models import Item,OrderItem,Order,Address,Payment,Refund



import random
import string

import stripe
stripe.api_key = 'sk_test_4pStMFNhjoHGLZBolR6JN9qZ007BEo7WJZ'

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))

class HomeView(ListView):
    model=Item
    paginate_by=8
    template_name='home.html'


class ItemDetailView(DetailView):
    model=Item
    template_name='product.html'

class OrderSummeryView(LoginRequiredMixin, View):
    def get(self,*args ,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
                'object':order
            }
            return render(self.request,'order-summary.html',context)
        except ObjectDoesNotExist:
            messages.warning(self.request,"You do not have an active order")
            return redirect("/")

def is_valid_form(values):
    valid=True
    for field in values:
        if field =="":
            valid=False
    return valid

class CheckOutView(View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            form=CheckoutForm
            context={
                'order':order,
                'form':form
                }
            shipping_address_qs=Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
                )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address':shipping_address_qs[0]})

            billing_address_qs=Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update({'default_billing_address':billing_address_qs[0]})
            return render(self.request,'checkout.html',context)
        except ObjectDoesNotExist:
            messages.info(self.request,"You do not have an active order")
            return redirect("checkout")
    def post(self,*args,**kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                use_default_shipping=form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    address_qs=Address.objects.filter(
                        user=self.request.user,
                        default=True,
                        address_type='S'

                    )
                    if address_qs.exists():
                        shipping_address=address_qs[0]
                        order.shipping_address=shipping_address
                        order.save()
                    else:
                        messages.info(self.request,"No default shipping address")
                        return redirect("/checkout")
                else:
                    shipping_address=form.cleaned_data.get('shipping_address')
                    shipping_address2=form.cleaned_data.get('shipping_address2')
                    shipping_country=form.cleaned_data.get('shipping_country')
                    shipping_zip=form.cleaned_data.get('shipping_zip')
                    if is_valid_form([shipping_address,shipping_country,shipping_zip]):
                        shipping_address=Address(
                            user=self.request.user,
                            street_address=shipping_address,
                            appartment_address=shipping_address2,
                            zip=shipping_zip,
                            country=shipping_country,
                            address_type='S'

                        )
                        shipping_address.save()
                        order.shipping_address=shipping_address
                        order.save()

                        set_default_shipping_address=form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping_address:
                            shipping_address.default=True
                            shipping_address.save()
                    else:
                        messages.info(self.request,"Please fill in the required shipping Address Field")

                # for billing address 
                same_billing_address=form.cleaned_data.get('same_billing_address')
                use_default_billing=form.cleaned_data.get('use_default_billing')
                if same_billing_address:
                    billing_address=shipping_address
                    billing_address.pk=None
                    billing_address.save()
                    billing_address.address_type="B"
                    billing_address.save()
                    order.billing_address=billing_address
                    order.save()

                elif use_default_billing:
                    address_qs=Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address=address_qs[0]
                        billing_address.save()
                        order.billing_address=billing_address
                        order.save()
                    else:
                        messages.info(self.request,"No default billing Address available")
                        return redirect("checkout")
                else:
                    billing_address=form.cleaned_data.get('billing_address')
                    billing_address2=form.cleaned_data.get('billing_address2')
                    billing_country=form.cleaned_data.get('billing_country')
                    billing_zip=form.cleaned_data.get('billing_zip')
                    if is_valid_form([billing_address,billing_country,billing_zip]):
                        billing_address=Address(
                            user=self.request.user,
                            street_address=billing_address,
                            appartment_address=billing_address2,
                            zip=billing_zip,
                            country=billing_country,
                            address_type='B'
                            )   
                        billing_address.save()
                        order.billing_address=billing_address
                        order.save()
                        set_default_billing=form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default=True
                            billing_address.save()
                    else:
                        messages.info(self.request,"please fill the required billing address")

                payment_option=form.cleaned_data.get('payment_option')

                if payment_option=="S":
                    return redirect("payment",payment_option='stripe')
                elif payment_option=="P":
                    return redirect("payment",payment_option='paypal')
                else:
                    messages.info(self.request,"You Selected invalid payment option")
            else:
                messages.info(self.request,"Somethings went wrong")
                return redirect("checkout")
        except ObjectDoesNotExist:
            messages.info(self.request,"You do not have an active order")
            return redirect("order-summary")

class PaymentView(View):
    def get(self,*args,**kwargs):
        return render(self.request,"payment.html")

    def post(self,*args,**kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        token=self.request.POST.get('stripeToken')
        # token = 'tok_visa'
        amount=int((order.get_total()) * 100)
        try:
            charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token, 
            )
            payment=Payment()
            payment.stripe_charge_id=charge['id']
            payment.user=self.request.user
            payment.amount=order.get_total()
            payment.save()

            order_items=order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered=True
            order.payment=payment
            order.ref_code=create_ref_code()
            order.save()
            messages.info(self.request,"Your order is placed successfully")
            return redirect("/")

        except stripe.error.CardError as e:
            body=e.json_body
            err=body.get('error',{})
            messages.warning(self.request,f"{error.get('messages')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            messages.warning(self.request,"Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request,"Invalid Parametter")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            messages.warning(self.request,"Authentication error")
            return redirect("/")
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request,"Network error")
            return redirect("/")
        except stripe.error.StripeError as e:
            messages.warning(self.request,"Somethings went wrong ,your era not charged.please try again")
            return redirect("/")
        except Exception as e:
            messages.warning(self.request,"A serious problem occour,please email us ")
            return redirect("/")

@login_required
def add_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_item,created=OrderItem.objects.get_or_create(
        user=request.user,
        item=item,
        ordered=False
    )
    print(order_item)
    print(created)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    print(order_qs.query)
    if order_qs.exists():
        order=order_qs[0]
        print(order)
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"This item quantity was updated")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request,"This item was added in your cart")
            return redirect("order-summary")
    else:
        order_date=timezone.now()
        order=Order.objects.create(user=request.user,order_date=order_date)
        order.items.add(order_item)
        messages.info(request,"This item was added in your cart")
        return redirect("order-summary")
@login_required
def remove_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
                user=request.user,
                item=item,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request,"This item was remove from your cart")
            return redirect("order-summary")
        else:
            messages.info(request,"This item not on your cart")
            return redirect ("product",slug=slug)
    else:
        messages.info(request,"/")
        return redirect("product",slug=slug)
    return redirect("product",slug=slug)
    

@login_required
def remove_single_item_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(
                user=request.user,
                item=item,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,"This item quantity was updated")
            return redirect("order-summary")
        else:
            messages.info(request,"This item was not in your cart")
            return redirect("product,slug=slug")
    else:
        messages.info(request,"You do not have an active order")
        return redirect("product,slug=slug")
    return redirect("product,slug=slug")


class RefundView(View):
    def get(self,*args,**kwargs):
        form=RefundForm
        context={
            'form':form
        }
        return render(self.request,"refund_request.html",context)

    def post(self,*args,**kwargs):
        form=RefundForm(self.request.POST)
        if form.is_valid():
            ref_code=form.cleaned_data.get('ref_code')
            message=form.cleaned_data.get('message')
            email=form.cleaned_data.get('email')
            try:
                order=Order.objects.get(ref_code=ref_code)
                order.refaund_request=True
                order.save()

                # store data in model
                refund=Refund()
                refund.order=order
                refund.reason=message
                refund.email=email
                refund.save()
                messages.info(self.request,"Your request was accepted")
                return redirect("refund-request")
            except ObjectDoesNotExist:
                messages.info(self.request,"Your order does not exists")
                return redirect("refund-request")