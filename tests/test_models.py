"""
Test cases for FireIncident Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_fire_incidents.py:TestFireIncidentModel

"""
import os
import logging
import unittest
from datetime import datetime
from service.models import FireIncident, DataValidationError, db
from service import app
from tests.factories import FireIncidentFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  F I R E   I N C I D E N T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestFireIncidentModel(unittest.TestCase):
    """Test Cases for FireIncident Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        FireIncident.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(FireIncident).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    # pylint: disable=duplicate-code
    def _validate_data(self, data: dict, fire_incident: FireIncident):
        """Check that the data dictionary matches the file_incident object"""
        self.assertEqual(data["object_id"], fire_incident.object_id)
        self.assertEqual(data["x"], fire_incident.x)
        self.assertEqual(data["y"], fire_incident.y)
        self.assertEqual(data["incident_size"], fire_incident.incident_size)
        self.assertEqual(
            datetime.fromisoformat(data["containment_datetime"]),
            fire_incident.containment_datetime,
        )
        self.assertEqual(
            datetime.fromisoformat(data["fire_discovery_datetime"]),
            fire_incident.fire_discovery_datetime,
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

    def test_create_a_fire_incident(self):
        """It should Create a fire incident and add it to the database"""
        fire_incidents = FireIncident.all()
        self.assertEqual(fire_incidents, [])
        fire_incident = FireIncidentFactory()
        self.assertTrue(fire_incident is not None)
        fire_incident.create()

        # Assert that it shows up in the database
        fire_incidents = FireIncident.all()
        self.assertEqual(len(fire_incidents), 1)

    def test_read_a_fire_incident(self):
        """It should Read a FireIncident"""
        fire_incident = FireIncidentFactory()
        logging.debug(fire_incident)
        fire_incident.create()
        self.assertIsNotNone(fire_incident.object_id)

        # Fetch it back and check it's values
        found_incident = FireIncident.find(fire_incident.object_id)
        self.assertEqual(found_incident.x, fire_incident.x)
        self.assertEqual(found_incident.y, fire_incident.y)
        self.assertEqual(found_incident.incident_size, fire_incident.incident_size)
        self.assertEqual(
            found_incident.containment_datetime, fire_incident.containment_datetime
        )
        self.assertEqual(
            found_incident.fire_discovery_datetime,
            fire_incident.fire_discovery_datetime,
        )
        self.assertEqual(found_incident.incident_name, fire_incident.incident_name)
        self.assertEqual(
            found_incident.incident_type_category, fire_incident.incident_type_category
        )
        self.assertEqual(
            found_incident.initial_latitude, fire_incident.initial_latitude
        )
        self.assertEqual(
            found_incident.initial_longitude, fire_incident.initial_longitude
        )
        self.assertEqual(found_incident.poo_city, fire_incident.poo_city)
        self.assertEqual(found_incident.poo_county, fire_incident.poo_county)
        self.assertEqual(found_incident.poo_state, fire_incident.poo_state)
        self.assertEqual(found_incident.fire_cause_id, fire_incident.fire_cause_id)
        self.assertEqual(
            found_incident.poo_landowner_category, fire_incident.poo_landowner_category
        )
        self.assertEqual(
            found_incident.unique_fire_identifier, fire_incident.unique_fire_identifier
        )

    def test_update_a_fire_incident(self):
        """It should Update a FireIncident"""
        fire_incident = FireIncidentFactory()
        logging.debug(fire_incident)
        fire_incident.create()
        logging.debug(fire_incident)
        self.assertIsNotNone(fire_incident.object_id)

        # Change it an save it
        fire_incident.incident_name = "$%^&*()"
        original_id = fire_incident.object_id
        fire_incident.update()
        self.assertEqual(fire_incident.object_id, original_id)
        self.assertEqual(fire_incident.incident_name, "$%^&*()")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        fire_incidents = FireIncident.all()
        self.assertEqual(len(fire_incidents), 1)
        self.assertEqual(fire_incidents[0].object_id, original_id)
        self.assertEqual(fire_incidents[0].incident_name, "$%^&*()")

    def test_delete_a_fire_incident(self):
        """It should Delete a FireIncident"""
        fire_incident = FireIncidentFactory()
        fire_incident.create()
        self.assertEqual(len(FireIncident.all()), 1)
        # delete the fire_incident and make sure it isn't in the database
        fire_incident.delete()
        self.assertEqual(len(FireIncident.all()), 0)

    def test_list_all_fire_incidents(self):
        """It should List all FireIncidents in the database"""
        fire_incidents = FireIncident.all()
        self.assertEqual(fire_incidents, [])
        # Create 5 FireIncidents
        for _ in range(5):
            fire_incident = FireIncidentFactory()
            fire_incident.create()
        # See if we get back 5 fire_incidents
        fire_incidents = FireIncident.all()
        self.assertEqual(len(fire_incidents), 5)

    def test_serialize_a_fire_incident(self):
        """It should serialize a FireIncident"""
        fire_incident = FireIncidentFactory()
        data = fire_incident.serialize()
        self.assertNotEqual(data, None)
        self._validate_data(data, fire_incident)

    def test_deserialize_a_fire_incident(self):
        """It should de-serialize a FireIncident"""
        data = FireIncidentFactory().serialize()
        fire_incident = FireIncident()
        fire_incident.deserialize(data)
        self.assertNotEqual(fire_incident, None)
        self._validate_data(data, fire_incident)

    def test_deserialize_missing_data(self):
        """It should not deserialize a FireIncident with missing data"""
        data = {"x": 1.0, "y": 1.0, "incident_size": 3}
        fire_incident = FireIncident()
        self.assertRaises(DataValidationError, fire_incident.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        fire_incident = FireIncident()
        self.assertRaises(DataValidationError, fire_incident.deserialize, data)

    def test_find_fire_incident(self):
        """It should Find a FireIncident by Object ID"""
        fire_incidents = FireIncidentFactory.create_batch(5)
        for fire_incident in fire_incidents:
            fire_incident.create()
        logging.debug(fire_incidents)
        # make sure they got saved
        self.assertEqual(len(FireIncident.all()), 5)
        # find the 2nd fire_incident in the list
        fire_incident = FireIncident.find(fire_incidents[1].object_id)
        self.assertIsNot(fire_incident, None)
        self.assertEqual(fire_incident.object_id, fire_incidents[1].object_id)

    def test_find_by_poo_county(self):
        """It should Find a FireIncident by POO County"""
        fire_incidents = FireIncidentFactory.create_batch(10)
        poo_county = fire_incidents[0].poo_county
        poo_county_count = 0
        for fire_incident in fire_incidents:
            fire_incident.create()
            if fire_incident.poo_county == poo_county:
                poo_county_count += 1
        logging.debug(fire_incidents)

        # make sure they got saved
        self.assertEqual(len(FireIncident.all()), 10)

        # test if poo_county filter works
        poo_list = list(FireIncident.find_by_poo_county(poo_county))
        self.assertEqual(len(poo_list), poo_county_count)
