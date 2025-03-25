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

            
