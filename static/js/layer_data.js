var battlefieldsIcon = L.ExtraMarkers.icon(
	{"innerHTML": "<img src='static/img/Challenge_Icon.svg' style='margin: 8px'>", "markerColor": "orange"}
);

var buildingPreservationNoticesIcon = L.ExtraMarkers.icon(
	{"icon": "fa-building-flag", "markerColor": "teal", "prefix": "fa", "svg": true}
);

var certificatesOfImmunityIcon = L.ExtraMarkers.icon(
	{"icon": "fa-scroll", "markerColor": "tan", "prefix": "fa", "svg": true}
);

var listedBuildingsIcon = L.ExtraMarkers.icon(
	{"icon": "fa-building", "markerColor": "#006fb2", "prefix": "fa", "svg": true}
);

var parksGardensIcon = L.ExtraMarkers.icon(
	{"icon": "fa-tree", "markerColor": "green", "prefix": "fa", "svg": false}
);

var protectedWreckSitesIcon = L.ExtraMarkers.icon(
	{"icon": "fa-anchor", "markerColor": "purple", "prefix": "fa", "svg": true}
);

var registeredLandscapesWalesIcon = L.ExtraMarkers.icon(
	{"icon": "fa-mountain", "markerColor": "Olive", "prefix": "fa", "svg": true}
);

var scheduledMonumentsIcon = L.ExtraMarkers.icon(
	{"icon": "fa-monument", "markerColor": "#a32d2f", "prefix": "fa", "svg": true}
);

var worldHeritageSitesIcon = L.ExtraMarkers.icon(
	{"icon": "fa-certificate", "markerColor": "grey", "prefix": "fa", "svg": true}
);

var deDesignatedIcon = L.ExtraMarkers.icon(
	{"icon": "fa-ban", "markerColor": "black", "prefix": "fa", "svg": false}
);


const layerData = [
    {
        "variable_prefix": "battlefields",
        "layer": "marker_cluster_battlefields",
        "icon": battlefieldsIcon,
        "noun": "Battlefield",
    },
    {
        "variable_prefix": "buildingPreservationNotices",
        "layer": "marker_cluster_building_preservation_notices",
        "icon": buildingPreservationNoticesIcon,
        "noun": "Building Preservation Notice",
    },
    {
        "variable_prefix": "certificatesOfImmunity",
        "layer": "marker_cluster_certificates_of_immunity",
        "icon": certificatesOfImmunityIcon,
        "noun": "Certificate of Immunity",
    },
    {
        "variable_prefix": "listedBuildings",
        "layer": "marker_cluster_listed_buildings",
        "icon": listedBuildingsIcon,
        "noun": "Listed Building",
    },
    {
        "variable_prefix": "parksGardens",
        "layer": "marker_cluster_parks_and_gardens",
        "icon": parksGardensIcon,
        "noun": "Park and Garden",
    },
    {
        "variable_prefix": "protectedWreckSites",
        "layer": "marker_cluster_protected_wreck_sites",
        "icon": protectedWreckSitesIcon,
        "noun": "Protected Wreck",
    },
    {
        "variable_prefix": "registeredLandscapesWales",
        "layer": "marker_cluster_registered_landscapes",
        "icon": registeredLandscapesWalesIcon,
        "noun": "Registered Landscape",
    },
    {
        "variable_prefix": "scheduledMonuments",
        "layer": "marker_cluster_scheduled_monuments",
        "icon": scheduledMonumentsIcon,
        "noun": "Scheduled Monument",
    },
    {
        "variable_prefix": "worldHeritageSites",
        "layer": "marker_cluster_world_heritage_sites",
        "icon": worldHeritageSitesIcon,
        "noun": "World Heritage Site",
    },
    {
        "variable_prefix": "deDesignated",
        "layer": "marker_cluster_de_designated",
        "icon": deDesignatedIcon,
        "noun": "De-designated Site",
    },
]
