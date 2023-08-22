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
FireIncident Service
"""

from flask import jsonify, request, url_for, abort
from service.models import FireIncident
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/healthcheck")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="FireIncident REST API Service",
            version="1.0",
            paths=url_for("list_fire_incidents", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL FIRE INCIDENTS
######################################################################
@app.route("/fires", methods=["GET"])
def list_fire_incidents():
    """Returns all of the FireIncidents"""
    app.logger.info("Request for fire_incident list")
    fire_incidents = []
    poo_county = request.args.get("poo_county")
    if poo_county:
        fire_incidents = FireIncident.find_by_poo_county(poo_county)
    else:
        fire_incidents = FireIncident.all()

    results = [fire_incident.serialize() for fire_incident in fire_incidents]
    app.logger.info("Returning %d fire_incidents", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A FIRE INCIDENT
######################################################################
@app.route("/fires/<int:object_id>", methods=["GET"])
def get_fire_incidents(object_id):
    """
    Retrieve a single FireIncident

    This endpoint will return a FireIncident based on it's id
    """
    app.logger.info("Request for fire incident with id: %s", object_id)
    fire_incident = FireIncident.find(object_id)
    if not fire_incident:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"FireIncident with id '{object_id}' was not found.",
        )

    app.logger.info("Returning fire incident: %s", str(fire_incident))
    return jsonify(fire_incident.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW FIRE INCIDENT
######################################################################
@app.route("/fires", methods=["POST"])
def create_fire_incidents():
    """
    Creates a FireIncident
    This endpoint will create a FireIncident based the data in the body that is posted
    """
    app.logger.info("Request to create a fire incident")
    check_content_type("application/json")
    fire_incident = FireIncident()
    fire_incident.deserialize(request.get_json())
    fire_incident.create()
    message = fire_incident.serialize()
    location_url = url_for(
        "get_fire_incidents", object_id=fire_incident.object_id, _external=True
    )

    app.logger.info("FireIncident with ID [%s] created.", fire_incident.object_id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING FIRE INCIDENT
######################################################################
@app.route("/fires/<int:object_id>", methods=["PUT"])
def update_fire_incidents(object_id):
    """
    Update a FireIncident

    This endpoint will update a FireIncident based the body that is posted
    """
    app.logger.info("Request to update fire incident with id: %s", object_id)
    check_content_type("application/json")

    fire_incident = FireIncident.find(object_id)
    if not fire_incident:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"FireIncident with id '{object_id}' was not found.",
        )

    fire_incident.deserialize(request.get_json())
    fire_incident.object_id = object_id
    fire_incident.update()

    app.logger.info("FireIncident with ID [%s] updated.", fire_incident.object_id)
    return jsonify(fire_incident.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A FIRE INCIDENT
######################################################################
@app.route("/fires/<int:object_id>", methods=["DELETE"])
def delete_fire_incidents(object_id):
    """
    Delete a FireIncident

    This endpoint will delete a FireIncident based the id specified in the path
    """
    app.logger.info("Request to delete fire incident with id: %s", object_id)
    fire_incident = FireIncident.find(object_id)
    if fire_incident:
        fire_incident.delete()

    app.logger.info("FireIncident with ID [%s] delete complete.", object_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
