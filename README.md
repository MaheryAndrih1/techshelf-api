# TechShelf - E-Commerce Platform

TechShelf is a comprehensive e-commerce platform for technology products, featuring multi-vendor support, user authentication, product management, order processing, and more.

## Features

- User authentication and account management
- Seller dashboard with store management
- Product listings and search
- Shopping cart functionality
- Secure checkout process
- Order management
- Sales analytics and reporting
- Notification system

## Technology Stack

- **Backend**: Django REST Framework
- **Frontend**: React (coming soon)
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger/OpenAPI

## API Documentation

Full API documentation is available at `/api/swagger/` when the server is running. You can also view it in Markdown format in the `api_documentation.md` file.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

### Installation

1. Clone the repository

# TechShelf Application Documentation

## Overview

TechShelf is an e-commerce platform that allows users to buy and sell tech products. The application is built using Django for the backend and ReactJS for the frontend. This documentation provides an overview of the application's architecture, models, views, and templates.
Next step : build frontend.
## Table of Contents

1. Architecture
2. Models
3. Views
4. Templates
5. Forms
6. Authentication
7. Notifications
8. Order Processing
9. Custom Template Tags
10. Settings

## Architecture

The TechShelf application follows the Model-View-Template (MVT) architecture pattern provided by Django. The main components are:

- **Models**: Define the structure of the database.
- **Views**: Handle the logic and interact with models to fetch data.
- **Templates**: Render the data into HTML for the frontend.

## Models

### Users

- **User**: Custom user model extending Django's AbstractUser.
- **BillingInfo**: Stores billing information for users.

### Stores

- **Store**: Represents a store created by a seller.
- **StoreTheme**: Stores theme information for a store.
- **Rating**: Stores ratings and reviews for stores.

### Products

- **Product**: Represents a product listed by a seller.
- **Like**: Stores likes for products.

### Orders

- **Cart**: Represents a shopping cart for a user.
- **CartItem**: Represents an item in a shopping cart.
- **ShippingInfo**: Stores shipping information for orders.
- **Order**: Represents an order placed by a user.
- **Promotion**: Stores promotion codes for discounts.

### Notifications

- **Notification**: Stores notifications for users.
- **SalesReport**: Stores sales reports for sellers.

## Views

### Users

- **login_view**: Handles user login.
- **logout_view**: Handles user logout.
- **register_view**: Handles user registration.
- **profile_view**: Displays user profile.
- **edit_profile_view**: Handles profile editing.
- **billing_info_view**: Handles billing information management.
- **upgrade_to_seller_view**: Handles upgrading a user to a seller.

### Stores

- **landing_page_view**: Displays the landing page.
- **about_view**: Displays the about page.
- **contact_view**: Handles contact form submissions.
- **how_it_works_view**: Displays the "How it Works" page.
- **store_list_view**: Displays a list of stores.
- **create_store_view**: Handles store creation.
- **store_detail_view**: Displays store details.
- **edit_store_view**: Handles store editing.
- **store_theme_view**: Handles store theme editing.
- **store_ratings_view**: Displays store ratings.
- **rate_store_view**: Handles store rating submissions.

### Products

- **product_list_view**: Displays a list of products.
- **product_detail_view**: Displays product details.
- **product_category_view**: Displays products by category.
- **create_product_view**: Handles product creation.
- **edit_product_view**: Handles product editing.
- **like_product_view**: Handles liking a product.

### Orders

- **cart_view**: Displays the shopping cart.
- **add_to_cart_view**: Handles adding items to the cart.
- **remove_from_cart_view**: Handles removing items from the cart.
- **update_cart_quantity_view**: Handles updating cart item quantities.
- **checkout_view**: Handles the checkout process.
- **order_list_view**: Displays a list of orders.
- **order_detail_view**: Displays order details.
- **apply_promotion_view**: Handles applying promotion codes.

### Notifications

- **notification_list_view**: Displays a list of notifications.
- **mark_notification_read_view**: Handles marking notifications as read.
- **sales_reports_view**: Displays sales reports.
- **generate_report_view**: Handles generating sales reports.
- **report_detail_view**: Displays sales report details.

## Templates

### Base Templates

- **base.html**: Base template for the application.

### Landing Pages

- **home.html**: Landing page template.
- **about.html**: About page template.
- **contact.html**: Contact page template.
- **how_it_works.html**: "How it Works" page template.

### Users

- **login.html**: Login page template.
- **register.html**: Registration page template.
- **profile.html**: Profile page template.
- **edit_profile.html**: Edit profile page template.
- **billing.html**: Billing information page template.
- **upgrade_seller.html**: Upgrade to seller page template.

### Stores

- **list.html**: Store list page template.
- **create.html**: Create store page template.
- **detail.html**: Store detail page template.
- **edit.html**: Edit store page template.
- **theme.html**: Edit store theme page template.
- **ratings.html**: Store ratings page template.
- **rate.html**: Rate store page template.

### Products

- **list.html**: Product list page template.
- **detail.html**: Product detail page template.
- **create.html**: Create product page template.
- **edit.html**: Edit product page template.

### Orders

- **cart.html**: Shopping cart page template.
- **checkout.html**: Checkout page template.
- **order_list.html**: Order list page template.
- **order_detail.html**: Order detail page template.

### Notifications

- **list.html**: Notification list page template.
- **reports.html**: Sales reports page template.
- **report_detail.html**: Sales report detail page template.

## Forms

### Users

- **RegistrationForm**: Form for user registration.
- **ProfileEditForm**: Form for editing user profile.
- **BillingInfoForm**: Form for managing billing information.

### Stores

- **StoreCreationForm**: Form for creating a new store.
- **StoreEditForm**: Form for editing an existing store.
- **StoreThemeForm**: Form for editing a store theme.
- **RatingForm**: Form for rating a store.

## Authentication

### Custom Authentication Backend

- **EmailBackend**: Custom authentication backend to allow login with email.

## Notifications

### Notification Creation

- Notifications are created when an order is placed or cancelled.

## Order Processing

### Checkout Process

- The checkout process involves creating shipping information, processing payment, and creating notifications for the buyer and seller.

## Custom Template Tags

### Product Filters

- **get_attribute**: Extracts attribute values from queryset items.
- **contains**: Checks if a user is in a list.

### Order Filters

- **multiply**: Multiplies two values.

## Settings

### Authentication Backends

```python
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
