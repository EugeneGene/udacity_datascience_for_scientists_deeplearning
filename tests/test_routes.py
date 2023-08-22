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
FireIncident API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestFireIncidentService
"""

import os
import logging
from unittest import TestCase

# from unittest.mock import MagicMock, patch
from service import app
from service.common import status
from service.models import db, init_db, FireIncident
from tests.factories import FireIncidentFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/fires"


######################################################################
#  T E S T   P E T   S E R V I C E
######################################################################
class TestFireIncidentService(TestCase):
    """FireIncident Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(FireIncident).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_fire_incidents(self, count):
        """Factory method to create fire_incidents in bulk"""
        fire_incidents = []
        for _ in range(count):
            test_fire_incident = FireIncidentFactory()
            response = self.client.post(BASE_URL, json=test_fire_incident.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test fire incident",
            )
            new_fire_incident = response.get_json()
            test_fire_incident.object_id = new_fire_incident["object_id"]
            fire_incidents.append(test_fire_incident)
        return fire_incidents

    # pylint: disable=duplicate-code
    def _validate_data(self, data: dict, fire_incident: FireIncident):
        """Check that the data dictionary matches the file_incident object"""
        self.assertEqual(data["object_id"], fire_incident.object_id)
        self.assertEqual(data["x"], fire_incident.x)
        self.assertEqual(data["y"], fire_incident.y)
        self.assertEqual(data["incident_size"], fire_incident.incident_size)
        self.assertEqual(
            data["containment_datetime"], fire_incident.containment_datetime.isoformat()
        )
        self.assertEqual(
            data["fire_discovery_datetime"],
            fire_incident.fire_discovery_datetime.isoformat(),
        )
        self.assertEqual(data["incident_name"], fire_incident.incident_name)
        self.assertEqual(
            data["incident_type_category"], fire_incident.incident_type_category
        )
        self.assertEqual(data["initial_latitude"], fire_incident.initial_latitude)
        self.assertEqual(data["initial_longitude"], fire_incident.initial_longitude)
        self.assertEqual(data["poo_city"], fire_incident.poo_city)
        self.assertEqual(data["poo_county"], fire_incident.poo_county)
        self.assertEqual(data["poo_state"], fire_incident.poo_state)
        self.assertEqual(data["fire_cause_id"], fire_incident.fire_cause_id)
        self.assertEqual(
            data["poo_landowner_category"], fire_incident.poo_landowner_category
        )
        self.assertEqual(
            data["unique_fire_identifier"], fire_incident.unique_fire_identifier
        )

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "FireIncident REST API Service")

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/healthcheck")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_get_fire_incident_list(self):
        """It should Get a list of FireIncidents"""
        self._create_fire_incidents(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_fire_incident(self):
        """It should Get a single FireIncident"""
        # get the id of a fire_incident
        fire_incident = self._create_fire_incidents(1)[0]
        response = self.client.get(f"{BASE_URL}/{fire_incident.object_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test that the data is correct
        data = response.get_json()
        self._validate_data(data, fire_incident)

    def test_get_fire_incident_not_found(self):
        """It should not Get a FireIncident thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_fire_incident(self):
        """It should Create a new FireIncident"""
        test_fire_incident = FireIncidentFactory()
        logging.debug("Test FireIncident: %s", test_fire_incident.serialize())
        response = self.client.post(BASE_URL, json=test_fire_incident.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        data = response.get_json()
        self._validate_data(data, test_fire_incident)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_fire_incident = response.get_json()
        self._validate_data(new_fire_incident, test_fire_incident)

    def test_update_fire_incident(self):
        """It should Update an existing FireIncident"""
        # create a fire_incident to update
        test_fire_incident = FireIncidentFactory()
        response = self.client.post(BASE_URL, json=test_fire_incident.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the fire_incident
        new_fire_incident = response.get_json()
        logging.debug(new_fire_incident)
        new_fire_incident["incident_name"] = "$%^&*()"
        response = self.client.put(
            f"{BASE_URL}/{new_fire_incident['object_id']}", json=new_fire_incident
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_fire_incident = response.get_json()
        self.assertEqual(updated_fire_incident["incident_name"], "$%^&*()")

    def test_delete_fire_incident(self):
        """It should Delete a FireIncident"""
        test_fire_incident = self._create_fire_incidents(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_fire_incident.object_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_fire_incident.object_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_fire_incident_list_by_poo_county(self):
        """It should Query FireIncidents by POO County"""
        fire_incidents = self._create_fire_incidents(10)
        poo_county = fire_incidents[0].poo_county
        poo_county_fire_incidents = [
            fire_incident
            for fire_incident in fire_incidents
            if fire_incident.poo_county == poo_county
        ]
        response = self.client.get(BASE_URL, query_string=f"poo_county={poo_county}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(poo_county_fire_incidents))
        # check the data just to be sure
        for fire_incident in data:
            self.assertEqual(fire_incident["poo_county"], poo_county)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_fire_incident_no_data(self):
        """It should not Create a FireIncident with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_fire_incident_no_content_type(self):
        """It should not Create a FireIncident with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_fire_incident_wrong_content_type(self):
        """It should not Create a FireIncident with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
