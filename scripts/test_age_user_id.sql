LOAD 'age';

SET search_path = ag_catalog, "$user", public;

SELECT *
FROM cypher(
    'pokec',
    $$
    MATCH (u:User)
    RETURN u.id
    LIMIT 3
    $$
) AS result(value agtype);