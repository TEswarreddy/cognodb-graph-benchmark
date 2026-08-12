LOAD 'age';

SET search_path = ag_catalog, "$user", public;

SELECT load_edges_from_file(
    'pokec',
    'CONNECTS_TO',
    'age_data/connects_to.csv'
);