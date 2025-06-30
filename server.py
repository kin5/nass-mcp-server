import argparse
from typing_extensions import TypedDict
import httpx
import os
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()

########################################################
# Definitions
########################################################
URL = "https://quickstats.nass.usda.gov/api/{endpoint}"
API_KEY = os.getenv("NASS_API_KEY")

########################################################
# Argument Types
########################################################
class ParameterQuery(TypedDict):
    param: str

class CommodityQuery(TypedDict):
    sector_desc: str | None
    group_desc: str | None
    commodity_desc: str | None

class LocationQuery(TypedDict):
    agg_level_desc: str | None
    state_name: str | None
    county_name: str | None
    region_desc: str | None
    watershed_desc: str | None
    zip_5: str | None
    country_code: str | None

class TimeYearQuery(TypedDict):
    year: str

class TimeLoadTimeQuery(TypedDict):
    load_time: str

class TimeFrequencyQuery(TypedDict):
    freq_desc: str
    begin_code: str
    end_code: str
    reference_period_desc: str | None
    week_ending: str | None

TimeQuery = TimeYearQuery | TimeLoadTimeQuery | TimeFrequencyQuery

########################################################
# API
########################################################
async def api(endpoint: str, params: dict) -> dict:
    url = URL.format(endpoint=endpoint)
    full_params = {"key": API_KEY, "format": "json", **params}
    response = await httpx.get(url, params=full_params)

    if not response.is_success:
        return {
            "status": "error",
            "message": response.text,
            "http_status": response.status_code,
        }

    return response.json()

########################################################
# MCP Server
########################################################
mcp = FastMCP(
    "USDA NASS API MCP Server",
    host="0.0.0.0",
    port=8000,
)

########################################################
# Tools
########################################################
@mcp.tool()
async def get_data(commodity: CommodityQuery, location: LocationQuery, time: TimeQuery) -> dict:
    """
    Get all available data for a given commodity, location, and time.

    Args:
        commodity: The commodity to get the data for.
        location: The location to get the data for.
        time: The time to get the data for.

    Returns:
        A dictionary with the data for the given commodity.
    """
    return await api("get_API", {**commodity, **location, **time})

@mcp.tool()
async def get_counts(commodity: CommodityQuery, location: LocationQuery, time: TimeQuery) -> dict:
    """
    Get the number, or count, of units of a given commodity for a location and time.

    Args:
        commodity: The commodity to get the counts for.
        location: The location to get the counts for.
        time: The time to get the counts for.

    Returns:
        A dictionary with one key, "count", and a value of the number of units of the given commodity.
    """
    return await api("get_counts", {**commodity, **location, **time})

@mcp.tool()
async def get_param_values(parameter: ParameterQuery) -> dict:
    """
    Get all possible values of a query parameter by its name.

    Args:
        parameter: The name of the parameter to get the values for.

    Returns:
        A dictionary with the parameter name and all possible values as a list.
    """
    return await api("get_param_values", {**parameter})

########################################################
# __main__
########################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--transport", choices=["streamable-http", "stdio"], default="streamable-http")
    args = parser.parse_args()

    mcp.run(args.transport)