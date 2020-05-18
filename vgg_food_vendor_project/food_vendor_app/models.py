from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Vendor(models.Model):

    businessName = models.CharField(max_length=100)

    email = models.EmailField(max_length=100)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)


class Customer(models.Model):

    firstname = models.CharField(max_length=32)

    lastname = models.CharField(max_length=32)

    email = models.EmailField(max_length=100)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)


class Auth(models.Model):

    email = models.EmailField(max_length=100)

    password = models.TextField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)

    userTypeId = models.ForeignKey("UserType", on_delete=models.CASCADE)


class UserType(models.Model):

    userTypeName = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True)


class Menu(models.Model):

    name = models.CharField(max_length=50)

    description = models.TextField()

    price = models.FloatField()

    quantity = models.IntegerField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    vendorId = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    isRecurring = models.BooleanField()

    frequencyOfReocurrence = models.IntegerField()


class Order(models.Model):

    customerId = models.ForeignKey("Customer", on_delete=models.CASCADE)

    vendorId = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    description = models.TextField()

    itemsOrdered = ArrayField(base_field=models.CharField(max_length=50))

    amountDue = models.CharField(max_length=50)

    amountPaid = models.CharField(max_length=50)

    amountOutstanding = models.CharField(max_length=50)

    orderStatusId = models.ForeignKey("OrderStatus", on_delete=models.CASCADE)

    menuId = models.ForeignKey("Menu", on_delete=models.CASCADE)

    dateAndTimeOfOrder = models.DateTimeField(
        auto_now_add=True, editable=False)


class OrderStatus(models.Model):

    name = models.CharField(max_length=50, unique=True)


class Notification(models.Model):

    subjectUser = models.ForeignKey("Auth", on_delete=models.CASCADE)

    orderId = models.ForeignKey("Order", on_delete=models.CASCADE)

    message = models.TextField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    messageStatusId = models.ForeignKey(
        "MessageStatus", on_delete=models.CASCADE)


class MessageStatus(models.Model):

    name = models.CharField(max_length=16, unique=True)
