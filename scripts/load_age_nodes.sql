LOAD 'age';

SET search_path = ag_catalog, "$user", public;

SELECT load_labels_from_file(
    'pokec',
    'User',
    'age_data/users.csv'
);