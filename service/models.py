"""
Models for FireIncident

All of the models are stored in this module
"""
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    FireIncident.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


# pylint: disable=too-many-instance-attributes
class FireIncident(db.Model):
    """
    Class that represents a FireIncident
    """

    app = None

    # Table Schema
    object_id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Double)
    y = db.Column(db.Double)
    incident_size = db.Column(db.Float)
    containment_datetime = db.Column(db.DateTime(timezone=True))
    fire_discovery_datetime = db.Column(db.DateTime(timezone=True))
    incident_name = db.Column(db.String(200))
    incident_type_category = db.Column(db.String(2))
    initial_latitude = db.Column(db.Double)
    initial_longitude = db.Column(db.Double)
    poo_city = db.Column(db.String(200))
    poo_county = db.Column(db.String(200))
    poo_state = db.Column(db.String(200))
    fire_cause_id = db.Column(db.Integer)
    poo_landowner_category = db.Column(db.String(200))
    unique_fire_identifier = db.Column(db.String(200))

    def __repr__(self):
        return f"<FireIncident {self.x} {self.y}]>"

    def create(self):
        """
        Creates a FireIncident to the database
        """
        logger.info("Creating %s", str(self))
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a FireIncident to the database
        """
        logger.info("Saving %s", str(self))
        db.session.commit()

    def delete(self):
        """Removes a FireIncident from the data store"""
        logger.info("Deleting %s", str(self))
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a FireIncident into a dictionary"""
        return {
            "object_id": self.object_id,
            "x": self.x,
            "y": self.y,
            "incident_size": self.incident_size,
            "containment_datetime": self.containment_datetime.isoformat(),
            "fire_discovery_datetime": self.fire_discovery_datetime.isoformat(),
            "incident_name": self.incident_name,
            "incident_type_category": self.incident_type_category,
            "initial_latitude": self.initial_latitude,
            "initial_longitude": self.initial_longitude,
            "poo_city": self.poo_city,
            "poo_county": self.poo_county,
            "poo_state": self.poo_state,
            "fire_cause_id": self.fire_cause_id,
            "poo_landowner_category": self.poo_landowner_category,
            "unique_fire_identifier": self.unique_fire_identifier,
        }

    def deserialize(self, data):
        """
        Deserializes a FireIncident from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.object_id = data["object_id"]
            self.x = data["x"]  # pylint: disable=invalid-name
            self.y = data["y"]  # pylint: disable=invalid-name
            self.incident_size = data["incident_size"]
            self.containment_datetime = datetime.fromisoformat(
                data["containment_datetime"]
            )
            self.fire_discovery_datetime = datetime.fromisoformat(
                data["fire_discovery_datetime"]
            )
            self.incident_name = data["incident_name"]
            self.incident_type_category = data["incident_type_category"]
            self.initial_latitude = data["initial_latitude"]
            self.initial_longitude = data["initial_longitude"]
            self.poo_city = data["poo_city"]
            self.poo_county = data["poo_county"]
            self.poo_state = data["poo_state"]
            self.fire_cause_id = data["fire_cause_id"]
            self.poo_landowner_category = data["poo_landowner_category"]
            self.unique_fire_identifier = data["unique_fire_identifier"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid FireIncident: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid FireIncident: body of request contained bad or no data - "
                "Error message: " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our SQLAlchemy tables

    @classmethod
    def all(cls):
        """Returns all of the FireIncidents in the database"""
        logger.info("Processing all FireIncidents")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a FireIncident by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_poo_county(cls, poo_county):
        """Returns all FireInstances with the given poo_county

        Args:
            poo_county (string): the POO County you want to match
        """
        logger.info("Processing poo county query for %s ...", poo_county)
        return cls.query.filter(cls.poo_county == poo_county)
