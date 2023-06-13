# Workpath-Tableau Connector

## About

Example application to update values of KPIs or Key Results in Workpath from values in a Tableau view. This application is aimed at Workpath customers who may want to:

* Study this code and use it as an example for their own custom integration with Workpath
* Download and possibly modify this code to run on their own infrastructure (which they are free to do as per the [MIT license](LICENSE))

Note that to make use of this application, the following are required:

* A Workpath subscription,
* Software development expertise,
* Clearance and support from your internal IT department.

Also note that this application is not part of any contractual agreement about a subscription of Workpath.

## Installation

A supported version of Python 3 is required. Here is one way to install the application natively:

1. Clone this git repository, and navigate to it
2. Create a virtual environment: `python3 -m venv venv && . venv/bin/activate`
3. Install this app in development mode: `pip install -e`

## Configuration

1. Create a Personal Access Token (PAT) in Tableau, from a user with read access to the views you'd like to sync from. Expose the variables `PAT_NAME` and `PAT` as environment variables to this application
2. Create a Workpath Connect API Token. Expose it on the environment as `CONNECT_TOKEN`
3. Create a copy of [connected_kpis.yml](connected_kpis.yml), and list all the KPIs and/or Key Results you would want to sync. Reach out to Workpath support to help populate this file

⚠️ Please follow Tableau security best practices for configuring users for access to Tableau, and creating and storing PATs.

## Usage

```sh
# Remember to expose PAT_NAME, PAT and CONNECT_TOKEN via environment variables
sync_kpis --tableau_domain tableau.acme.com --site_id acme --kpis_path your_kpis.yml

# To see all options:
sync_kpis --help
```

This project additionally contains some helper scripts to explore views, KPIs and goals in Tableau and Workpath, which is useful to populate [connected_kpis.yml](connected_kpis.yml) with your actual configuration:

```sh
# To list all KPIs and Key Results available through Connect API, helpful for identifying IDs:
list_kpis
list_goals

# To list all views available in Tableau:
list_views
```

## Limitations

- It is not always possible to access all metrics you see in a Tableau view via its API, especially for dashboards composed of multiple sheets of data. It's recommended to ask your data analysts to construct a specific view for this script to read from.
- This script can only sync data from one Tableau site at a time; you will need separate YML configuration files for different Tableau sites.
- Tableau filters are not yet supported.

## See also

- [Workpath Connect API documentation](https://developer.workpath.com/)
- [Tableau Server Client documentation](https://tableau.github.io/server-client-python/docs/)