# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory
from service.models import DataValidationError
from unittest.mock import patch, MagicMock

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #

    # TASK 2a
    def test_a_read_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        # Set the ID of the product object to None and then call the create() method on the product.
        product.id = None 
        product.create()
        self.assertIsNotNone(product.id, "Product ID should not be None after creation")
        # Fetch the product back from the DB using the product ID
        found_product = Product.query.get(product.id)
        # Assert that the properties of the found product match the original product obj
        self.assertEqual(found_product.id, product.id, "Product IDs should match")
        self.assertEqual(found_product.name, product.name, "Product names should match")
        self.assertEqual(found_product.description, product.description, "Product descriptions should match")
        self.assertEqual(Decimal(found_product.price), product.price, "Product prices should match")
        self.assertEqual(found_product.available, product.available, "Product availability should match")
        self.assertEqual(found_product.category, product.category, "Product categories should match")

        app.logger.debug(f"Found Product: {found_product}")

    # Task 2b
    def test_update_a_product(self):
        """It should Update a Product"""
        # Step 1: Create a product
        product = ProductFactory()
        product.id = None  # Ensure ID is None to trigger creation
        product.create()  # Save the product to the system
        
        # Step 2: Assert that the product was created and has an ID
        self.assertIsNotNone(product.id)
        
        # Step 3: Update the product description and save it
        product.description = "testing"
        original_id = product.id
        product.update()  # Save the updated product to the system
        
        # Step 4: Assert that the ID is unchanged, and the description is updated
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        
        # Step 5: Fetch all products and verify there's only one product
        products = Product.all()
        self.assertEqual(len(products), 1)
        
        # Step 6: Verify that the product ID is the same and the description is updated
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    # Task 2c
    def test_delete_a_product(self):
        """It should Delete a Product"""
        # Step 1: Create a product
        product = ProductFactory()
        product.create()  # Save the product to the system
        # Step 2: Assert that there's only one product in the system
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Step 3: Delete the product from the system
        product.delete()  # Remove the product from the system
           # Step 4: Assert that the product has been deleted
        products = Product.all()
        self.assertEqual(len(products), 0)

    # Task 2d
    def test_list_all_products(self):
        """It should List all Products in the database"""
        # Step 1: Assert if there are no products in the database at the beginning
        products = Product.all()
        self.assertEqual(len(products), 0)
        # Step 2: Create and save five products to the database
        for _ in range(5):
            product = ProductFactory()
            product.create()  # Save the product to the database
        # Step 3: Fetch all products from the database
        products = Product.all()
        # Step 4: Assert that there are 5 products in the database
        self.assertEqual(len(products), 5)
 
    # Task 2e
    def test_find_by_name(self):
        """It should Find a Product by Name"""
        # Create and save a batch of 5 products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()  # Save each product to the database
        # Retrieve the name of the first product in the list
        product_name = products[0].name
        # Count the number of occurrences of the product name in the list
        count = len([p for p in products if p.name == product_name])
        # Find products by name using the find_by_name() method
        found_products = Product.find_by_name(product_name).all()  # Fetch actual results with .all()
        # Assert that the count of found products matches the expected count
        self.assertEqual(len(found_products), count)
        # Assert that each found product's name matches the expected name
        for product in found_products:
            self.assertEqual(product.name, product_name)

    # Task 2f
    def test_find_by_category(self):
        """It should Find Products by Category"""
        
        # Create and save a batch of 10 products using the ProductFactory
        products = ProductFactory.create_batch(10)
        for product in products:
            db.session.add(product)  # Add products to the session
        db.session.commit()  # Commit to save the products to the database
        
        # Retrieve the category of the first product in the products list
        category = products[0].category
        
        # Count the number of occurrences of products with the same category in the list
        count = len([product for product in products if product.category == category])
        
        # Retrieve products from the database that have the specified category
        found = Product.query.filter_by(category=category).all()
        
        # Assert if the count of the found products matches the expected count
        self.assertEqual(len(found), count)
        
        # Assert that each found product's category matches the expected category
        for product in found:
            self.assertEqual(product.category, category)

    # Task 2g
    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    # to cover models.py line 106
    def test_update_product_with_empty_id(self):
            """Test that DataValidationError is raised when updating a product with an empty ID"""
            # Create a product object without setting an ID (simulating empty ID scenario)
            product = Product(name="Test Product", price=100)
            # Assert that calling update() raises a DataValidationError
            with self.assertRaises(DataValidationError) as context:
                product.update()  # This should raise the error
            # Check that the error message matches the expected one
            self.assertEqual(str(context.exception), "Update called with empty ID field")

    # to cover models.py line 139
    def test_deserialize_invalid_available_type(self):
        """Test that a DataValidationError is raised when the 'available' field has an invalid type"""
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": "100.0",  # Assuming price is passed as a string and will be cast to Decimal
            "available": "yes",  # Invalid type (should be boolean)
            "category": "ELECTRONICS"  # Assuming category is valid
        }

        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        
        self.assertEqual(str(context.exception), "Invalid type for boolean [available]: <class 'str'>")

    # to cover models.py line 145
    def test_deserialize_invalid_attribute(self):
        data = {
            "name": "Test Product",
            "description": "A test product",
            "price": "100.0",
            "available": True,
            # "category" field is intentionally omitted to trigger the AttributeError
        }
        product = Product()
        with self.assertRaises(DataValidationError) as context:
            product.deserialize(data)
        self.assertEqual(str(context.exception), "Invalid product: missing category")
        
    # to cover models.py 189-190
    @patch("service.models.logger.info")  # Mock logger.info with the correct import path
    @patch("service.models.Product.query.get")  # Mock query.get with the correct import path
    def test_find_product_by_id(self, mock_query_get, mock_logger_info):
        # Arrange: Mock the return value of query.get
        product_id = 1
        mock_product = Product(id=product_id, name="Test Product")
        mock_query_get.return_value = mock_product  # Simulate the product being returned from DB
        
        # Act: Call the find method
        product = Product.find(product_id)
        
        # Assert: Ensure logger.info was called with the correct message
        mock_logger_info.assert_called_with("Processing lookup for id %s ...", product_id)
        
        # Assert: Ensure query.get was called with the correct product_id
        mock_query_get.assert_called_with(product_id)
        
        # Assert: Ensure the product returned is the same as the mock product
        self.assertEqual(product, mock_product)
    
    # to cover models.py 217-221
    @patch('service.models.Product.query.filter')
    @patch('service.models.logger.info')
    def test_find_by_price(self, mock_logger, mock_filter):
        # Arrange
        price = Decimal('19.99')
        mock_product = MagicMock()
        mock_product.price = price
        mock_filter.return_value = [mock_product]  # Simulate returned products

        # Act
        result = Product.find_by_price(price)

        # Assert that the logger is called
        mock_logger.assert_called_once_with("Processing price query for %s ...", price)

        # Ensure filter was called with the right parameters
        mock_filter.assert_called_once_with(Product.price == price)  # Check this

        # Assert the result is what we expect
        self.assertEqual(result, [mock_product])

    @patch('service.models.Product.query.filter')
    @patch('service.models.logger.info')
    def test_find_by_price_with_string_input(self, mock_logger, mock_filter):
        # Arrange
        price_str = '"19.99"'  # String input with quotes
        price_decimal = Decimal('19.99')
        mock_product = MagicMock()
        mock_product.price = price_decimal
        mock_filter.return_value = [mock_product]  # Simulate returned products

        # Act
        result = Product.find_by_price(price_str)  # Call with string input

        # Assert that the logger is called
        mock_logger.assert_called_once_with("Processing price query for %s ...", price_str)

        # Ensure filter was called with the right parameters (price_decimal after conversion)
        mock_filter.assert_called_once_with(Product.price == price_decimal)

        # Assert the result is what we expect
        self.assertEqual(result, [mock_product])

    @patch('service.models.Product.query')
    def test_find_product_by_id(self, mock_query):
        # Arrange
        product_id = 1
        mock_product = MagicMock()
        mock_query.get.return_value = mock_product  # Simulate returned product by ID

        # Act
        result = Product.find(product_id)

        # Assert that get was called with the correct product_id
        mock_query.get.assert_called_once_with(product_id)

        # Assert that the result is the mock product
        self.assertEqual(result, mock_product)
