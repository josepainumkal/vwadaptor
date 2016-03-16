from flask_cloudy import Storage
from config import config


storage_extra = config.STORAGE_EXTRA
storage = Storage(provider=config.STORAGE_PROVIDER, key=STORAGE_KEY,
                  secret=config.STORAGE_SECRET, container=config.STORAGE_CONTAINER,
                  allowed_extensions=config.STORAGE_ALLOWED_EXTENSIONS,**storage_extra)
