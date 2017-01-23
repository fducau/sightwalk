// Initialize map and default map center
var mymap = L.map('mapid');
var mapCenter = [40.773342, -73.970264];
var deaultZoom = 13;

// Initialize path markers
var originMarker;
var destinationMarker;

var shortestPath;
var shortestObject;

var interestingPaths;
var interestingObjects;

var scoring;

var highlighted = { color: "#f24753", weight: 4, opacity: 0.8};
var normal = { color: "#f24753", weight: 4, opacity: 0.30};
var shortestStyle = {weight: 4, opacity: 0.9};

L.tileLayer('https://api.mapbox.com/styles/v1/mvp291/civyo8ort002t2jltkixo4bju/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibXZwMjkxIiwiYSI6ImNpdnlvNmp5ajAyeXUyeG8ybHhzZWlsMjQifQ.BPR8SV8UcdAIIWVXjnOl-Q', 
    { attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>'}).addTo(mymap);

mymap.on('click', onMapClick);

function drawShortestPath() {
    if (shortestObject) {
        if (shortestPath) {
            mymap.removeLayer(shortestPath);
        }

        shortestPath = L.geoJSON(shortestObject.geojson, {
            style: function (feature) {
                return shortestStyle;
            }
        }).addTo(mymap);
        var tooltip = "<b>Shortest Path</b>";
        tooltip += "<br><b>distance: </b>" + shortestObject.distance.toFixed(2) + " miles</br>";
        shortestPath.bindTooltip(tooltip);
    }
}

function clearPaths() {
    if (interestingPaths) {
        for (var j = 0; j < interestingPaths.length; j++){
            mymap.removeLayer(interestingPaths[j]);
        }
        interestingPaths = null;
    }
}

function pathEvents() {
    for (var j = 0; j < interestingPaths.length; j++){
        interestingPaths[j].setStyle(normal);
        interestingPaths[j].on('mouseover', function() {
            this.setStyle(highlighted);
        });
        interestingPaths[j].on('mouseout', function() {
            this.setStyle(normal);
        });
        interestingPaths[j].on('click', pathEvents);

        if (interestingPaths[j] == this) {
            changeImages(interestingObjects[j].photos);
        }
    }
    this.setStyle(highlighted);
    var tooltip = this.getTooltip();
    this.unbindTooltip();
    this.off();
    this.bindTooltip(tooltip);
}

function drawInterestingPaths() {
    if (interestingObjects) {
        if (interestingPaths) {
            clearPaths();
        }
        interestingPaths = [];
        for (var j = 0; j < interestingObjects.length; j++) {
            var path = L.geoJSON(interestingObjects[j].geojson, {
                style: function (feature) {
                    return normal;
            }}).addTo(mymap);
            path.on('mouseover', function() {
                this.setStyle(highlighted);
            });
            path.on('mouseout', function() {
                this.setStyle(normal);
            });
            if (j == 0) {
                path.setStyle(highlighted);
                path.off();
                changeImages(interestingObjects[j].photos);
            }
            path.on('click', pathEvents);
            var tooltip = "<b>Intesting Path #" + j +"</b>\n";
            tooltip += "<br><b>distance: </b>" + interestingObjects[j].distance.toFixed(2) + " miles";
            tooltip += "<br><b>interestingness: </b>" + interestingObjects[j].score.toFixed(4);
            path.bindTooltip(tooltip);

            interestingPaths.push(path);
        }
        mymap.fitBounds(interestingPaths[0].getBounds());
    }
}

function onMapClick(e) {
    if (!destinationMarker) {
        destinationMarker = L.marker(e.latlng, {
            riseOnHover: true,
            draggable: true
        }).addTo(mymap);

        destinationMarker.on('dragend', setLocationValues);
        setLocationValues();
    }
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(setMapPosition);
    } else {
        setMapPosition(null);
    }
}

function setMapPosition(position) {
    if (position) { // If there is a position for user set it as center and 
        center = [position.coords.latitude, position.coords.longitude];
        $( "#origin" ).val("Your Location");
    } else {
        center = mapCenter;
    }
    mymap.setView(center, deaultZoom);
    setOriginMarker(center);
}

function setLocationValues(e) {
    var latlng = originMarker.getLatLng();
    var location = [latlng.lat, latlng.lng];
    var locationText = location[0].toString() + ", " + location[1].toString();
    $( "#origin" ).val(locationText);
    if (destinationMarker) {
        latlng = destinationMarker.getLatLng();
        location = [latlng.lat, latlng.lng];
        locationText = location[0].toString() + ", " + location[1].toString();
        $( "#destination" ).val(locationText);
        requestShortest();
    }
    clearPaths();
}

function setOriginMarker(location) {
    originMarker = L.marker(location, {
        riseOnHover: true,
        draggable: true
    }).addTo(mymap);
    originLocation = location;
    var locationText = location[0].toString() + ", " + location[1].toString();
    originMarker.bindPopup("<b>Here you are!</b><br>The default origin for your path is<br>" + locationText).openPopup();
    originMarker.on('dragend', setLocationValues);
    $( "#origin" ).val(locationText);
}

function changeImages(images) {
    for (var j = 1; j <= images.length; j++) {
        $("#photo-" + j.toString()).attr("src", images[j-1]);
        $("#photo-" + j.toString()).css("visibility", "visible");
    }

    for (var j = images.length + 1; j <= 4; j++) {
        $("#photo-" + j.toString()).css("visibility", "hidden");
    }
}

function requestInteresting(request) {
    $.ajax({
        url: "interesting",
        dataType: "json",
        data: {
            origin: $( "#origin" ).val(),
            destination: $( "#destination" ).val(),
            time: $( "#time" ).val(),
            touristic: $( "#touristic_slider" ).val(),
            popular: $( "#pop_slider" ).val(),
            rand: ($("#rand").attr("checked") == "checked")
        },
        success: function( result ) {
            interestingObjects = [];
            for (var j = 0; j < result.length; j++){
                interestingObjects.push(result[j]);
            }
            drawInterestingPaths();
        }
    });
}

function requestShortest() {
    $.ajax({
        url: "shortest",
        type: "get",
        dataType: "json",
        data: {
            origin: $( "#origin" ).val(),
            destination: $( "#destination" ).val()
        },
        success: function(result) {
            shortestObject = result;
            alert(JSON.stringify(result.geojson));
            drawShortestPath();
        },
        error: function() {
            alert('No path found');
        }
    });
}

function requestScoring() {
    $.ajax({
        url: "score",
        type: "get",
        dataType: "json",
        data: {},
        success: function(result) {
            //mymap.clearLayers();
            alert(result);
            scoring =  L.geoJSON(result, {
                style: function (feature) {
                    alert(feature);
                    return {opacity: 0.9};
                }
            }).addTo(mymap);
            alert('finished');
        },
        error: function() {
            alert('Problem with scoring');
        }
    });
}

$(document).ready(function() {
    getLocation();

    $("#touristic_slider").ionRangeSlider({
        type: "single",
        grid: false,
        min: 0,
        max: 1,
        step: 0.1,
        grid_snap: true
    });

    $("#pop_slider").ionRangeSlider({
        type: "single",
        grid: false,
        min: 0,
        max: 1,
        step: 0.1,
        grid_snap: true
    });

    $("#rand, #a_star").change(function () {
        if ($("#rand").attr("checked") === "checked") {
            $("#rand").attr("checked", null);
            $("#a_star").attr("checked", "checked");
        } else {
            $("#a_star").attr("checked", null);
            $("#rand").attr("checked", "checked");
        }
    });
})