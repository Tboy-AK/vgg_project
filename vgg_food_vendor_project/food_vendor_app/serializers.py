from rest_framework import serializers
from vgg_food_vendor_project.food_vendor_app import models as inAppModels


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Vendor
        fields = ['id', 'businessName', 'email', 'phoneNumber',
                  'dateTimeCreated', 'dateTimeModified']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Customer
        fields = ['id', 'firstname', 'lastname', 'email', 'phoneNumber',
                  'dateTimeCreated', 'dateTimeModified']


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Auth
        fields = ['id', 'email', 'password',
                  'dateTimeCreated', 'dateTimeModified']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Menu
        fields = ['id', 'name', 'description', 'price', 'quantity', 'unit',
                  'dateTimeCreated', 'vendorId', 'isRecurring', 'frequencyOfReoccurrence']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Order
        fields = ['id', 'customerId', 'vendorId', 'description', 'itemsOrdered', 'amountDue',
                  'amountPaid', 'amountOutstanding', 'orderStatusId', 'menuId', 'dateAndTimeOfOrder', 'preOrderDateTime']


class Order_OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Order
        fields = ['orderStatusId']


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.OrderStatus
        fields = ['id', 'name']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.Notification
        fields = ['id', 'subjectUser', 'orderId',
                  'message', 'dateTimeCreated', 'messageStatusId']


class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = inAppModels.MessageStatus
        fields = ['id', 'name']
