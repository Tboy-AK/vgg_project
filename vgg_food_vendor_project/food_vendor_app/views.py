from os import getenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from vgg_food_vendor_project.food_vendor_app.models import Auth, Customer, Menu, MessageStatus, Notification, Order, OrderStatus, Vendor, UserType
from vgg_food_vendor_project.food_vendor_app.serializers import UserSerializer, GroupSerializer, AuthSerializer, CustomerSerializer, MenuSerializer, MessageStatusSerializer, NotificationSerializer, OrderSerializer, OrderStatusSerializer, VendorSerializer, UserTypeSerializer


def getSingularDataObject(self, relationalModel, id):
    """
    Function that gets a database row by id.
    """
    try:
        return relationalModel.objects.get(id=id)
    except relationalModel.DoesNotExist:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class HomeDescAPIView(APIView):
    """
    API endpoint that allows vendors to be viewed or created.
    """

    def get(self):
        """
        Endpoint method that allows all vendors to be viewed.
        """

        app_base_route = getenv(
            'APP_BASE_ROUTE', 'http://localhost:8000/vgg-food-vendor')

        return Response({
            'vendor/': '{}/vendor/'.format(app_base_route),
            'customer/': '{}/customer/'.format(app_base_route),
            'auth-user/': '{}/auth-user/'.format(app_base_route),
            'menu/': '{}/menu/'.format(app_base_route),
            'order/': '{}/order/'.format(app_base_route),
            'order-status/': '{}/order-status/'.format(app_base_route),
            'notification/': '{}/notification/'.format(app_base_route),
            'message-status/': '{}/message-status/'.format(app_base_route),
            'user-type/': '{}/user-type/'.format(app_base_route),
        })


class VendorAPIView(APIView):
    """
    API endpoint that allows vendors to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all vendors to be viewed.
        """
        vendors = Vendor.objects.all()
        serializer = VendorSerializer(vendors, many=True)
        return Response({
            'requiredFields': {'businessName': '', 'email': '', 'phoneNumber': '', 'password': ''},
            'responseData': serializer.data,
        })

    def post(self, request):
        """
        Endpoint method that allows a new vendor to be created.
        """
        serializer = VendorSerializer(data=request.data)

        try:
            userType = UserType.objects.get(userTypeName='vendor')
        except UserType.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        userTypeSerializer = UserTypeSerializer(userType)
        request.data['userTypeId'] = userTypeSerializer.data['id']

        authSerializer = AuthSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            if authSerializer.is_valid():
                authSerializer.save()
            else:
                return Response(authSerializer.errors, status=status.HTTP_404_NOT_FOUND)
            serializingResponse = serializer.data
            serializingResponse['userTypeName'] = 'vendor'
            return Response(serializingResponse, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetVendorAPIView(APIView):
    """
    API endpoint that allows a vendor to be viewed or edited.
    """

    def get(self, request, id):
        """
        Endpoint method that gets a database row by id.
        """
        userType = getSingularDataObject(Vendor, id)
        serializer = VendorSerializer(userType)
        return Response(serializer.data)


class CustomerAPIView(APIView):
    """
    API endpoint that allows customers to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all customers to be viewed.
        """
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response({
            'requiredFields': {'firstname': '', 'lastname': '', 'email': '', 'phoneNumber': '', 'password': ''},
            'responseData': serializer.data,
        })

    def post(self, request):
        """
        Endpoint method that allows a new customer to be created.
        """

        serializer = UserTypeSerializer(data=request.data)

        try:
            userType = UserType.objects.get(userTypeName='customer')
        except UserType.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        userTypeSerializer = UserTypeSerializer(userType)
        request.data['userTypeId'] = userTypeSerializer.data['id']

        authSerializer = AuthSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            if authSerializer.is_valid():
                authSerializer.save()
            else:
                return Response(authSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializingResponse = serializer.data
            serializingResponse['userTypeName'] = 'customer'
            return Response(serializingResponse, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetCustomerAPIView(APIView):
    """
    API endpoint that allows a customer to be viewed or edited.
    """

    def get(self, request, id):
        """
        Endpoint method that gets a database row by id.
        """
        userType = getSingularDataObject(Customer, id)
        serializer = CustomerSerializer(userType)
        return Response(serializer.data)


class AuthAPIView(APIView):
    """
    API endpoint that allows Auth users to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all Auth users to be viewed.
        """
        authUsers = Auth.objects.all()
        serializer = AuthSerializer(authUsers, many=True)
        return Response(serializer.data)


class UserTypeAPIView(APIView):
    """
    API endpoint that allows UserType users to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all user types to be viewed.
        """
        userType = UserType.objects.all()
        serializer = UserTypeSerializer(userType, many=True)
        return Response(serializer.data)


class MenuAPIView(APIView):
    """
    API endpoint that allows menus to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all menus to be viewed.
        """
        menus = Menu.objects.all()
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Endpoint method that allows a new menu to be created.
        """
        serializer = MenuSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetMenuAPIView(APIView):
    """
    API endpoint that allows a menu to be viewed or edited.
    """

    def get(self, request, id):
        """
        Endpoint method that gets a database row by id.
        """
        userType = getSingularDataObject(Menu, id)
        serializer = MenuSerializer(userType)
        return Response(serializer.data)


class OrderAPIView(APIView):
    """
    API endpoint that allows orders to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all orders to be viewed.
        """
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Endpoint method that allows a new order to be created.
        """
        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetOrderAPIView(APIView):
    """
    API endpoint that allows an order to be viewed or edited.
    """

    def get(self, request, id):
        """
        Endpoint method that gets a database row by id.
        """
        userType = getSingularDataObject(Order, id)
        serializer = OrderSerializer(userType)
        return Response(serializer.data)


class OrderStatusAPIView(APIView):
    """
    API endpoint that allows order statuses to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all order statuses to be viewed.
        """
        orderStatuses = OrderStatus.objects.all()
        serializer = OrderStatusSerializer(orderStatuses, many=True)
        return Response(serializer.data)


class NotificationAPIView(APIView):
    """
    API endpoint that allows notifications to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all notifications to be viewed.
        """
        notifications = Notification.objects.all()
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Endpoint method that allows a new notification to be created.
        """
        serializer = NotificationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TargetNotificationAPIView(APIView):
    """
    API endpoint that allows a notification to be viewed or edited.
    """

    def get(self, request, id):
        """
        Endpoint method that gets a database row by id.
        """
        userType = getSingularDataObject(Notification, id)
        serializer = NotificationSerializer(userType)
        return Response(serializer.data)


class MessageStatusAPIView(APIView):
    """
    API endpoint that allows message statuses to be viewed or created.
    """

    def get(self, request):
        """
        Endpoint method that allows all message statuses to be viewed.
        """
        messageStatuses = MessageStatus.objects.all()
        serializer = MessageStatusSerializer(messageStatuses, many=True)
        return Response(serializer.data)
