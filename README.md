# Workpath-Tableau Connector

## About

Example application to update values of KPIs or Key Results in Workpath from values in a Tableau dashboard.

## Installation

A supported version of Python 3 is required.

1. Clone this git repository, and navigate to it
2. Create a virtual environment: `python3 -m venv venv && . venv/bin/activate`
3. Install this app in development mode: `pip install -e`

## Configuration

1. Create a Personal Access Token in Tableau, from a user with read access to the views you'd like to sync from. Expose the variables `PAT_NAME` and `PAT` as environment variables
2. Create a Workpath Connect API Token. Expose it as `CONNECT_TOKEN`
3. Create a copy of [`connected_kpis.yml`](connected_kpis.yml), and list all the KPIs and/or Key Results you would want to sync. Reach out to Workpath support to help populate this file

## Usage

```sh
# Remember to expose PAT_NAME, PAT and CONNECT_TOKEN via environment variables
sync_kpis --tableau_domain tableau.acme.com --site_id acme --kpis_path your_kpis.yml

# To see all options:
sync_kpis --help

# To list all KPIs and Key Results available through Connect API, helpful for identifying IDs:
list_kpis
list_goals

# To list all views available in Tableau:
list_views
```

## Limitations

- Can only retrieve values visible in a view's CSV export
- Can only sync data from one Tableau site at a time
- Filters are not yet supported

## See also

- [Workpath Connect API documentation](https://developer.workpath.com/)
- [Tableau Server Client documentation](https://tableau.github.io/server-client-python/docs/)