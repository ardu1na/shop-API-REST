from django.test import TestCase
from django.contrib.auth.models import User
from ecommerce.models import Category, Product, Client, Cart, ProductCart, Order
from django.core.exceptions import ValidationError
from django.urls import reverse

from rest_framework.test import APIClient
from .serializers import (
    ProductSerializer,
)

class APISerializerTestCase(TestCase):
    def setUp(self):
        # Create a test user for this test case
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

    def test_product_serializer(self):
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(name='Test Product', description='Description', price=10, category=category)
        serializer = ProductSerializer(product)
        expected_data = {
            'id': product.id,
            'name': 'Test Product',
            'description': 'Description',
            'price': '10.00',
            'brand': None,
            'category': category.id,
            'category_name': 'Test Category',
            'image': None,
            'stock': 0,
            'available': False,
            'date_created': serializer.data['date_created'],  # Include only the relevant fields
            'date_updated': serializer.data['date_updated'],  # Include only the relevant fields
        }
        self.assertEqual(serializer.data, expected_data)




class ModelTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
    def test_create_client_on_new_user(self):
        # Ensure a Client is created when a User is created
        self.assertTrue(Client.objects.filter(user=self.user).exists())

    def test_product_cart_validation(self):
        # Create a category
        category = Category.objects.create(name='Test Category')
        # Create a product with no stock
        product = Product.objects.create(name='Test Product', description='Description', price=10, category=category)
        # Create a cart
        cart = Cart.objects.create(client=self.user.client)
        # Attempt to add a product with an amount greater than stock to the cart
        with self.assertRaises(ValidationError):
            ProductCart.objects.create(cart=cart, product=product, ammount=2)

    def test_update_cart_signal(self):
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(name='Test Product', description='Description', price=10, category=category)
        cart = Cart.objects.create(client=self.user.client)
        
        # Decrease the stock to 1, so it's not exceeded by the ProductCart
        product.stock = 1
        product.save()
        
        product_cart = ProductCart.objects.create(cart=cart, product=product, ammount=1)
        
        # Check if the cart's total and products_q are updated correctly
        cart.refresh_from_db()
        self.assertEqual(cart.total, product.price)
        self.assertEqual(cart.products_q, 1)

    def test_create_order_on_cart_done_signal(self):
        category = Category.objects.create(name='Test Category')
        product = Product.objects.create(name='Test Product', description='Description', price=10, category=category)
        cart = Cart.objects.create(client=self.user.client, done=True)
        # Ensure that an order is created when a cart is marked as done
        self.assertTrue(Order.objects.filter(cart=cart).exists())
