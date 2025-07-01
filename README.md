# MCP Server for USDA NASS API
The [USDA National Agricultural Statistics Service API](https://quickstats.nass.usda.gov/api), known as *Quick Stats*, contains survey and census data on United States agricultural production.

### NASS API access
Request an API key [here](https://quickstats.nass.usda.gov/api).

## Tools
### `get_full_dataset(query: Query) -> str`

Get all available data for a given commodity, location, and time.

**Arguments:**
- `query` (`Query`): Dictionary with three keys, `"commodity"`, `"location"`, and `"time"`, each with a dictionary of parameter and value pairs.

**Returns:**
- `str`: Full response text as a string

---

### `get_db_record_count(query: Query) -> str`

Get the number, or count, of database records of a given commodity for a location and time.

**Arguments:**
- `query` (`Query`): Dictionary with three keys, `"commodity"`, `"location"`, and `"time"`, each with a dictionary of parameter and value pairs.

**Returns:**
- `str`: String of JSON data with one key, `"count"`, and a value of the number of records.

---

### `get_param_values(query: ParamQuery) -> str`

Get all possible values of a query parameter by its name.

**Arguments:**
- `parameter` (`ParameterQuery`): Dictionary with one key, `"param"`, and a value of the parameter name to get the values for.

**Returns:**
- `str`: String of JSON data with the parameter names and all their possible values as a list.


## Getting started
I highly recommend using [uv](https://github.com/astral-sh/uv) for package and virtual environment management.

### Docker
The `Dockerfile` is setup to run the MCP server with default settings. Using `make`, you can build an image and run a container:
- `build`: build the image from `Dockerfile`
- `run`: run the MCP server with default settings (e.g. `localhost`, `8000:8000`)

### The short way
#### Setup command
If you have `make`, `uv`, and are on macOS/Linux, running `make setup` should be all you need to get started with the project. 

### The long way
#### Installation
Activate your virtual environment and:
```shell
pip install -r requirements.txt
```

#### .env
Copy the `.env.example` to a `.env` file. Replace the value of `NASS_API_KEY` with your NASS API key.

## Configuration
There are several configuration options for changing functionality of the MCP server.

The following configurations are available as **environment variables**:
| Option         | Values                  | Default    | Description                                                            |
|----------------|-------------------------|------------|------------------------------------------------------------------------|
| NASS_API_KEY   | `string`                |            | Your NASS API key                                                      |
| NASS_MCP_HOST  | `string`                | `0.0.0.0`  | The host to run the MCP server on                                      |
| NASS_MCP_PORT  | `integer`               | `8000`     | The port to run the MCP server on                                      |
| NASS_MCP_FORMAT| `CSV` or `JSON` or `XML`| `CSV`      | The format to return the data in from the NASS API `/api_GET` endpoint |
| NASS_ENV       | `production`            |            | A flag for telling the MCP server to skip local dev steps (e.g. `load_dotenv`) |

The following configurations are available as **command line arguments**
| Option                  | Values                               | Default             | Description                           |
|-------------------------|--------------------------------------|---------------------|---------------------------------------|
| `-t` `--transport`      | `streamable-http` or `stdio`         | `streamable-http`   | Transport protocol for the MCP server |