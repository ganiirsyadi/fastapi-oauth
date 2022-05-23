import logging
from datetime import datetime
from time import gmtime, strftime

from logstash_async.handler import (AsynchronousLogstashHandler,
                                    LogstashFormatter)

# Create the logger and set it's logging level
logger = logging.getLogger("logstash")
logger.setLevel(logging.DEBUG)        

# Create the handler
handler = AsynchronousLogstashHandler(
    host='dd7f32ad-362c-4939-b5f8-4c22ef432917-ls.logit.io', 
    port=26691, 
    database_path='')
# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter()
handler.setFormatter(formatter)

# Assign handler to the logger
logger.addHandler(handler)
