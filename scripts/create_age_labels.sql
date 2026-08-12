LOAD 'age';

SET search_path = ag_catalog, "$user", public;

SELECT create_vlabel('pokec', 'User');

SELECT create_elabel('pokec', 'CONNECTS_TO');