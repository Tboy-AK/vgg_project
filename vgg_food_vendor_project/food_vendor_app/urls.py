from django.urls import path
from rest_framework_jwt.views import RefreshJSONWebToken
from vgg_food_vendor_project.food_vendor_app import views


urlpatterns = [
    # refresh token
    path('token/refresh/', RefreshJSONWebToken.as_view()),

    # homepage
    path('', views.HomeDescAPIView.as_view()),

    # user login
    path('login/', views.LoginAPIView.as_view()),


    # user authentication and vendor view


    # vendor signup on POST, and public view vendors on GET
    path('vendor/', views.VendorAPIView.as_view()),

    # customer signup on POST
    path('customer/', views.CustomerAPIView.as_view()),


    # auth vendor


    # vendor view all menu on GET, vendor create menu on POST
    path('auth/vendor/menu/', views.AuthVendorMenuAPIView.as_view()),

    # vendor update menu on PUT, vendor delete menu on DELETE
    path('auth/vendor/menu/<int:menu_id>/',
         views.AuthVendorMenuDetailAPIView.as_view()),

    # vendor view all orders on GET
    path('auth/vendor/order/', views.AuthVendorOrderAPIView.as_view()),

    # vendor view order, update order status on PATCH
    path('auth/vendor/order/<int:order_id>/',
         views.AuthVendorOrderDetailAPIView.as_view()),

    # vendor generate daily sales report
    path('auth/vendor/sales/daily/', views.AuthVendorSalesReportAPIView.as_view()),

    # vendor view all notifications, notify customer
    path('auth/vendor/notification/',
         views.VendorNotificationAPIView.as_view()),

    # vendor view a notification
    path('auth/vendor/notification/<int:notification_id>/',
         views.VendorNotificationDetailAPIView.as_view()),


    # public


    # view all menus
    path('menu/', views.MenuAPIView.as_view()),

    # view all menus of a vendor
    path('vendor/<int:vendor_id>/menu/', views.VendorMenuAPIView.as_view()),

    # view a menu
    path('menu/<int:menu_id>/', views.MenuDetailAPIView.as_view()),


    # customer, auth customer


    # customer view all orders on GET, make order on POST
    path('auth/customer/order/', views.AuthCustomerOrderAPIView.as_view()),

    # customer view order on GET, cancel order on DELETE
    path('auth/customer/order/<int:order_id>/',
         views.AuthCustomerOrderDetailAPIView.as_view()),

    # customer order payment on PATCH
    path('auth/customer/order/payment/<int:order_id>/',
         views.AuthCustomerOrderPaymentAPIView.as_view()),

    # customer view all notifications
    path('auth/customer/notification/',
         views.CustomerNotificationAPIView.as_view()),

    # customer view a notification
    path('auth/customer/notification/<int:notification_id>/',
         views.CustomerNotificationDetailAPIView.as_view()),
]
