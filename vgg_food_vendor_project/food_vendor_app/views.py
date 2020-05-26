from os import getenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import jwt
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from datetime import datetime, timedelta
import pytz
from django.utils import timezone, timesince
from vgg_food_vendor_project.food_vendor_app.models import (
    Auth,
    Customer,
    Menu,
    MessageStatus,
    Notification,
    Order,
    OrderStatus,
    Vendor
)
from vgg_food_vendor_project.food_vendor_app.serializers import (
    AuthSerializer,
    CustomerSerializer,
    MenuSerializer,
    MessageStatusSerializer,
    NotificationSerializer,
    OrderSerializer,
    Order_OrderStatusSerializer,
    OrderStatusSerializer,
    VendorSerializer
)


#########################################################################################
# GLOBAL FUNCTIONS DEFINITION
#########################################################################################


# The base URL for this app


app_base_route = getenv('APP_BASE_ROUTE')


# Globally accessible functions


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

    if 'Authorization' not in request.headers.keys():
        return {'error': {
            'message': 'Log on to {}login to login'.format(app_base_route), 'status': status.HTTP_403_FORBIDDEN}}

    accessToken = request.headers['Authorization']

    try:
        userPayload = api_settings.JWT_DECODE_HANDLER(accessToken)
    except:
        return {
            'error': {'message': 'Log on to {}login to login'.format(app_base_route),
                      'status': status.HTTP_401_UNAUTHORIZED}
        }

    # Authorize user

    if userPayload['userType'] != userType:
        return {'error': {
            'message': 'Only {}s are allowed'.format(userType), 'status': status.HTTP_403_FORBIDDEN}}

    return userPayload


def getDefaultForeignKey(RelatedModel):
    try:
        relatedModel = RelatedModel.objects.values_list('id', flat=True)
    except RelatedModel.DoesNotExist:
        return {'error': {
            'message': 'Issue with related data. Contact us at mailto:help@fva.org to rectify this issue.', 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}}

    listOfPrimaryKeys = list(relatedModel)
    return listOfPrimaryKeys[0]


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
            'login/POST': '{}login/'.format(app_base_route),
            'vendor/GET-POST/': '{}vendor/'.format(app_base_route),
            'customer-signup/POST/': '{}customer/'.format(app_base_route),
            'token/refresh/POST': '{}token/refresh/'.format(app_base_route),

            # auth vendor
            'auth-vendor-menu/GET-POST/': '{}auth/vendor/menu/'.format(app_base_route),
            'auth-vendor-menu/GET-PUT-DELETE/': '{}auth/vendor/menu/1/'.format(app_base_route),
            'auth-vendor-order/GET/': '{}auth/vendor/order/'.format(app_base_route),
            'auth-vendor-order/GET-PATCH/order-status/': '{}auth/vendor/order/1/'.format(app_base_route),
            'auth-vendor-sales/GET/': '{}auth/vendor/sales/'.format(app_base_route),
            'auth-vendor-notification/POST/customer/': '{}auth/vendor/notification/<int:customer_id>/'.format(app_base_route),
            'auth-vendor-notification/GET/': '{}auth/vendor/notification/'.format(app_base_route),

            # public
            'get-all-menus/GET/': '{}menu/'.format(app_base_route),
            'get-all-menu-by-a-vendor/GET/': '{}vendor/1/menu/'.format(app_base_route),
            'get-a-menu/GET/': '{}menu/1/'.format(app_base_route),

            # auth customer
            'auth-customer-order/GET-POST/': '{}auth/customer/order/'.format(app_base_route),
            'notification/GET/': '{}auth/customer/notification/'.format(app_base_route),

            'get-a-vendor/': '{}vendor/1/'.format(app_base_route),
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
                'message': 'You are not registered on this FVA app. Log on to {}vendor/ to sign up as a vendor or {}customer/ to sign up as customer'.format(app_base_route)
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
                'message': 'No user profile matching this user. Contact us at mailto:help@fva.org to rectify this issue.'
            }, status=status.HTTP_404_NOT_FOUND)

        if vendor == None:
            customerSerializer = CustomerSerializer(customer)
            accessToken = self.generateToken(customerSerializer, 'customer')
            return Response(
                {'lastLogin': str(datetime.now()),
                 'data': customerSerializer.data},
                headers={
                    'Authorization': accessToken
                })

        if customer == None:
            vendorSerializer = VendorSerializer(vendor)
            accessToken = self.generateToken(vendorSerializer, 'vendor')
            return Response(
                {'lastLogin': str(datetime.utcnow()),
                 'data': vendorSerializer.data},
                headers={
                    'Authorization': accessToken
                })

        return Response({
            'message': 'Conflicting user profile. Contact us at mailto:help@fva.org to rectify this issue.'
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
    API endpoint that allows authorized vendor to create a food menu and view all his food menu.
    """

    def get(self, request):
        """
        API method that allows vendor to view all his food menu.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            menu = Menu.objects.filter(vendorId=userPayload['user_id'])
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

        if 'error' in userPayload.keys():
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
        menuRequestData['vendorId'] = userPayload['user_id']

        for k in menuRequestData.keys():
            if k in ['id', 'dateTimeCreated']:
                menuRequestData.pop(k)

        # Create the food menu

        menuSerializer = MenuSerializer(data=menuRequestData)

        if menuSerializer.is_valid():
            menuSerializer.save()
            return Response(menuSerializer.data, status=status.HTTP_201_CREATED)
        return Response(menuSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth vendor view a menu, update a menu, delete a menu


class AuthVendorMenuDetailAPIView(APIView):
    """
    API endpoint that allows authorized vendor to create a food menu and view a food menu.
    """

    def get(self, request, menu_id):
        """
        API method that allows authorized vendor to view a food menu.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
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
        API method that allows vendor update food menu.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
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

        for k in menuRequestData.keys():
            if k in ['id', 'dateTimeCreated']:
                menuRequestData.pop(k)

        # Get the required menu

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Update the food menu

        menuSerializer = MenuSerializer(menu, menuRequestData, partial=True)

        if menuSerializer.is_valid():
            menuSerializer.save()
            return Response(menuSerializer.data)
        return Response(menuSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, menu_id):
        """
        API method that allows a new food menu to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required food menu

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Delete the food menu

        menu.delete()
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_200_OK)


# auth vendor view orders


class AuthVendorOrderAPIView(APIView):
    """
    API endpoint that allows authorized vendor view all his food orders.
    """

    def get(self, request):
        """
        API method that allows authorized vendor to view all his food orders.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # check for vendors orders

        try:
            order = Order.objects.filter(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No orders have been made to you in a while'}, status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)


# auth vendor view an order, update order status


class AuthVendorOrderDetailAPIView(APIView):
    """
    API endpoint that allows vendor to create a food menu and view a food menu.
    """

    def get(self, request, order_id):
        """
        API method that allows vendor to view all food order.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.get(
                vendorId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found for user'}, status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(order)
        return Response(orderSerializer.data)

    def patch(self, request, order_id):
        """
        API method that allows a new food order to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required order

        try:
            order = Order.objects.get(
                vendorId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found for user'}, status=status.HTTP_404_NOT_FOUND)

        # check that order status exists in database

        try:
            orderStatus = OrderStatus.objects.get(
                id=request.data['orderStatus'])
        except:
            return Response({'message': 'Invalid order status'}, status=status.HTTP_404_NOT_FOUND)

        orderStatusSerializer = OrderStatusSerializer(orderStatus)

        orderStatusIdData = {'orderStatusId': orderStatusSerializer.data['id']}

        # Update the food order status

        orderSerializer = OrderSerializer(
            order, orderStatusIdData, partial=True)

        if orderSerializer.is_valid():
            orderSerializer.save()
            return Response(orderSerializer.data)
        return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth vendor view daily sales report


class AuthVendorSalesReportAPIView(APIView):
    """
    API endpoint that allows authorized vendor view daily sales report.
    """

    def get(self, request):
        """
        API method that allows authorized vendor to view daily sales report.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            orders = Order.objects.filter(
                vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        orderSerializer = OrderSerializer(orders, many=True)

        dateTimes = []

        for e in orderSerializer.data:
            if datetime.strptime(
                    e['dateAndTimeOfOrder'], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone().day == datetime.utcnow().astimezone().day:
                dateTimes.append(e)

        return Response(dateTimes)


# auth vendor view notifications, notify customer


class VendorNotificationAPIView(APIView):
    """
    API endpoint that allows authorized vendor view notifications, notify customer.
    """

    def get(self, request):
        """
        API method that allows authorized vendor to view notifications.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Check for orders associated with vendor

        try:
            orders = Order.objects.filter(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No foodorders for notifications to show'}, status=status.HTTP_400_BAD_REQUEST)

        orderSerializer = OrderSerializer(orders, many=True)
        response = []

        for e in orderSerializer.data:
            try:
                notifications = Notification.objects.filter(orderId=e['id'])
            except Notification.DoesNotExist:
                continue

            if notifications:
                # Notifications sorted grouped by order
                notificationSerializer = NotificationSerializer(
                    notifications, many=True)
                response.extend(notificationSerializer.data)

        if len(response) > 0:

            # Get message statues

            try:
                messageStatus = MessageStatus.objects.all()
            except MessageStatus.DoesNotExist:
                return Response({'message': 'An issue with our message status. Please contact'}, status=status.HTTP_400_BAD_REQUEST)

            messageStatusSerializer = MessageStatusSerializer(
                messageStatus, many=True)
            messageStatus = {}

            for e in messageStatusSerializer.data:
                messageStatus[e['id']] = e['name']

            for e in response:
                if e['messageStatusId'] in messageStatus.keys():
                    e['messageStatus'] = messageStatus[e['messageStatusId']]
                    e.pop('messageStatusId')
            return Response(response)
        return Response({'message': 'No notifications to show'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        API method that allows authorized vendor to send notification to customer.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        notificationRequestData = {**request.data}

        # Validate user input

        try:
            Order.objects.filter(
                vendorId=userPayload['user_id'], customerId=notificationRequestData['subjectUser'])
        except Order.DoesNotExist:
            return Response({'message': 'No recipient found for the given order'}, status=status.HTTP_404_NOT_FOUND)

        for k in notificationRequestData.keys():
            if k in ['id', 'dateTimeCreated']:
                notificationRequestData.pop(k)

        # Get message status name

        try:
            messageStatus = MessageStatus.objects.get(
                id=notificationRequestData['messageStatusId'])
        except MessageStatus.DoesNotExist:
            return Response({'message': 'Invalid message status'}, status=status.HTTP_400_BAD_REQUEST)

        messageStatuserializer = MessageStatusSerializer(messageStatus)

        # Send notification

        notificationSerializer = NotificationSerializer(
            data=notificationRequestData)

        if notificationSerializer.is_valid():
            notificationSerializer.save()
            response = {**notificationSerializer.data}
            response.pop('messageStatusId')
            response['messageStatus'] = messageStatuserializer.data['name']
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(notificationSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth vendor view notifications, notify customer


class VendorNotificationDetailAPIView(APIView):
    """
    API endpoint that allows authorized vendor view a notification.
    """

    def get(self, request, notification_id):
        """
        API method that allows authorized vendor to view a notification.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'vendor')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            orders = Order.objects.filter(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No notifications to show'}, status=status.HTTP_404_NOT_FOUND)

        orderSerializer = NotificationSerializer(orders, many=True)
        notificationResponse = []

        for k, v in orderSerializer.data.items():
            try:
                notification = Notification.objects.get(
                    orderId=v['id'], id=notification_id)
            except Notification.DoesNotExist:
                continue

            if notification:

                # Notifications grouped by order

                notificationSerializer = NotificationSerializer(notification)
                notificationResponse.append(notificationSerializer)

        if len(notificationResponse == 1):
            return Response(notificationResponse[0])
        if len(notificationResponse == 0):
            return Response({'message': 'No notification to show'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': 'Unexpected number of notifications'}, status=status.HTTP_400_BAD_REQUEST)


#########################################################################################
# VIEWS FOR AUTHENTICATED CUSTOMERS
#########################################################################################


# auth customer view orders, create order


class AuthCustomerOrderAPIView(APIView):
    """
    API endpoint that allows auhtorized customer to create a food order and view all his food order.
    """

    def get(self, request):
        """
        API method that allows authorized customer to view all his food orders.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.filter(customerId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'You have not made any order recently'}, status=status.HTTP_204_NO_CONTENT)

        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)

    def post(self, request):
        """
        API method that allows customer create a new food order from available food menu.
        Customer can preoroder with the preorder date
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # validate user input

        orderRequestData = {**request.data}

        for k in orderRequestData.keys():
            if k in ['id', 'dateAndTimeOfOrder']:
                orderRequestData.pop(k)

        if 'description' in orderRequestData.keys() and len(orderRequestData['description']) < 5:
            orderRequestData.pop('description')

        if 'preOrderDateTime' in orderRequestData.keys():
            if len(orderRequestData['preOrderDateTime']) == 0:
                orderRequestData.pop('preOrderDateTime')
            elif len(orderRequestData['preOrderDateTime']) < 13:
                return Response({'message': 'Wrong date/time format. yyyy-mm-dd-hh'}, status.HTTP_400_BAD_REQUEST)

        orderRequestData['customerId'] = userPayload['user_id']

        # Check for order status

        orderStatusId = getDefaultForeignKey(OrderStatus)

        try:
            if orderStatusId['error']:
                return Response({'message': orderStatusId['error']['message']
                                 }, status=orderStatusId['error']['status'])
        except:
            pass

        orderRequestData['orderStatusId'] = orderStatusId

        # check that menu exists

        amountDue = 0

        for menuId in orderRequestData['itemsOrdered']:
            try:
                menu = Menu.objects.get(
                    vendorId=orderRequestData['vendorId'], id=menuId)
            except Menu.DoesNotExist:
                return Response({'message': 'The selected menu ({}) is not available for order'.format(menuId)}, status.HTTP_404_NOT_FOUND)

            menuSerializer = MenuSerializer(menu)
            amountDue += menuSerializer.data['price']

        orderRequestData['amountDue'] = amountDue
        orderRequestData['amountOutstanding'] = amountDue

        # handle pre-orders

        if 'preOrderDateTime' in orderRequestData.keys():

            try:
                orderRequestData['preOrderDateTime'] = datetime.strptime(
                    orderRequestData['preOrderDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(tz=pytz.utc)
            except:
                return Response({'message': 'Invalid date/time format => yyyy-mm-ddThh:mm:ss.ffffffZ'}, status.HTTP_400_BAD_REQUEST)

            currentDateTime = datetime.utcnow().astimezone(tz=pytz.utc)

            if (orderRequestData['preOrderDateTime'] - currentDateTime).seconds < 18000 or (orderRequestData['preOrderDateTime'] - currentDateTime).days > 3:
                return Response({'message': 'Unacceptable pre-order. Pre-order is valid between 5 hours and 3 days after the order is placed'}, status.HTTP_400_BAD_REQUEST)

        # Create the food order

        orderSerializer = OrderSerializer(data=orderRequestData)

        if orderSerializer.is_valid():
            orderSerializer.save()
            return Response(orderSerializer.data, status=status.HTTP_201_CREATED)
        return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth customer view an order, delete (cancel) an order


class AuthCustomerOrderDetailAPIView(APIView):
    """
    API endpoint that allows authorized customer view a food order and delete (cancel) a food order.
    """

    def get(self, request, order_id):
        """
        API method that allows customer to view a food order.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            order = Order.objects.get(
                customerId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found for user'}, status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(order)
        return Response(orderSerializer.data)

    def delete(self, request, order_id):
        """
        API method that allows a new food order to be created.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # Get the required food order

        try:
            order = Order.objects.get(
                customerId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found for user'}, status=status.HTTP_404_NOT_FOUND)

        # validate status to cancel order

        orderSerializer = OrderSerializer(order)

        if orderSerializer.data['orderStatusId'] > 2:
            return Response({'message': 'Processed order cannot be cancelled'}, status.HTTP_400_BAD_REQUEST)

        # Cancel the food order

        order.delete()
        return Response({'message': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


# auth customer view an order, delete (cancel) an order


class AuthCustomerOrderPaymentAPIView(APIView):
    """
    API endpoint that allows authorized customer pay for a food order.
    """

    def patch(self, request, order_id):
        """
        API method that allows authorized customer pay for a food order.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        # validate user input

        if 'amountPaid' not in request.data.keys() or type(request.data['amountPaid']) not in [int, float] or request.data['amountPaid'] <= 0:
            return Response({'message': 'Invalid data type. Amount must be a positive non-zero number'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the required order

        try:
            order = Order.objects.get(
                customerId=userPayload['user_id'], id=order_id)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found for user'}, status=status.HTTP_404_NOT_FOUND)

        # process payment

        orderSerializer = OrderSerializer(order)
        orderProcessData = {}
        orderProcessData['amountPaid'] = orderSerializer.data['amountPaid'] + \
            request.data['amountPaid']
        orderProcessData['amountOutstanding'] = orderSerializer.data['amountDue'] - \
            orderProcessData['amountPaid']

        # Update the food order amount paid and amount outstanding

        orderSerializer = OrderSerializer(
            order, orderProcessData, partial=True)

        if orderSerializer.is_valid():
            orderSerializer.save()
            return Response(orderSerializer.data)
        return Response(orderSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


# auth customer view notifications, notify customer


class CustomerNotificationAPIView(APIView):
    """
    API endpoint that allows authorized customer view notifications, notify customer.
    """

    def get(self, request):
        """
        API method that allows authorized customer to view notifications.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            notifications = Notification.objects.filter(
                subjectUser=userPayload['user_id'])
        except Notification.DoesNotExist:
            return Response({'message': 'No notifications to show'}, status=status.HTTP_400_BAD_REQUEST)

        notificationSerializer = NotificationSerializer(
            notifications, many=True)

        return Response(notificationSerializer.data)


# auth customer view notifications


class CustomerNotificationDetailAPIView(APIView):
    """
    API endpoint that allows authorized customer view a notification.
    """

    def get(self, request, notification_id):
        """
        API method that allows authorized customer to view a notification.
        """

        # Authenticate/Authorize user

        userPayload = userAuthProcess(request, 'customer')

        if 'error' in userPayload.keys():
            return Response({'message': userPayload['error']['message']
                             }, status=userPayload['error']['status'])

        try:
            notification = Notification.objects.get(
                subjectUser=userPayload['user_id'], id=notification_id)
        except Notification.DoesNotExist:
            return Response({'message': 'No notification to show'}, status=status.HTTP_400_BAD_REQUEST)

        notificationSerializer = NotificationSerializer(notification)

        return Response(notificationSerializer.data)


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
            menu = Menu.objects.filter(vendorId=vendor_id)
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
