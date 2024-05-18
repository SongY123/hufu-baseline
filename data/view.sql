CREATE VIEW osm_a(id, location) AS
SELECT osm_a_0.id,
       osm_a_0.location
FROM osm_a_0
UNION
SELECT osm_a_1.id,
       osm_a_1.location
FROM osm_a_1
UNION
SELECT osm_a_2.id,
       osm_a_2.location
FROM osm_a_2
UNION
SELECT osm_a_3.id,
       osm_a_3.location
FROM osm_a_3
UNION
SELECT osm_a_4.id,
       osm_a_4.location
FROM osm_a_4
UNION
SELECT osm_a_5.id,
       osm_a_5.location
FROM osm_a_5;