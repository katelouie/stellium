"""Integration tests for complete chart calculation."""

import datetime as dt

import pytest

from stellium.core.builder import ChartBuilder
from stellium.core.models import ChartLocation
from stellium.core.native import Native
from stellium.engines.aspects import ModernAspectEngine
from stellium.engines.houses import PlacidusHouses, WholeSignHouses


def test_einstein_chart():
    """Test calculating Einstein's birth chart."""
    birthday = dt.datetime(1879, 3, 14, 11, 30)
    location = "Ulm, Germany"
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .with_aspects(ModernAspectEngine())
        .calculate()
    )

    # Verify chart was calculated
    assert chart.datetime.local_datetime == birthday
    assert "Ulm" in chart.location.name

    # Verify positions
    assert len(chart.positions) > 10

    # Sun should be Pisces
    sun = chart.get_object("Sun")
    assert sun is not None
    assert sun.sign == "Pisces"

    # Verify houses
    assert chart.default_house_system == "Placidus"
    assert len(chart.house_systems["Placidus"].cusps) == 12

    # Verify aspects calculated
    assert len(chart.aspects) > 0


def test_chart_to_dict():
    """Test chart seralization to dictionary."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=0, longitude=0, name="Test")
    native = Native(birthday, location)

    chart = ChartBuilder.from_native(native).calculate()
    data = chart.to_dict()

    assert "datetime" in data
    assert "location" in data
    assert "positions" in data
    assert "house_systems" in data

    # Verify structure
    assert data["location"]["name"] == "Test"
    assert len(data["positions"]) > 0
    assert len(data["house_systems"]["Placidus"]["cusps"]) == 12


def test_different_house_systems():
    """Test that different house systems product different results."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40, longitude=-74)
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses(), WholeSignHouses()])
        .calculate()
    )

    # Different systems, different cusps
    assert chart.house_systems["Placidus"] != chart.house_systems["Whole Sign"]


def test_points_and_nodes_object_types():
    """Test that POINT and NODE object types are correctly assigned."""
    birthday = dt.datetime(2000, 1, 1, 12, 0, tzinfo=dt.UTC)
    location = ChartLocation(latitude=40, longitude=-74, name="Test Location")
    native = Native(birthday, location)

    chart = (
        ChartBuilder.from_native(native)
        .with_house_systems([PlacidusHouses()])
        .with_aspects(ModernAspectEngine())
        .calculate()
    )

    # Test that we have nodes
    nodes = chart.get_nodes()
    assert len(nodes) > 0, "Should have at least one node"

    # Verify True Node and South Node exist
    true_node = chart.get_object("True Node")
    south_node = chart.get_object("South Node")
    assert true_node is not None, "True Node should exist"
    assert south_node is not None, "South Node should exist"

    # Verify they're opposite each other (180 degrees apart)
    node_distance = abs(true_node.longitude - south_node.longitude)
    # Account for wraparound
    if node_distance > 180:
        node_distance = 360 - node_distance
    assert abs(node_distance - 180) < 0.01, "Nodes should be 180 degrees apart"

    # Test that we have points
    points = chart.get_points()
    assert len(points) > 0, "Should have at least one point"

    # Verify Vertex exists and is a POINT type
    vertex = chart.get_object("Vertex")
    assert vertex is not None, "Vertex should exist"
    from stellium.core.models import ObjectType

    assert vertex.object_type == ObjectType.POINT, "Vertex should be POINT type"

    # Verify Mean Apogee (Lilith) exists and is a POINT type
    lilith = chart.get_object("Mean Apogee")
    assert lilith is not None, "Mean Apogee (Lilith) should exist"
    assert lilith.object_type == ObjectType.POINT, "Lilith should be POINT type"

    # Test that aspects include nodes and points
    # Find any aspect involving a node or point
    node_aspects = [
        a
        for a in chart.aspects
        if a.object1.name in ["True Node", "South Node"]
        or a.object2.name in ["True Node", "South Node"]
    ]
    point_aspects = [
        a
        for a in chart.aspects
        if a.object1.name in ["Vertex", "Mean Apogee"]
        or a.object2.name in ["Vertex", "Mean Apogee"]
    ]

    # We should have SOME aspects involving nodes/points (depending on the chart)
    # Just verify the engine doesn't error out - we may or may not have aspects
    # depending on orbs and positions
    print(f"Found {len(node_aspects)} aspects involving nodes")
    print(f"Found {len(point_aspects)} aspects involving points")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
