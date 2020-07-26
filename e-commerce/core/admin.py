from django.contrib import admin

from .models import Order,OrderItem,Item,Address,Payment,Refund

def meke_refund_accepted(ModelAdmin,request,querset):
    querset.update(refaund_request=False,refaund_granted=True)
meke_refund_accepted.short_description=("Make order to refund granted")

class OrderAdmin(admin.ModelAdmin):
    list_display=[
        'user',
        'ordered',
        'payment',
        'being_delivared',
        'received',
        'refaund_request',
        'refaund_granted',
        'shipping_address',
        'billing_address',
    ]
    list_display_links=[
        'shipping_address',
        'billing_address',
        'user',
        'payment'
    ]
    search_fields=[
        'user__username',
        'ref_code'
    ]
    list_filter=[
        'ordered',
        'being_delivared',
        'received',
        'refaund_request',
        'refaund_granted',
    ]
    actions=[meke_refund_accepted]
class AddressAdmin(admin.ModelAdmin):
    list_display=[
        'user',
        'street_address',
        'appartment_address',
        'zip',
        'address_type',
        'country',
        'default',
    ]
    list_filter=['default','address_type','country']
    list_display_links=['user','street_address','appartment_address','zip']


admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Item)
admin.site.register(Payment)
admin.site.register(Address,AddressAdmin)
admin.site.register(Refund)
