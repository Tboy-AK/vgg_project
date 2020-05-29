from os import getenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from datetime import datetime, timedelta
import pytz
import bcrypt
import re as regex
from phonenumbers import (
    parse as phoneparse,
    is_valid_number,
    format_number as format_phone,
    PhoneNumberFormat,
)
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


class EnsureRequiredFields():
    def __init__(self, requiredInputFields=[], requestFields=[]):
        """
        Function that checks for required input fields and returns an error dictionary if one is missing
        """

        for e in requestFields:
            if e in requiredInputFields:
                requiredInputFields.pop(requiredInputFields.index(e))

        if len(requiredInputFields) != 0:
            self.requiredInputFields = requiredInputFields
            self.error = {'message': 'Required fields missing',
                          'missing-fields': self.requiredInputFields,
                          'status': status.HTTP_403_FORBIDDEN}

    def errorResponse(self):
        """
        Response to be called in the case of an error.
        """
        return Response({'message': self.error['message'],
                         'missing-fields': self.error['missing-fields'],
                         }, status=self.error['status'])


def protectRestrictedInput(requestData={}):
    """
    Function that removes special keys from the initial request dictionary and returns a sanitized request dictioinary
    """

    for k in requestData.keys():
        if k in ['id', 'dateTimeCreated', 'dateTimeModified', 'dateAndTimeOfOrder']:
            requestData.pop(k)
            continue
        if type(requestData[k]) == str:
            requestData[k].strip()
    return requestData


class SanitizePassword():
    def __init__(self, password):
        '''
        Function to validate user password.
        '''

        self.password = password

        if len(password) < 8:
            self.error = {'message': 'Password must have at least 8 characters',
                          'status': status.HTTP_400_BAD_REQUEST}

        passwordHasNumber = False
        for intChar in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if intChar in password:
                passwordHasNumber = True
                break
        if passwordHasNumber == False:
            self.error = {'message': 'Password must have at least a number',
                          'status': status.HTTP_400_BAD_REQUEST}

        passwordHasLowerCase = False
        for intChar in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
            if intChar in password:
                passwordHasLowerCase = True
                break
        if passwordHasLowerCase == False:
            self.error = {'message': 'Password must be alphanumeric with lower and upper case characters',
                          'status': status.HTTP_400_BAD_REQUEST}

        passwordHasHigherCase = False
        for intChar in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            if intChar in password:
                passwordHasHigherCase = True
                break
        if passwordHasHigherCase == False:
            self.error = {'message': 'Password must be alphanumeric with lower and upper case characters',
                          'status': status.HTTP_400_BAD_REQUEST}

    def passwordError(self):
        '''
        Response to be called in the case of an error.
        '''
        return Response({'message': self.error['message']
                         }, status=self.error['status'])

    def hashPassword(self):
        '''
        Function to hash valid user password.
        '''
        encodedPassword = self.password.encode('utf-8')
        return bcrypt.hashpw(
            encodedPassword, bcrypt.gensalt())


def getDataById(relationalModel, relationId, modelSerializer):
    """
    Function that gets data by id.
    """

    try:
        relationObject = relationalModel.objects.get(id=relationId)
    except relationalModel.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(modelSerializer(relationObject).data)


class UserAuthProcess():
    def __init__(self, request, userType):
        """
        Function that handles both authentication and authorization of users.
        """

        # Authenticate user

        if 'FVA-USER' not in request.COOKIES.keys():
            self.error = {'message': 'Log on to {}login to login'.format(app_base_route),
                          'status': status.HTTP_403_FORBIDDEN}

        accessToken = request.COOKIES.get('FVA-USER')

        try:
            userPayload = api_settings.JWT_DECODE_HANDLER(accessToken)
        except:
            self.error = {'message': 'Log on to {}login to login'.format(app_base_route),
                          'status': status.HTTP_401_UNAUTHORIZED}

        # Authorize user

        for k, v in userPayload.items():
            if type(v) == list:
                userPayload[k] = v[0]

        if userPayload['username'] != userType:
            self.error = {'message': 'Only {}s are allowed'.format(userType),
                          'status': status.HTTP_403_FORBIDDEN}

        self.userPayload = userPayload

    def errorResponse(self):
        """
        Response to be called in the case of an error.
        """
        return Response({'message': self.error['message']
                         }, status=self.error['status'])


class getDefaultForeignKey():
    def __init__(self, RelatedModel):
        try:
            relatedModel = RelatedModel.objects.values_list('id', flat=True)
        except RelatedModel.DoesNotExist:
            self.error = {'message': 'Issue with related data. Contact us at mailto:help@fva.org to rectify this issue.',
                          'status': status.HTTP_500_INTERNAL_SERVER_ERROR}

        self.defaultForeignKey = list(relatedModel)[0]

    def errorResponse(self):
        return Response({'message': self.error['message']
                         }, status=self.error['status'])


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

            # auth vendor
            'auth-vendor-menus/GET-POST/': '{}auth/vendor/menu/'.format(app_base_route),
            'auth-vendor-menu/GET-PUT-DELETE/': '{}auth/vendor/menu/1/'.format(app_base_route),
            'auth-vendor-orders/GET/': '{}auth/vendor/order/'.format(app_base_route),
            'auth-vendor-order/GET-PATCH/order-status/': '{}auth/vendor/order/1/'.format(app_base_route),
            'auth-vendor-sales/GET/': '{}auth/vendor/sales/daily/'.format(app_base_route),
            'auth-vendor-notifications/GET-POST/customer/': '{}auth/vendor/notification/'.format(app_base_route),
            'auth-vendor-notification/GET/': '{}auth/vendor/notification/1/'.format(app_base_route),

            # public
            'get-all-menus/GET/': '{}menu/'.format(app_base_route),
            'get-all-menu-by-a-vendor/GET/': '{}vendor/1/menu/'.format(app_base_route),
            'get-a-menu/GET/': '{}menu/1/'.format(app_base_route),

            # auth customer
            'auth-customer-orders/GET-POST/': '{}auth/customer/order/'.format(app_base_route),
            'auth-customer-order/GET-DELETE/': '{}auth/customer/order/1'.format(app_base_route),
            'auth-customer-payment/PATCH/': '{}auth/customer/order/payment/1'.format(app_base_route),
            'customer-notifications/GET/': '{}auth/customer/notification/'.format(app_base_route),
            'customer-notification/GET/': '{}auth/customer/notification/1'.format(app_base_route),
        })


#########################################################################################
# AUTHENTICATE APP USERS
#########################################################################################


# user login


class LoginAPIView(APIView):
    """
    API endpoint that allows users to log in.
    """

    class userAuth():
        def __init__(self, modelSerializer, userType):
            """
            An object of essential details user details
            """

            self.username = userType,
            self.email = modelSerializer.data['email'],
            self.pk = modelSerializer.data['id'],
            self.userType = userType

    def generateToken(self, modelSerializer, userType):
        userObject = self.userAuth(modelSerializer, userType)
        tokenPayload = api_settings.JWT_PAYLOAD_HANDLER(userObject)
        return api_settings.JWT_ENCODE_HANDLER(tokenPayload)

    def post(self, request):
        """
        API method that allows a user to log in.
        """

        # validate user input

        requestData = {**request.data}

        requiredFields = EnsureRequiredFields(
            ['email', 'password'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        # check that user is signed up

        try:
            authUser = Auth.objects.get(
                email=requestData['email'])
        except Auth.DoesNotExist:
            return Response({
                'message': 'Wrong username or password. Log on to {}vendor/ to sign up as a vendor or {}customer/ to sign up as customer'.format(app_base_route, app_base_route)
            }, status=status.HTTP_401_UNAUTHORIZED)

        # confirm password

        authSerializer = AuthSerializer(authUser)

        if not bcrypt.checkpw(requestData['password'].encode('utf-8'), authSerializer.data['password']):
            return Response({
                'message': 'Wrong username or password. Ensure your email and password are correct'.format(app_base_route, app_base_route)
            }, status=status.HTTP_401_UNAUTHORIZED)

        # confirm user profile

        try:
            vendor = Vendor.objects.get(email=requestData['email'])
        except Vendor.DoesNotExist:
            try:
                customer = Customer.objects.get(email=requestData['email'])
            except Customer.DoesNotExist:
                return Response({
                    'message': 'No user profile matching this user. Contact us at mailto:help@fva.org to rectify this issue.'
                }, status=status.HTTP_404_NOT_FOUND)

        # process response

        if vendor:
            vendorSerializer = VendorSerializer(vendor)
            accessToken = self.generateToken(vendorSerializer, 'vendor')
            return Response(
                {'latestLogin': str(datetime.utcnow()),
                 'exp': '20-hrs',
                 'data': vendorSerializer.data},
                headers={
                    'Set-Cookie': 'FVA-USER={}; domain={}; path=/api/auth; max-age=72000; HttpOnly'.format(accessToken, getenv('APP_DOMAIN_NAME'))
                })

        if customer:
            customerSerializer = CustomerSerializer(customer)
            accessToken = self.generateToken(customerSerializer, 'customer')
            return Response(
                {'latestLogin': str(datetime.utcnow()),
                 'exp': '20-hrs',
                 'data': customerSerializer.data},
                headers={
                    'Set-Cookie': 'FVA-USER={}; domain={}; path=/api/auth; max-age=72000; HttpOnly'.format(accessToken, getenv('APP_DOMAIN_NAME'))
                })

        return Response({
            'message': 'Conflicting user profile? Contact us at mailto:tobia807@gmail.com.'
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

        # validate user input

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(
            ['businessName', 'email', 'phoneNumber', 'password'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        emailFormat = '^[a-z0-9]+[\._]?[a-za-z0-9]+[@]\w+[.]\w{2,3}$'
        if not regex.search(emailFormat, requestData['email']):
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        phone = phoneparse(requestData['phoneNumber'], 'NG')
        if not is_valid_number(phone):
            return Response({'message': 'Phone number must be valid Nigerian number'}, status=status.HTTP_400_BAD_REQUEST)
        requestData['phoneNumber'] = format_phone(
            phone, PhoneNumberFormat.E164)

        validPassword = SanitizePassword(requestData['password'])
        try:
            if validPassword.error:
                return validPassword.passwordError()
        except:
            pass
        requestData['password'] = validPassword.hashPassword()

        # register user

        authSerializer = AuthSerializer(data=requestData)

        if authSerializer.is_valid():

            # create user profile

            vendorSerializer = VendorSerializer(data=requestData)

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

        # validate user input

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(
            ['firstname', 'lastname', 'email', 'phoneNumber', 'password'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        emailFormat = '^[a-z0-9]+[\._]?[a-za-z0-9]+[@]\w+[.]\w{2,3}$'
        if not regex.search(emailFormat, requestData['email']):
            return Response({'message': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

        phone = phoneparse(requestData['phoneNumber'], 'NG')
        if not is_valid_number(phone):
            return Response({'message': 'Phone number must be valid Nigerian number'}, status=status.HTTP_400_BAD_REQUEST)
        requestData['phoneNumber'] = format_phone(
            phone, PhoneNumberFormat.E164)

        validPassword = SanitizePassword(requestData['password'])
        try:
            if validPassword.error:
                return validPassword.passwordError()
        except:
            pass
        requestData['password'] = validPassword.hashPassword()

        # register user

        authSerializer = AuthSerializer(data=requestData)

        if authSerializer.is_valid():

            # create user profile

            customerSerializer = CustomerSerializer(data=requestData)

            if customerSerializer.is_valid():
                authSerializer.save()
                customerSerializer.save()
                return Response(customerSerializer.data, status=status.HTTP_201_CREATED)
            return Response(customerSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(authSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # validate input data

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(['name', 'price', 'quantity', 'unit',
                                               'isRecurring', 'frequencyOfReoccurrence'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        if 'description' in requestData.keys() and len(requestData['description']) < 5:
            requestData.pop('description')

        if requestData['isRecurring'] == True and len(requestData['frequencyOfReoccurrence']) < 1:
            return Response({'message': 'Frequency of re-occurrence must be stated if menu re-occurs'
                             }, status=status.HTTP_400_BAD_REQUEST)

        if requestData['isRecurring'] == False and len(requestData['frequencyOfReoccurrence']) > 0:
            return Response({'message': 'Frequency of re-occurrence must be nil if menu does not re-occur'
                             }, status=status.HTTP_400_BAD_REQUEST)

        requestData['vendorId'] = userPayload['user_id']

        # Create the food menu

        menuSerializer = MenuSerializer(data=requestData)

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # validate input data

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(['name', 'price', 'quantity', 'unit',
                                               'isRecurring', 'frequencyOfReoccurrence'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        if 'description' in requestData.keys() and len(requestData['description']) < 5:
            requestData.pop('description')

        if requestData['isRecurring'] == True and len(requestData['frequencyOfReoccurrence']) < 1:
            return Response({'message': 'Frequency of re-occurrence must be stated if menu re-occurs'
                             }, status=status.HTTP_400_BAD_REQUEST)

        if requestData['isRecurring'] == False and len(requestData['frequencyOfReoccurrence']) > 0:
            return Response({'message': 'Frequency of re-occurrence must be nil if menu does not re-occur'
                             }, status=status.HTTP_400_BAD_REQUEST)

        # Get the required menu

        try:
            menu = Menu.objects.get(
                vendorId=userPayload['user_id'], id=menu_id)
        except Menu.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Update the food menu

        menuSerializer = MenuSerializer(menu, requestData, partial=True)

        if menuSerializer.is_valid():
            menuSerializer.save()
            return Response(menuSerializer.data)
        return Response(menuSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, menu_id):
        """
        API method that allows a new food menu to be created.
        """

        # Authenticate/Authorize user

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # Check through orders to extract vital info for the sales report

        try:
            orders = Order.objects.filter(
                vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        orderSerializer = OrderSerializer(orders, many=True)

        ordersOfTheDay = []

        # Extract only orders for the last 24hrs
        today = datetime.now()
        midnight = datetime(today.year, today.month,
                            today.day, 0, 0, 0, 0, tzinfo=pytz.utc)
        for e in orderSerializer.data:
            if (midnight - datetime.strptime(
                    e['dateAndTimeOfOrder'], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(tz=pytz.utc)).days == 0:
                ordersOfTheDay.append(e)

        responseData = {'salesList': [],
                        'totalAmountAtHand': 0,
                        'totalAmountOutstanding': 0,
                        'expectedSalesForTheDay': 0,
                        }

        for e in ordersOfTheDay:
            salesDetail = {}
            salesDetail['dateAndTimeOfOrder'] = e['dateAndTimeOfOrder']
            salesDetail['amountAtHand'] = e['amountPaid']
            salesDetail['amountOutstanding'] = e['amountOutstanding']
            salesDetail['customerId'] = e['customerId']
            salesDetail['orderId'] = e['id']
            responseData['salesList'].append(salesDetail)
            responseData['totalAmountAtHand'] += e['amountPaid']
            responseData['totalAmountOutstanding'] += e['amountOutstanding']
            responseData['expectedSalesForTheDay'] += e['amountDue']

        return Response(responseData)


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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # Check for orders associated with vendor

        try:
            orders = Order.objects.filter(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No food orders to prompt notifications'}, status=status.HTTP_400_BAD_REQUEST)

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

        if len(response) == 0:
            return Response({'message': 'No notifications to show'}, status=status.HTTP_204_NO_CONTENT)

        # Get message statuses

        try:
            messageStatus = MessageStatus.objects.all()
        except MessageStatus.DoesNotExist:
            return Response({'message': 'An issue with our message status. Please contact mailto:tobia807@gmail.com'}, status=status.HTTP_400_BAD_REQUEST)

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

    def post(self, request):
        """
        API method that allows authorized vendor to send notification to customer.
        """

        # Authenticate/Authorize user

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # Validate user input

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(
            ['subjectUser', 'orderId', 'message', 'messageStatusId'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        try:
            Order.objects.filter(
                vendorId=userPayload['user_id'], customerId=requestData['subjectUser'])
        except Order.DoesNotExist:
            return Response({'message': 'No recipient found for the given order'}, status=status.HTTP_404_NOT_FOUND)

        # Get message status name

        try:
            messageStatus = MessageStatus.objects.get(
                id=requestData['messageStatusId'])
        except MessageStatus.DoesNotExist:
            return Response({'message': 'Invalid message status'}, status=status.HTTP_400_BAD_REQUEST)

        messageStatuserializer = MessageStatusSerializer(messageStatus)

        # Send notification

        notificationSerializer = NotificationSerializer(
            data=requestData)

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

        userAuth = UserAuthProcess(request, 'vendor')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        try:
            orders = Order.objects.filter(vendorId=userPayload['user_id'])
        except Order.DoesNotExist:
            return Response({'message': 'No food orders to prompt notifications'}, status=status.HTTP_404_NOT_FOUND)

        orderSerializer = OrderSerializer(orders, many=True)

        for e in orderSerializer.data:
            try:
                notification = Notification.objects.get(
                    orderId=e['id'], id=notification_id)
            except Notification.DoesNotExist:
                continue

            if notification:
                notificationSerializer = NotificationSerializer(notification)

                # Get message statuses

                try:
                    messageStatus = MessageStatus.objects.get(
                        id=notificationSerializer.data['messageStatusId'])
                except MessageStatus.DoesNotExist:
                    return Response({'message': 'An issue with our message status. Please contact mailto:tobia807@gmail.com'}, status=status.HTTP_400_BAD_REQUEST)

                messageStatusSerializer = MessageStatusSerializer(
                    messageStatus)
                response = {**notificationSerializer.data}
                response['messageStatusId'] = messageStatusSerializer.data['name']
                return Response(response)
        return Response(status=status.HTTP_404_NOT_FOUND)


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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # validate user input

        requestData = protectRestrictedInput({**request.data})

        requiredFields = EnsureRequiredFields(
            ['vendorId', 'itemsOrdered'], requestData.keys())
        try:
            if requiredFields.error:
                return requiredFields.errorResponse()
        except:
            pass

        if 'description' in requestData.keys() and len(requestData['description']) < 5:
            requestData.pop('description')

        if 'preOrderDateTime' in requestData.keys():
            if len(requestData['preOrderDateTime']) == 0:
                requestData.pop('preOrderDateTime')
            elif len(requestData['preOrderDateTime']) < 13:
                return Response({'message': 'Wrong date/time format. yyyy-mm-dd-hh'}, status.HTTP_400_BAD_REQUEST)

        requestData['customerId'] = userPayload['user_id']

        # Check for order status

        orderStatusId = getDefaultForeignKey(OrderStatus)

        try:
            if orderStatusId.error:
                return orderStatusId.errorResponse()
        except:
            pass

        requestData['orderStatusId'] = orderStatusId

        # check that menu exists

        amountDue = 0

        for menuId in requestData['itemsOrdered']:
            try:
                menu = Menu.objects.get(
                    vendorId=requestData['vendorId'], id=menuId)
            except Menu.DoesNotExist:
                return Response({'message': 'The selected menu ({}) is not available for order'.format(menuId)}, status.HTTP_404_NOT_FOUND)

            menuSerializer = MenuSerializer(menu)
            amountDue += menuSerializer.data['price']

        requestData['amountDue'] = amountDue
        requestData['amountOutstanding'] = amountDue

        # handle pre-orders

        if 'preOrderDateTime' in requestData.keys():

            try:
                requestData['preOrderDateTime'] = datetime.strptime(
                    requestData['preOrderDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(tz=pytz.utc)
            except:
                return Response({'message': 'Invalid date/time format => yyyy-mm-ddThh:mm:ss.ffffffZ'}, status.HTTP_400_BAD_REQUEST)

            currentDateTime = datetime.utcnow().astimezone(tz=pytz.utc)

            if (requestData['preOrderDateTime'] - currentDateTime).seconds < 18000 or (requestData['preOrderDateTime'] - currentDateTime).days > 3:
                return Response({'message': 'Unacceptable pre-order. Pre-order is valid between 5 hours and 3 days after the order is placed'}, status.HTTP_400_BAD_REQUEST)

        # Create the food order

        orderSerializer = OrderSerializer(data=requestData)

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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        # Get notifications for the customer

        try:
            notifications = Notification.objects.filter(
                subjectUser=userPayload['user_id'])
        except Notification.DoesNotExist:
            return Response({'message': 'No notifications to show'}, status=status.HTTP_400_BAD_REQUEST)

        notificationSerializer = NotificationSerializer(
            notifications, many=True)

        # Get message statuses

        try:
            messageStatus = MessageStatus.objects.all()
        except MessageStatus.DoesNotExist:
            return Response({'message': 'An issue with our message status. Please contact mailto:tobia807@gmail.com'}, status=status.HTTP_400_BAD_REQUEST)

        messageStatusSerializer = MessageStatusSerializer(
            messageStatus, many=True)
        messageStatus = {}

        for e in messageStatusSerializer.data:
            messageStatus[e['id']] = e['name']

        for e in notificationSerializer.data:
            if e['messageStatusId'] in messageStatus.keys():
                e['messageStatus'] = messageStatus[e['messageStatusId']]
                e.pop('messageStatusId')
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

        userAuth = UserAuthProcess(request, 'customer')
        try:
            if userAuth.error:
                return userAuth.errorResponse()
        except:
            pass
        userPayload = userAuth.userPayload

        try:
            notification = Notification.objects.get(
                subjectUser=userPayload['user_id'], id=notification_id)
        except Notification.DoesNotExist:
            return Response({'message': 'No notification to show'}, status=status.HTTP_400_BAD_REQUEST)

        notificationSerializer = NotificationSerializer(notification)

        # Get message statuses

        try:
            messageStatus = MessageStatus.objects.get(
                id=notificationSerializer.data['messageStatusId'])
        except MessageStatus.DoesNotExist:
            return Response({'message': 'An issue with our message status. Please contact mailto:tobia807@gmail.com'}, status=status.HTTP_400_BAD_REQUEST)

        messageStatusSerializer = MessageStatusSerializer(messageStatus)
        response = {**notificationSerializer.data}
        response['messageStatusId'] = messageStatusSerializer.data['name']
        return Response(response)


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

        return getDataById(Menu, menu_id, MenuSerializer)


# get-a-vendor


class VendorDetailAPIView(APIView):
    """
    API endpoint that allows a vendor to be viewed.
    """

    def get(self, request, vendor_id):
        """
        API method that gets a database row by id.
        """

        return getDataById(Vendor, vendor_id, VendorSerializer)
