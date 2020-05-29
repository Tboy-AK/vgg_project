# food_vendor_project

An API for food vendors to make transactions and communicate with their customers

Built with [Django REST Framework](https://www.django-rest-framework.org)

Hosted on [food-vendor-api.herokuapp.com](https://tboyak-foodvendorapp.herokuapp.com)

A more detailed documentation for this application can be found [here](https://drive.google.com/open?id=1AtUWIAsD-tCA5P7gaRxDhlS1PJKDyRHl)


## Major routes

1. *domain*/api/
2. *domain*/admin/


## Admin access

Username: tboyak
Password: asdf1234!

## Types of Users

- Vendors
- Customers


## Important To Note

- All routes must end with a forward slash "/"
- Timezones are UTC


## Core Features

- Authentication and authorization
- Food purchase / pre-order
- Food order management
- Notification


## Functional Requirements (Vendor)

- The vendor should be able to sign up with name, email and phone number.
- The vendor should be able to set a password.
- The vendor should be able to log in with email and password.
- The vendor should be able to create a menu.
- The vendor should be able to update a menu.
- The vendor should be able to view orders
- The vendor should be able to update order status.
- The vendor should be able to generate a daily report of sales.
- The vendor should be able to send notifications to the customer on available menu or debts, order progress and other relevant information.  


## Functional Requirements (Customer)

- Customer should be able to sign up with name, email and phone number.
- Customer should be able to set a password.
- Customer should be able to log in with email and password.
- Customer should be able to purchase food from the available menu that has been put up by the vendor.
- Customer should be able to pre-order food.
- Customer should be able to cancel order.
- Payment for food purchased or pre-ordered (No payment integration required. A flip of payment status is sufficient).
