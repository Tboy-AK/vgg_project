from django.contrib.auth.models import User, Group
from rest_framework import serializers
from vgg_food_vendor_project.food_vendor_app import models as inAppModels


class UserSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerialiser(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class AuthSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Auth
        fields = ['email', 'password', 'dateTimeCreated', 'dateTimeModified']


class VendorSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Vendor
        fields = ['businessName', 'phoneNumber',
                  'dateTimeCreated', 'dateTimeModified', 'auth_id']


class CustomerSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Customer
        fields = ['firstname', 'lastname', 'phoneNumber',
                  'dateTimeCreated', 'dateTimeModified', 'auth_id']


class MenuSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Menu
        fields = ['name', 'description', 'price', 'quantity', 'dateTimeCreated',
                  'vendorId', 'isRecurring', 'frequencyOfReocurrence']


class OrderSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Order
        fields = ['customerId', 'vendorId', 'description', 'itemsOrdered', 'amountDue',
                  'amountPaid', 'amountOutstanding', 'orderStatusId', 'menuId', 'dateAndTimeOfOrder']


class OrderStatusSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.OrderStatus
        fields = ['name']


class NotificationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Notification
        fields = ['fromVendor', 'toCustomer', 'orderId',
                  'message', 'dateTimeCreated', 'messageStatusId']


class MessageStatusSerialiser(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.MessageStatus
        fields = ['name']
