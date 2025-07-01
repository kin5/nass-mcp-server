import argparse
from typing import Annotated, NotRequired, TypedDict, Literal, List
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

# Due to token savings, I highly recommend using CSV format.
AVAILABLE_FORMATS = ["JSON", "CSV", "XML"]
FORMAT = os.getenv("NASS_API_FORMAT", "CSV")
if FORMAT not in AVAILABLE_FORMATS:
    raise ValueError(f"Invalid format: {FORMAT}. Available formats: {AVAILABLE_FORMATS}")


########################################################
# Types
########################################################
CommodityLiteral = Literal[
    "source_desc",
    "sector_desc",
    "group_desc",
    "commodity_desc",
    "class_desc",
    "prodn_practice_desc",
    "util_practice_desc",
    "statisticcat_desc",
    "unit_desc",
    "short_desc",
    "domain_desc",
    "domaincat_desc",
]

LocationLiteral = Literal[
    "agg_level_desc",
    "state_ansi",
    "state_fips_code",
    "state_alpha",
    "state_name",
    "asd_code",
    "asd_desc",
    "county_ansi",
    "county_code",
    "county_name",
    "region_desc",
    "zip_5",
    "watershed_code",
    "watershed_desc",
    "congr_district_code",
    "country_code",
    "country_name",
    "location_desc",
]

TimeLiteral = Literal[
    "year",
    "freq_desc",
    "begin_code",
    "end_code",
    "reference_period_desc",
    "week_ending",
    "load_time",
]

ParamLiteral = Literal[CommodityLiteral, LocationLiteral, TimeLiteral]

########################################################
# Parameter Types
########################################################
class ParameterQuery(TypedDict):
    param: ParamLiteral

class CommodityQuery(TypedDict):
    """Commodity query schema with all possible parameters and their descriptions."""
    commodity_desc: Annotated[str, "The primary subject of interest (e.g., CORN, CATTLE, LABOR, TRACTORS, OPERATORS)"]
    source_desc: NotRequired[Annotated[str, "Source of data (CENSUS or SURVEY). Census program includes the Census of Ag as well as follow up projects. Survey program includes national, state, and county surveys."]]
    sector_desc: NotRequired[Annotated[str, "Five high level, broad categories useful to narrow down choices (Crops, Animals & Products, Economics, Demographics, and Environmental)."]]
    group_desc: NotRequired[Annotated[str, "Subsets within sector (e.g., under sector = Crops, the groups are Field Crops, Fruit & Tree Nuts, Horticulture, and Vegetables)."]]
    class_desc: NotRequired[Annotated[str, "Generally a physical attribute (e.g., variety, size, color, gender) of the commodity."]]
    prodn_practice_desc: NotRequired[Annotated[str, "A method of production or action taken on the commodity (e.g., IRRIGATED, ORGANIC, ON FEED)."]]
    util_practice_desc: NotRequired[Annotated[str, "Utilizations (e.g., GRAIN, FROZEN, SLAUGHTER) or marketing channels (e.g., FRESH MARKET, PROCESSING, RETAIL)."]]
    statisticcat_desc: NotRequired[Annotated[str, "The aspect of a commodity being measured (e.g., AREA HARVESTED, PRICE RECEIVED, INVENTORY, SALES)."]]
    unit_desc: NotRequired[Annotated[str, "The unit associated with the statistic category (e.g., ACRES, $ / LB, HEAD, $, OPERATIONS)."]]
    domain_desc: NotRequired[Annotated[str, "Generally another characteristic of operations that produce a particular commodity (e.g., ECONOMIC CLASS, AREA OPERATED, NAICS CLASSIFICATION, SALES). For chemical usage data, the domain describes the type of chemical applied to the commodity. The domain = TOTAL will have no further breakouts; i.e., the data value pertains completely to the short_desc."]]
    domaincat_desc: NotRequired[Annotated[str, "Categories or partitions within a domain (e.g., under domain = Sales, domain categories include $1,000 TO $9,999, $10,000 TO $19,999, etc)."]]

class LocationQuery(TypedDict):
    """Location query schema with all possible parameters and their descriptions."""
    agg_level_desc: NotRequired[Annotated[str, "Aggregation level or geographic granularity of the data (e.g., State, Ag District, County, Region, Zip Code)."]]
    state_ansi: NotRequired[Annotated[str, "American National Standards Institute (ANSI) standard 2-digit state codes."]]
    state_fips_code: NotRequired[Annotated[str, "NASS 2-digit state codes; include 99 and 98 for US TOTAL and OTHER STATES, respectively; otherwise match ANSI codes."]]
    state_alpha: NotRequired[Annotated[str, "State abbreviation, 2-character alpha code."]]
    state_name: NotRequired[Annotated[str, "State full name."]]
    asd_code: NotRequired[Annotated[str, "NASS defined county groups, unique within a state, 2-digit ag statistics district code."]]
    asd_desc: NotRequired[Annotated[str, "Ag statistics district name."]]
    county_ansi: NotRequired[Annotated[str, "ANSI standard 3-digit county codes."]]
    county_code: NotRequired[Annotated[str, "NASS 3-digit county codes; includes 998 for OTHER (COMBINED) COUNTIES and Alaska county codes; otherwise match ANSI codes."]]
    county_name: NotRequired[Annotated[str, "County name."]]
    region_desc: NotRequired[Annotated[str, "NASS defined geographic entities not readily defined by other standard geographic levels. A region can be a less than a state (Sub-State) or a group of states (Multi-State), and may be specific to a commodity."]]
    zip_5: NotRequired[Annotated[str, "US Postal Service 5-digit zip code."]]
    watershed_code: NotRequired[Annotated[str, "US Geological Survey (USGS) 8-digit Hydrologic Unit Code (HUC) for watersheds."]]
    watershed_desc: NotRequired[Annotated[str, "Name assigned to the HUC."]]
    congr_district_code: NotRequired[Annotated[str, "US Congressional District 2-digit code."]]
    country_code: NotRequired[Annotated[str, "US Census Bureau, Foreign Trade Division 4-digit country code, as of April, 2007."]]
    country_name: NotRequired[Annotated[str, "Country name."]]
    location_desc: NotRequired[Annotated[str, "Full description for the location dimension."]]

class TimeYearQuery(TypedDict):
    """Schema for querying data by year."""
    year: Annotated[str, "The numeric year of the data."]

class TimeLoadTimeQuery(TypedDict):
    """Schema for querying data by database load time."""
    load_time: Annotated[str, "Date and time indicating when record was inserted into Quick Stats database."]

class TimePeriodQuery(TypedDict):
    """Schema for querying data by frequency, begin code, end code, reference period, and week ending."""
    freq_desc: Annotated[str, "Length of time covered (Annual, Season, Monthly, Weekly, Point in Time). Monthly often covers more than one month. Point in Time is as of a particular day."]
    begin_code: Annotated[str, "If applicable, a 2-digit code corresponding to the beginning of the reference period (e.g., for freq_desc = Monthly, begin_code ranges from 01 (January) to 12 (December))."]
    end_code: Annotated[str, "If applicable, a 2-digit code corresponding to the end of the reference period (e.g., the reference period of Jan thru Mar will have begin_code = 01 and end_code = 03)."]
    reference_period_desc: NotRequired[Annotated[str, "The specific time frame, within a freq_desc."]]
    week_ending: NotRequired[Annotated[str, "Week ending date, used when freq_desc = Weekly."]]

class Query(TypedDict):
    commodity: Annotated[CommodityQuery, "Dictionary of one commodity parameter and value pair"]
    location: Annotated[LocationQuery, "Dictionary of location parameter and value pairs"]
    time: Annotated[TimeYearQuery | TimeLoadTimeQuery | TimePeriodQuery, "Dictionary of time parameter and value pairs"]

########################################################
# API
########################################################
async def api(endpoint: str, params: dict) -> dict:
    url = URL.format(endpoint=endpoint)
    full_params = {"key": API_KEY, **params}
    response = httpx.get(url, params=full_params)

    if not response.is_success:
        return {
            "status": "error",
            "message": response.text,
            "http_status": response.status_code,
        }

    if "json" in response.headers.get("content-type", "").lower():
        return response.json()
        
    return response.text

########################################################
# MCP Server
########################################################
mcp = FastMCP(
    "USDA NASS API MCP Server",
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", 8000),
)

########################################################
# Resources
########################################################
@mcp.resource("nass://parameter_names", title="Parameter Names", description="List of all possible query parameter names")
def get_parameter_names() -> List[str]:
    """List of all possible query parameter names.

    Args:
        None

    Returns:
        A list of strings, each representing a parameter name.
    """
    return [
        "source_desc",
        "sector_desc",
        "group_desc",
        "commodity_desc",
        "class_desc",
        "prodn_practice_desc",
        "util_practice_desc",
        "statisticcat_desc",
        "unit_desc",
        "short_desc",
        "domain_desc",
        "domaincat_desc",
        "agg_level_desc",
        "state_ansi",
        "state_fips_code",
        "state_alpha",
        "state_name",
        "asd_code",
        "asd_desc",
        "county_ansi",
        "county_code",
        "county_name",
        "region_desc",
        "zip_5",
        "watershed_code",
        "watershed_desc",
        "congr_district_code",
        "country_code",
        "country_name",
        "location_desc",
        "year",
        "freq_desc",
        "begin_code",
        "end_code",
        "reference_period_desc",
        "week_ending",
        "load_time",
    ]

@mcp.resource("nass://operator_names", title="Operator Names", description="List of operators that can be appended to parameter names in a query")
def get_operator_names() -> List[str]:
    """Operators that can be used in a query by appending them to parameter names to filter results.

    Examples:
        __LE = less than or equal to
        __LT = less than
        __GT = greater than
        __GE = greater than or equal to
        __LIKE = contains
        __NOT_LIKE = does not contain
        __NE = not equal to

    Args:
        None

    Returns:
        A list of strings, each representing an operator.
    """
    return [
        "__LE",
        "__LT",
        "__GT",
        "__GE",
        "__LIKE",
        "__NOT_LIKE",
        "__NE",
    ]

########################################################
# Tools
########################################################
@mcp.tool()
async def get_full_dataset(query: Query) -> dict:
    """Get all available data for a given commodity, location, and time.

    Args:
        query: Dictionary with three keys, "commodity", "location", and "time", each with a dictionary of parameter and value pairs.

    Returns:
        A dictionary with the data for the given commodity.
    """
    params = {
        "format": FORMAT,
        **query["commodity"],
        **query["location"],
        **query["time"],
    }
    return await api("api_GET", params)

@mcp.tool()
async def get_db_record_count(query: Query) -> dict:
    """Get the number, or count, of database records of a given commodity for a location and time.

    Args:
        query: Dictionary with three keys, "commodity", "location", and "time", each with a dictionary of parameter and value pairs.

    Returns:
        A dictionary with one key, "count", and a value of the number of records.
    """
    params = {
        **query["commodity"],
        **query["location"],
        **query["time"],
    }
    return await api("get_counts", params)

@mcp.tool()
async def get_param_values(parameter: ParameterQuery) -> dict:
    """Get all possible values of a query parameter by its name.

    Args:
        parameter: Dictionary with one key, "param", and a value of the parameter name to get the values for.

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