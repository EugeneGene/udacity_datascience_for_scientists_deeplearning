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
Test Factory to make fake objects for testing
"""
from datetime import timezone
import datetime
import factory
from factory.fuzzy import FuzzyChoice, FuzzyFloat, FuzzyInteger, FuzzyDateTime
from service.models import FireIncident


class FireIncidentFactory(factory.Factory):
    """Creates fake fire data"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = FireIncident

    object_id = factory.Sequence(lambda n: n + 300000)
    x = FuzzyFloat(-90.0, 90.0)
    y = FuzzyFloat(-90.0, 90.0)
    incident_size = FuzzyFloat(0.0, 1000000.0)
    containment_datetime = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=timezone.utc))
    fire_discovery_datetime = FuzzyDateTime(datetime.datetime(2008, 1, 1, tzinfo=timezone.utc))
    incident_name = FuzzyChoice(choices=["Santa Anna, CA", "Santa Monica, CA", "Venice, CA"])
    incident_type_category = FuzzyChoice(choices=["WF", "RX"])
    initial_latitude = FuzzyFloat(0.0, 180.0)
    initial_longitude = FuzzyFloat(0.0, 180.0)
    poo_city = FuzzyChoice(choices=["Santa Clarita", "Los Angeles"])
    poo_county = FuzzyChoice(choices=["Los Angeles"])
    poo_state = FuzzyChoice(choices=["US-CA"])
    fire_cause_id = FuzzyInteger(0, 3)
    poo_landowner_category = FuzzyChoice(choices=["private", "federal", "other"])
    unique_fire_identifier = FuzzyChoice(choices=["1994-AZCRA-000037", "1992-HIHKP-009203"])
