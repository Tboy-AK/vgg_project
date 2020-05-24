from os import getenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import datetime
from vgg_food_vendor_project.food_vendor_app.models import Auth, Customer, Menu, MessageStatus, Notification, Order, OrderStatus, Vendor
from vgg_food_vendor_project.food_vendor_app.serializers import AuthSerializer, CustomerSerializer, MenuSerializer, MessageStatusSerializer, NotificationSerializer, OrderSerializer, Order_OrderStatusSerializer, OrderStatusSerializer, VendorSerializer


#########################################################################################
# GLOBAL FUNCTIONS DEFINITION
#########################################################################################


def getDataById(relationalModel, relationId, modelSerializer):
    """
    Function that gets data by id.
    """

    try:
        relationObject = relationalModel.objects.get(id=relationId)
    except relationalModel.DoesNotExist:
        return None

    return modelSerializer(relationObject)


def userAuthProcess(request, userType):
    """
    Function that handles both authentication and authorization of users.
    """

    # Authenticate user

    accessToken = request.headers['Authorization']

    if not accessToken:
        return {'error': {
            'message': '', 'status': status.HTTP_403_FORBIDDEN}}

    try:
        userPayload = api_settings.JWT_DECODE_HANDLER(accessToken)
    except:
        return {
            'error': {'message': 'Log on to {}/login to login'.format(request.META['HTTP_HOST']),
                      'status': status.HTTP_401_UNAUTHORIZED}
        }

    # Authorize user

    if userPayload['userType'] != userType:
        return {'error': {
            'message': '', 'status': status.HTTP_403_FORBIDDEN}}

    return userPayload


def filterDataArrayById(dataArray, id):
    """
    Function that gets an object from an array by Id.
    """

    for dataObject in dataArray:
        if dataObject['id'] == id:
            return dataObject

    return Response(status=status.HTTP_404_NOT_FOUND)


#########################################################################################
# LANDING VIEW
#########################################################################################


class HomeDescAPIView(APIView):
    """
    API endpoint that gives a summarised description of the app.
    """

    def get(self, request):
        """
        API method that allows all vendors to be viewed.
        """

        return Response({
            # authentication
            'login/POST': '{}login/'.format(request.META['HTTP_HOST']),
            'vendor/GET-POST/': '{}vendor/'.format(request.META['HTTP_HOST']),
            'customer-signup/POST/': '{}customer/'.format(request.META['HTTP_HOST']),
            'token/refresh/POST': '{}token/refresh/'.format(request.META['HTTP_HOST']),

            # auth vendor
            'auth-vendor-menu/GET-POST/': '{}auth/vendor/menu/'.format(request.META['HTTP_HOST']),
            'auth-vendor-menu/GET-PUT-DELETE/': '{}auth/vendor/menu/1/'.format(request.META['HTTP_HOST']),
            'auth-vendor-order/GET/': '{}auth/vendor/order/'.format(request.META['HTTP_HOST']),
            'auth-vendor-order/GET-PATCH/order-status/': '{}auth/vendor/order/1/'.format(request.META['HTTP_HOST']),
            'auth-vendor-sales/GET/': '{}auth/vendor/sales/'.format(request.META['HTTP_HOST']),
            'auth-vendor-notification/POST/customer/': '{}auth/vendor/notification/<int:customer_id>/'.format(request.META['HTTP_HOST']),
            'auth-vendor-notification/GET/': '{}auth/vendor/notification/'.format(request.META['HTTP_HOST']),

            # public
            'get-all-menus/GET/': '{}menu/'.format(request.META['HTTP_HOST']),
            'get-all-menu-by-a-vendor/GET/': '{}vendor/1/menu/'.format(request.META['HTTP_HOST']),
            'get-a-menu/GET/': '{}menu/1/'.format(request.META['HTTP_HOST']),

            # auth customer
            'auth-customer-order/GET-POST/': '{}auth/customer/order/'.format(request.META['HTTP_HOST']),
            'notification/GET/': '{}auth/customer/notification/'.format(request.META['HTTP_HOST']),

            'get-a-vendor/': '{}vendor/1/'.format(request.META['HTTP_HOST']),
        })


#########################################################################################
# AUTHENTICATE APP USERS
#########################################################################################


# user login
class LoginAPIView(APIView):
    """
    API endpoint that allows users to log in.
    """

    def generateToken(self, modelSerializer, userType):
        userObject = {'username': modelSerializer.data['email'],
                      'pk': modelSerializer.data['id'],
                      'userType': userType,
                      }
        tokenPayload = api_settings.JWT_PAYLOAD_HANDLER(userObject)
        return api_settings.JWT_ENCODE_HANDLER(tokenPayload)

    def post(self, request):
        """
        API method that allows a user to log in.
        """

        # check that user is signed up

        try:
            authUser = Auth.objects.get(
                email=request.data['email'])
        except Auth.DoesNotExist:
            return Response({
                'message': 'You are not registered on this FVA app. Log on to {}vendor/ to sign up as a vendor or {}customer/ to sign up as customer'.format(request.META['HTTP_HOST'])
            }, status=status.HTTP_401_UNAUTHORIZED)

        # authenticate user

        try:
            authUser = Auth.objects.get(
                email=request.data['email'], password=request.data['password'])
        except Auth.DoesNotExist:
            return Response({
                'message': 'Wrong username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AuthSerializer(authUser)
        userId = serializer.data['id']

        # confirm user profile

        try:
            vendor = Vendor.objects.get(email=request.data['email'])
        except Vendor.DoesNotExist:
            vendor = None

        try:
            customer = Customer.objects.get(email=request.data['email'])
        except Customer.DoesNotExist:
            customer = None

        # process response

        if vendor == None and customer == None:
            return Response({
                'message': 'No user profile matching this user. Contact us at help@fva.org to rectify this issue.'
            }, status=status.HTTP_404_NOT_FOUND)

        if vendor == None:
            customerSerializer = CustomerSerializer(customer)
            accessToken = self.generateToken(customerSerializer, 'customer')
            return Response(
                {'lastLogin': str(datetime.datetime.utcnow()),
                 'data': customerSerializer.data},
                headers={
                    'Authorization': accessToken
                })

        if customer == None:
            vendorSerializer = VendorSerializer(vendor)
            accessToken = self.generateToken(vendorSerializer, 'vendor')
            return Response(
                {'lastLogin': str(datetime.datetime.utcnow()),
                 'data': vendorSerializer.data},
                headers={
                    'Authorization': accessToken
                })

        return Response({
            'message': 'Conflicting user profile. Contact us at help@fva.org to rectify this issue.'
        }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


# vendor view, vendor sign up
class VendorAPIView(APIView):
    """
    API endpoint that allows vendors to be viewed.
    """

    def get(self, request):
        """
        API method that allows all vendors to be viewed.
        """

        vendors = Vendor.objects.all()
        vendorSerializer = VendorSerializer(vendors, many=True)
        return Response(vendorSerializer.data)

    def post(self, request):
        """
        API method that allows a new vendor to be created.
        """

        # register user

        authSerializer = AuthSerializer(data=request.data)

        if authSerializer.is_valid():

            # create user profile

            vendorSerializer = VendorSerializer(data=request.data)

            if vendorSerializer.is_valid():
                authSerializer.save()
                vendorSerializer.save()
                return Response(vendorSerializer.data, status=status.HTTP_201_CREATED)
            return Response(vendorSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(authSerializer.errors, status=status.HTTP_404_NOT_FOUND)


# customer-signup
class CustomerAPIView(APIView):
    """
    API endpoint that allows a customer to be viewed or edited.
    """

    def post(self, request):
        """
        API method that allows a new customer to be created.
        """

        # register user

        authSerializer = AuthSerializer(data=request.data)

        if authSerializer.is_valid():

            # create user profile

            customerSerializer = CustomerSerializer(data=request.data)

            if customerSerializer.is_valid():
                authSerializer.save()
                customerSerializer.save()
                return Response(customerSerializer.data, status=status.HTTP_201_CREATED)
            return Response(customerSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(authSerializer.errors, status=status.HTTP_404_NOT_FOUND)


#########################################################################################
# VIEWS FOR AUTHENTICATED VENDORS
#########################################################################################


# auth vendor view menu, create menu
class AuthVendorMenuAPIView(APIView):
    """
    API endpoint that allows vendor to create a food menu and view all authorized food menu.
    """

    def get(self, request):
        """
        API method that allows vendor to view all food menu.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            menu = Menu.objects.get(vendorId=userPayload['user_id'])
        except Menu.DoesNotExist:
            return Response({'message': 'You have not created any food menu recently'}, status=status.HTTP_204_NO_CONTENT)

        menuSerializer = MenuSerializer(menu, many=True)
        return Response(menuSerializer.data)

    def post(self, request):
        """
        API method that allows a new food menu to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # validate input data

        if request.data['isRecurring'] == True and len(request.data['frequencyOfReoccurrence']) < 1:
            return Response({'message': 'Frequency of re-occurrence must be stated if menu re-occurs'
                             }, status=status.HTTP_400_BAD_REQUEST)

        if request.data['isRecurring'] == False and len(request.data['frequencyOfReoccurrence']) > 0:
            return Response({'message': 'Frequency of re-occurrence must be nil if menu does not re-occur'
                             }, status=status.HTTP_400_BAD_REQUEST)

        # Create the food menu

        menuRequestData = {**request.data}
        menuRequestData['vendorId'] = userPayload['user_id']

        menuSerializer = MenuSerializer(data=menuRequestData)

        if menuSerializer.is_valid():
            menuSerializer.save()
            return Response(menuSerializer.data, status=status.HTTP_201_CREATED)
        return Response(menuSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth vendor view a menu, update a menu, delete a menu
class AuthVendorMenuDetailAPIView(APIView):
    """
    API endpoint that allows vendor to create a food menu and view all authorized food menu.
    """

    def get(self, request, menu_id):
        """
        API method that allows vendor to view all food menu.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        menuSerializer = MenuSerializer(menu)
        return Response(menuSerializer.data)

    def put(self, request, menu_id):
        """
        API method that allows a new food menu to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # validate input data

        if request.data['isRecurring'] == True and len(request.data['frequencyOfReoccurrence']) < 1:
            return Response({'message': 'Frequency of re-occurrence must be stated if menu re-occurs'
                             }, status=status.HTTP_400_BAD_REQUEST)

        if request.data['isRecurring'] == False and len(request.data['frequencyOfReoccurrence']) > 0:
            return Response({'message': 'Frequency of re-occurrence must be nil if menu does not re-occur'
                             }, status=status.HTTP_400_BAD_REQUEST)

        menuRequestData = {**request.data}

        for k in menuRequestData.items():
            if k in ['id', 'dateTimeCreated', 'vendorId']:
                menuRequestData.pop(k)

        # Get the required menu

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Update the food menu

        menuSerializer = MenuSerializer(menu, menuRequestData)

        if menuSerializer.is_valid():
            menuSerializer.save()
            return Response(menuSerializer.data, status=status.HTTP_200_OK)
        return Response(menuSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, menu_id):
        """
        API method that allows a new food menu to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required food menu

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Delete the food menu

        menu.delete()
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)


# auth vendor view orders
class AuthVendorOrderAPIView(APIView):
    """
    API endpoint that allows authorized vendors view all authorized food order.
    """

    def get(self, request):
        """
        API method that allows customer to view all food orders.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # check for vendors orders

        try:
            order = Order.objects.get(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No orders have been made to you in a while'}, status=status.HTTP_204_NO_CONTENT)

        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)


# auth vendor view an order, update order status
class AuthVendorOrderDetailAPIView(APIView):
    """
    API endpoint that allows vendor to create a food menu and view all authorized food menu.
    """

    def get(self, request, order_id):
        """
        API method that allows vendor to view all food order.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.get(
                vendorId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(order)
        return Response(orderSerializer.data)

    def put(self, request, order_id):
        """
        API method that allows a new food order to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required order

        try:
            order = Order.objects.get(
                vendorId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # check that order status exists in database

        try:
            orderStatus = OrderStatus.objects.get(
                name=request.data['orderStatus'])
        except OrderStatus.DoesNotExist:
            return Response({'message': 'Invalid order status'}, status=status.HTTP_404_NOT_FOUND)

        orderStatusIdData = {'orderStatusId': orderStatus['id']}

        # Update the food order

        orderSerializer = OrderSerializer(order, orderStatusIdData)

        if orderSerializer.is_valid():
            orderSerializer.save()
            return Response(orderSerializer.data, status=status.HTTP_200_OK)
        return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


#########################################################################################
# VIEWS FOR AUTHENTICATED CUSTOMERS
#########################################################################################


# auth customer view orders, create order
class AuthCustomerOrderAPIView(APIView):
    """
    API endpoint that allows customer to create a food order and view all authorized food order.
    """

    def get(self, request):
        """
        API method that allows customer to view all food orders.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.get(customerId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'You have not made any order recently'}, status=status.HTTP_204_NO_CONTENT)

        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)

    def post(self, request):
        """
        API method that allows a new food order to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Create the food order

        orderRequestData = {**request.data}
        orderRequestData['customerId'] = userPayload['user_id']

        orderSerializer = OrderSerializer(data=orderRequestData)

        if orderSerializer.is_valid():
            orderSerializer.save()
            return Response(orderSerializer.data, status=status.HTTP_201_CREATED)
        return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth customer view a order, delete a order
class AuthCustomerMenuDetailAPIView(APIView):
    """
    API endpoint that allows authorized customer get a food order and delete a food order.
    """

    def get(self, request, order_id):
        """
        API method that allows customer to view a food order.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.get(
                customerId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(order)
        return Response(orderSerializer.data)

    def delete(self, request, order_id):
        """
        API method that allows a new food order to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if userPayload['error']:
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required food order

        try:
            order = Order.objects.get(
                customerId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Cancel the food order

        order.delete()
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)


#########################################################################################
# OTHER USEFUL VIEWS
#########################################################################################


# get-all-menu
class MenuAPIView(APIView):
    """
    API endpoint that allows all food menu to be viewed.
    """

    def get(self, request):
        """
        Function that gets all food menu.
        """

        menu = Menu.objects.all()
        menuSerializer = MenuSerializer(menu, many=True)
        return Response(menuSerializer.data)


# get-all-menu-from-a-vendor
class VendorMenuAPIView(APIView):
    """
    API endpoint that publicly allows all food menu of a vendor to be viewed.
    """

    def get(self, request, vendor_id):
        """
        Function that gets all menu by vendor id.
        """

        try:
            menu = Menu.objects.get(vendorId=vendor_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        menuSerializer = MenuSerializer(menu, many=True)
        return Response(menuSerializer.data)


# get-a-menu
class MenuDetailAPIView(APIView):
    """
    API endpoint that allows a specific food menu to be viewed.
    """

    def get(self, request, menu_id):
        """
        Function that gets menu by id.
        """

        menu = getDataById(Menu, menu_id, MenuSerializer)

        if menu == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(menu.data)


# get-a-vendor
class VendorDetailAPIView(APIView):
    """
    API endpoint that allows a vendor to be viewed.
    """

    def get(self, request, vendor_id):
        """
        API method that gets a database row by id.
        """

        vendor = getDataById(Vendor, vendor_id, VendorSerializer)

        if vendor == None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(vendor.data)
