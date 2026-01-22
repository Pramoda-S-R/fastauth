import logging

logging.getLogger("fastauth").addHandler(logging.NullHandler())
logging.getLogger("fastauth.audit").addHandler(logging.NullHandler())
