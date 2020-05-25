from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField


class Vendor(models.Model):

    businessName = models.CharField(max_length=100)

    email = models.EmailField(max_length=100, unique=True)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True, editable=False)


class Customer(models.Model):

    firstname = models.CharField(max_length=32)

    lastname = models.CharField(max_length=32)

    email = models.EmailField(max_length=100, unique=True)

    phoneNumber = models.CharField(max_length=16, unique=True)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True, editable=False)


class Auth(models.Model):

    email = models.EmailField(max_length=100, unique=True)

    password = models.TextField()

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    dateTimeModified = models.DateTimeField(auto_now=True, editable=False)


class Menu(models.Model):

    name = models.CharField(max_length=50, unique=True)

    description = models.TextField()

    price = models.FloatField()

    quantity = models.IntegerField()

    unit = models.CharField(max_length=16)

    dateTimeCreated = models.DateTimeField(auto_now_add=True, editable=False)

    vendorId = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    isRecurring = models.BooleanField(default=False)

    frequencyOfReoccurrence = ArrayField(
        base_field=models.CharField(max_length=10), size=7)


class Order(models.Model):

    customerId = models.ForeignKey("Customer", on_delete=models.CASCADE)

    vendorId = models.ForeignKey("Vendor", on_delete=models.CASCADE)

    description = models.TextField(null=True)

    itemsOrdered = ArrayField(base_field=models.IntegerField())

    amountDue = models.FloatField()

    amountPaid = models.FloatField(default=0)

    amountOutstanding = models.FloatField()

    orderStatusId = models.ForeignKey("OrderStatus", on_delete=models.CASCADE)

    dateAndTimeOfOrder = models.DateTimeField(
        auto_now_add=True, editable=False)

    preOrderDateTime = models.DateTimeField(null=True)


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
