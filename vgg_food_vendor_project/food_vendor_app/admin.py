from django.contrib import admin
from vgg_food_vendor_project.food_vendor_app.models import Vendor, Customer, Auth, UserType, Menu, Order, OrderStatus, Notification, MessageStatus

# Register your models here.
admin.site.register(Vendor)
admin.site.register(Customer)
admin.site.register(Auth)
admin.site.register(UserType)
admin.site.register(Menu)
admin.site.register(Order)
admin.site.register(OrderStatus)
admin.site.register(Notification)
admin.site.register(MessageStatus)
