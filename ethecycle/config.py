from os import environ

from ethecycle.util.string_constants import DEBUG


class Config:
    include_extended_properties = False
    debug = DEBUG in environ
    drop_database = False
    extract_only = False
    skip_load_from_db = False
    is_docker_image_build = 'IS_DOCKER_IMAGE_BUILD' in environ
