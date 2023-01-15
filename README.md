# google-mileage-reconstruct

Use this tool to summarize trips taken by car by calendar year.

This tool works with Google Location History data from Google Takeout (https://support.google.com/accounts/answer/3024190?hl=en)

Output is a csv containing:
* startTimestamp (utc)
* endTimestamp (utc)
* start lat
* start lon
* start address
* end lat
* end lon
* end address
* distance (meters)

If address is included in location history data that will be used, otherwise we try to resolve it using reverse geocode lookup (requires google maps API key)

## Setup
1. python3 -m venv .venv
2. source .venv/bin/activate
3. python3 -m pip install -r requirements.txt

### Optional (reverse geocode address resolution):
1. https://developers.google.com/maps/documentation/geocoding/get-api-key
2. set environment variable G_API_KEY