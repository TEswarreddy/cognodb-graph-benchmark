LOAD 'age';

SET search_path = ag_catalog, "$user", public;

SELECT ag_catalog.create_graph('pokec');