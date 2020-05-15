from django.db import models

from django.utils import timezone

from django.contrib.postgres.fields import ArrayField


class Vendor(models.Model):

    businessName = models.CharField(max_length=100)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)

    auth_id = models.ForeignKey("Auth", on_delete=models.CASCADE)


class Customer(models.Model):

    firstname = models.CharField(max_length=32)

    lastname = models.CharField(max_length=32)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)

    auth_id = models.ForeignKey("Auth", on_delete=models.CASCADE)


class Auth(models.Model):

    email = models.CharField(max_length=100, unique=True)

    password = models.CharField(max_length=32)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)


class Menu(models.Model):

    name = models.CharField(max_length=50)

    description = models.TextField()

    price = models.DecimalField(decimal_places=2)

    quantity = models.IntegerField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    vendorId = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    isRecurring = models.BooleanField()

    frequencyOfReocurrence = models.IntegerField()


class Order(models.Model):

    customerId = models.ForeignKey("Customer", on_delete=models.SET_NULL)

    vendorId = models.ForeignKey("Vendor", on_delete=models.SET_NULL)

    description = models.TextField()

    itemsOrdered = ArrayField(base_field=models.CharField(max_length=50))

    amountDue = models.CharField(max_length=50)

    amountPaid = models.CharField(max_length=50)

    amountOutstanding = models.CharField(max_length=50)

    orderStatusId = models.ForeignKey("OrderStatus", on_delete=models.SET_NULL)

    menuId = models.ForeignKey("Menu", on_delete=models.SET_NULL)

    dateAndTimeOfOrder = models.DateTimeField(
        auto_now_add=True, editable=False)


class OrderStatus(models.Model):

    name = models.CharField(max_length=50, unique=True)


class Notification(models.Model):

    fromVendor = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    toCustomer = models.ForeignKey("Customer", on_delete=models.CASCADE)

    orderId = models.ForeignKey("Order", on_delete=models.CASCADE)

    message = models.TextField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    messageStatusId = models.ForeignKey(
        "MessageStatus", on_delete=models.SET_NULL)


class MessageStatus(models.Model):

    name = models.CharField(max_length=16, unique=True)
