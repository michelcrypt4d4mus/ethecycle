from os import environ

from ethecycle.util.string_constants import DEBUG

IS_TEST_ENV = environ['ETHECYCLE_ENV'] == 'test'


class Config:
    include_extended_properties = False
    debug = DEBUG in environ
    drop_database = False
    extract_only = False
    skip_load_from_db = False
    is_docker_image_build = 'IS_DOCKER_IMAGE_BUILD' in environ
    is_test_env = IS_TEST_ENV
    preserve_csvs = False
    suppress_chain_address_db_collision_warnings = False

    # Hacky way to limit output
    max_rows = 1000 if IS_TEST_ENV else 10000000000
