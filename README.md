# Inventory CRUD API

Provides an HTTP API for exposing CRUD style routes against database tables. 

## Developer Interface

### Models
`models/`

`SQLModel`s for each database table are located in the `models/*.py` files. Models with `table=True` will automatically be converted to CRUD routes.

### Router
`router/`

Routes are created dynamically based on the `SQLModel`s found in the `models/` directory. These routes use the format `/category/modelname` to represent each model that is loaded, derived from the following file scheme: `application/models/category/modelname.py`


## Installing

Install requirements first.
```bash
pip install -r requirements.txt
```

Then let `poetry` handle the dependencies for you. Currently we only support postgres (and sqlite, for testing) as a database driver. However, 
```bash
poetry install --no-dev [--extras pgsql]
```

If you are running containers, you probably want to mount the code to the container, rather than writing it to the image. This will prep your image with the dependencies but allow the mounted code to be used for the application. 
```bash
poetry build
pip install -e .
```


## Execution

### Environment File

The `.env` file should contain the following settings
- LOG_LEVEL
- DATABASE_PROTOCOL
- DATABASE_NAME
- DATABASE_USERNAME
- DATABASE_PASSWORD
- DATABASE_HOSTNAME
- DATABASE_PORT

`LOG_LEVEL` will default to `INFO`, and only needs to be set if you require a different logging level. The `DATABASE_*` settings are dependent on the database driver you are using, and may not all be required. You will also need to ensure your database driver is installed.

### Command

If the `host` and `port` values are not provided on the command line, fallback to environment variables `API_HOST` and `API_PORT`

```bash
python -m application [host] [port]
```

## Routes Offered

### Get All
`GET /category/model`

Returns a list of all the entries for the given `model`. Can handle query parameters to allow for searching. Parameters must match the attribute name and type for the given `model`. Does not currently support searching for `null` in attributes.

### Create One
`POST /category/model`

Creates a new instance of the given `model`, automatically assigning an appropriate `id` value. All other values must be passed as JSON in the request body.

### Delete All
`DELETE /category/model`

Deletes all entries for the given `model`. Deletes can be filtered based on query params, in the same way "Get All" works. Does not currently support searching for `null` in attributes. 

### Get One
`GET /category/model/id`

Returns a single instance of the given `model`, based on the `id`. Returns `null` if the `id` does not exist.

### Update One
`PUT /category/model/id`

Updates an instance of the given `model`, based on the `id`. Default values will take precedence on an update if the body does not contain a value for that attribute.

### Delete One
`DELETE /category/model/id`

Deletes an instance of the given `model`, based on the `id`.