from django.urls import path
from vgg_food_vendor_project.food_vendor_app import views


urlpatterns = [

    # homepage
    path('', views.HomeDescAPIView.as_view()),

    # general view of vendors
    path('vendor/', views.VendorAPIView.as_view()),
    path('vendor/<int:id>/', views.TargetVendorAPIView.as_view()),
    path('vendor/<int:id>/menu/', views.TargetMenuAPIView.as_view()),
    path('vendor/<int:id>/menu/<int:id>/', views.TargetMenuAPIView.as_view()),

    # general view of menus
    path('menu/', views.MenuAPIView.as_view()),
    path('menu/<int:id>/', views.TargetMenuAPIView.as_view()),

    # user login
    path('login/', views.AuthAPIView.as_view()),

    # vendor signup
    path('auth/vendor/', views.VendorAPIView.as_view()),

    # logged-in vendor
    path('auth/vendor/menu/', views.TargetOrderAPIView.as_view()),
    path('auth/vendor/order/', views.TargetOrderAPIView.as_view()),
    path('auth/vendor/order/<int:id>/', views.TargetOrderAPIView.as_view()),
    path('auth/vendor/customer/', views.TargetCustomerAPIView.as_view()),
    path('auth/vendor/customer/<int:id>/',
         views.TargetCustomerAPIView.as_view()),

    # customer signup
    path('auth/customer/', views.CustomerAPIView.as_view()),

    # logged-in customer
    path('auth/customer/order/', views.OrderAPIView.as_view()),
    path('auth/customer/order/<int:id>/', views.TargetOrderAPIView.as_view()),
    path('auth/customer/vendor/', views.TargetOrderAPIView.as_view()),

    # notifications
    path('auth/notification/', views.NotificationAPIView.as_view()),
    path('auth/notification/<int:id>', views.TargetNotificationAPIView.as_view()),
]
