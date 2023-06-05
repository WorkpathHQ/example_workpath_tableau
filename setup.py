import setuptools

setuptools.setup(
    name="workpath_tableau",
    version="0.1",
    author="Workpath GmbH",
    description="Sync KPIs from Tableau to Workpath.",
    install_requires=[
        "pyyaml",
        "requests",
        "tableauserverclient",
    ],
    entry_points={
        "console_scripts": [
            "sync_kpis=workpath_tableau.__main__:sync_kpis",
            "list_views=workpath_tableau.__main__:list_views",
            "list_goals=workpath_tableau.__main__:list_goals",
            "list_kpis=workpath_tableau.__main__:list_kpis",
        ]
    },
)
