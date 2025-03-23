import Feature from './node_modules/ol/Feature.js';
import Geolocation from './node_modules/ol/Geolocation.js';
import Map from './node_modules/ol/Map.js';
import View from './node_modules/ol/View.js';
import Point from './node_modules/ol/geom/Point.js';
import TileLayer from './node_modules/ol/layer/Tile.js';
import VectorLayer from './node_modules/ol/layer/Vector.js';
import OSM from './node_modules/ol/source/OSM.js';
import VectorSource from './node_modules/ol/source/Vector.js';
import CircleStyle from './node_modules/ol/style/Circle.js';
import Fill from './node_modules/ol/style/Fill.js';
import Stroke from './node_modules/ol/style/Stroke.js';
import Style from './node_modules/ol/style/Style.js';
import RegularShape from "./node_modules/ol/style/RegularShape.js";
import Overlay from "./node_modules/ol/Overlay.js";
import Select from './node_modules/ol/interaction/Select.js';
import {click} from "./node_modules/ol/events/condition.js";
import {useGeographic} from "./node_modules/ol/proj.js";
import {toLonLat} from './node_modules/ol/proj.js';

useGeographic(); // forces geographic coordinates

// the center and zoom will be changed when location tracking is enabled to focus on the user's position
const view = new View({
    center: [0, 0],
    zoom: 17,
});

const rasterLayer = new TileLayer({
    source: new OSM(),
});

const drawMarkers = new VectorLayer({
    source: new VectorSource({
        features: [],
    })
});

// Creates the overlay used when the user wants to interact with a map marker.
const popContainer = document.getElementById('marker-popup');
const popContent = document.getElementById('marker-popup-content');
const popCloser = document.getElementById('marker-popup-closer');
const markerPopups = new Overlay({
    element: popContainer,
    autoPan: {
        animation: {
            duration: 250,
        },
    },
});

// handles closing the markerPopups
popCloser.onclick = closePopup;

function closePopup() {
    popContainer.style.animation = "popup-exit 0.5s";
    setTimeout(function () {markerPopups.setPosition(undefined);}, 480);
     // removes popup
    popCloser.blur();
    return false; // otherwise returns a href?
}

const map = new Map({
    layers: [
        rasterLayer,
        drawMarkers,
    ],
    target: 'map',
    view: view,
    overlays: [markerPopups],
});

const geolocation = new Geolocation({
    // enableHighAccuracy must be set to true to have the heading value.
    trackingOptions: {
        enableHighAccuracy: true,
    },
    projection: view.getProjection(),
});

// controls how the user's position is visually represented on the map
const positionFeature = new Feature();
positionFeature.setStyle(
    new Style({
        image: new CircleStyle({
            radius: 6,
            fill: new Fill({
                color: '#3399CC',
            }),
            stroke: new Stroke({
                color: '#fff',
                width: 2,
            }),
        }),
    }),
);

let interactableMarkers; // will hold the position of interactable markers

// changes the position of the position indicator on the map (above) to match when the user's position updates
// ternary operator used to create a new Point at the coordinates of the geolocator, if defined, null otherwise
geolocation.on('change:position', function () {
    const coordinates = toLonLat(geolocation.getPosition());
    positionFeature.setGeometry(coordinates ? new Point(coordinates) : null);
    const newPos = positionFeature.getGeometry().getCoordinates();

    // resets list of interactable markers
    interactableMarkers = [];
    // iterate through all markers, checking if they are now within range to interact with.
    const markersOnMap = drawMarkers.getSource().getFeatures();
    console.log("MARKERS: " + markersOnMap);
    for (const currMarker of markersOnMap) {
        const markerPos = currMarker.getGeometry().getCoordinates();
        console.log(markerPos);
        // if the current marker is within range to interact with
        if (isMarkerInRange(markerPos, newPos)) {
            console.log("marker at " + markerPos + " IS interactable.");
            interactableMarkers.push(markerPos);
        } else {
            console.log("marker at " + markerPos + " IS NOT interactable.");
        }
    } 

    // updates the view's centre to the user's new position:
    console.log("centering view on: " + newPos);
    mapView.setCenter(newPos);
    // logs the positions of the interactable markers
    console.log("positions of markers that can be interacted with: ");
    console.log(interactableMarkers);
});

function isMarkerInRange(markerPos, playerPos) {
    const distance = Math.sqrt((markerPos[0] - playerPos[0])**2 + (markerPos[1] - playerPos[1])**2);
    console.log("distance: " + distance);
    if (distance <= 0.010) { // must be changed back to 0.001 (or similar), is set higher for testing purposes
        return true;
    } else {
        return false;
    }
}

let userFeatures = [positionFeature];

map.addLayer( new VectorLayer({
                source: new VectorSource({
                    features: userFeatures,
                }),
}));


// gets the view property of the map, which we can use to set the center and zoom
const mapView = map.getView();

function enableGeolocation() {
    if ("geolocation" in navigator) {
        geolocation.setTracking(true); // will automatically prompt user
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

const jsonMarkers = document.getElementById("marker-data").innerHTML;
console.log(jsonMarkers);
const markersObject = JSON.parse(jsonMarkers);
console.log(markersObject);

// these are updated when a marker is collected, so cannot be constant
let collected = document.getElementById("user-inv").innerHTML.split(',');
console.log("Initial collected data: ", collected);

function prepopulateMap() {
    // prepopulates the map with markers based on the data in markers.json
    for (const currMarker of markersObject.markers) {
        console.log("creating marker of id: " + currMarker.idno);
        createMarkerFromJSON(currMarker);
    }
}

function createMarkerFromJSON(data) {
    console.log("Adding new marker...");


    let markerShape;
    let markerColor;

    // converts chosen color to hex value
    console.log("Setting color...");
    console.log("color from form: " + data.color);
    switch (data.color) {
        case "red":
            console.log("case: red");
            markerColor = '#FF0000';
            break;
        case "green":
            console.log("case: green");
            markerColor = '#00FF00';
            break;
        case "blue":
            console.log("case: blue");
            markerColor = '#0000FF';
            break;
        case "yellow":
            console.log("case: yellow");
            markerColor = '#FFFF00';
            break;
    }

    // creates the object for the marker's shape, using the shape and color specified by the user
    console.log("Setting shape...");
    console.log("shape from form: " + data.shape);
    switch (data.shape) {
        case "circle":
            console.log("case: circle");
            markerShape = new CircleStyle({
                radius: 6,
                fill: new Fill({
                    color: markerColor,
                }),
                stroke: new Stroke({
                    color: '#000',
                    width: 2,
                })
            });
            break;
        case "square":
            console.log("case: square");
            markerShape = new RegularShape({
                fill: new Fill({
                    color: markerColor,
                }),
                stroke: new Stroke({
                    color: '#000',
                    width: 2,
                }),
                points: 4,
                radius: 6,
                angle: Math.PI / 4,
            });
            break;
        case "triangle":
            console.log("case: triangle");
            markerShape = new RegularShape({
                fill: new Fill({
                    color: markerColor,
                }),
                stroke: new Stroke({
                    color: '#000',
                    width: 2,
                }),
                points: 3,
                radius: 10,
                rotation: Math.PI / 4,
                angle: 0,
            });
            break;
    }

    // creates the marker
    console.log("Making marker object...");
    console.log("Shape and color:");
    console.log(markerShape);
    console.log(markerColor);
    const marker = new Feature({
        type: "marker",
    });
    marker.setStyle(new Style({
        image: markerShape,
    }));
    console.log(marker);

    console.log("Adding marker to vector layer...");
    drawMarkers.getSource().addFeature(marker);

    // places the marker on the map
    console.log("Placing marker on map...");
    console.log("Latitude: " + data.latitude);
    console.log("Longitude: " + data.longitude);
    const markerPos = [data.latitude, data.longitude];
    marker.setGeometry(new Point(markerPos));
}

// prompt user to enable geolocation
enableGeolocation();

// adding interactions to the map

// allowing selection of features (for markers)

// defines how a selected mark is styled
const selectedMarkerStyle = new Style({
    image: new CircleStyle({
        radius: 6,
        fill: new Fill({
            color: '#001000',
        }),
        stroke: new Stroke({
            color: '#00FAAA',
            width: 3,
        }),
    })

});

// features on the drawMarkers layer can be selected, which will restyle them (while selected) according to the
// selectedMarkerStyle
const clickSelection = new Select({
    condition: click,
    layers: [drawMarkers],
    style: selectedMarkerStyle,
});
map.addInteraction(clickSelection);
// when a marker is clicked:
clickSelection.on('select', function (e) {
    // add popup on marker
    console.log(e);

    const marker = e.selected[0];
    // avoids a popup appearing when a marker is deselcted by clicking on the map, instead of a marker
    if (marker !== undefined) { 
        const markerPos = marker.getGeometry().getCoordinates();
        
        // gets the details of the marker selected
        let markerDetails;
        for (const currMarkerDetails of markersObject.markers) {
            if ((currMarkerDetails.latitude == markerPos[0]) && (currMarkerDetails.longitude == markerPos[1])) {
                markerDetails = currMarkerDetails;
            }
        }

        // checks if the marker selected is interactable
        let interactable = false;
        for (const subArr of interactableMarkers) {
            console.log(subArr + " " + markerPos);
            if ((subArr[0] == markerPos[0]) && (subArr[1] == markerPos[1])) {
                interactable = true;
            }
        }

        console.log("popup position: " + markerPos);

        if (interactable) {
            console.log("Selected interactable marker.");

            // creates an array of the markers that have already been collected today
            let userInvList = collected

            popContent.innerHTML = '<h3><code>' + markerDetails.name +'</code></h3> <p>Selected Marker at: </p><code>' + markerPos + '</code>' + '<button id="popup-button">Collect</button>';
            const popupButton = document.getElementById("popup-button");
            if (!userInvList.includes(markerDetails.idno)) {
                popupButton.addEventListener("click", collectFromMarker);
            } else {
                // restyle button to show it's already been collected
                popupButton.setAttribute("disabled", "") // boolean attribute, can be set to empty string to be true

            }
        } else {
            console.log("Selected un-interactable marker.");
            popContent.innerHTML = '<h3><code>' + markerDetails.name +'</code></h3><p>Selected Marker at: </p><code>' + markerPos + '</code>';
        }

        // called here to ensure the player does not softlock into a situation where all markers are collected and cannot reset
        // as the update call would otherwise only be called when a marker is collected
        ajaxCallUpdateInvData()

        function collectFromMarker() {
            switch (markerDetails.color) {
                case "green":
                    console.log("GREEN");
                    $(document).ready(ajaxCallCollectMarker("claim_green_marker"));
                    $(document).ready(ajaxCallUpdateInvData);
                    closePopup();
                    break;
                case "red":
                    console.log("RED");
                    $(document).ready(ajaxCallCollectMarker("claim_red_marker"));
                    $(document).ready(ajaxCallUpdateInvData);
                    closePopup();
                    break;
                case "blue":
                    console.log("BLUE");
                    $(document).ready(ajaxCallCollectMarker("claim_blue_marker"));
                    $(document).ready(ajaxCallUpdateInvData);
                    closePopup();
                    break;
            }
        }

        function ajaxCallCollectMarker(funcUrl) {
            $.ajax({
                url: funcUrl,
                type: 'POST',
                data: {'marker_id': markerDetails.idno},
                success: function(response) {
                    console.log("sent marker id to view successfully");
                    console.log("Response: ", response);
                },
                error: function(error) {
                    console.log("encountered error when sending marker id: ", error);
                }
            })
            .done(response => {console.log(response)}) // we don't need to do anything with the response
        }

        function ajaxCallUpdateInvData() {
            $.ajax({
                url: "update_inv_on_page",
                type: 'GET'
            })
            .done(response => {
                const collectedObj = response;
                collected = collectedObj.collected
            })
        }

        markerPopups.setPosition(markerPos);
        popContainer.style.animation = "popup-enter 0.5s";
    }
});

prepopulateMap();
