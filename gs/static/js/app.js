$(document).ready(function(){
  var longs,lats;
  $("#query").on("click",function(){
            var loc = document.getElementById("location");
            var lats,longs;
            
              if(navigator.geolocation){
                navigator.geolocation.getCurrentPosition(showPosition);
              }
              else{
                x.innHTML = "Your location cannot be retrieved";
              }
            $(this).prop("disabled",true)
            var map;

            var styles = {
              'highway': {
                'service': new ol.style.Style({
                  stroke: new ol.style.Stroke({
                    color: 'rgba(255, 255, 255, 1.0)',
                    width: 2
                  })
                }),
                '.*': new ol.style.Style({
                  stroke: new ol.style.Stroke({
                    color: 'rgba(255, 255, 255, 1.0)',
                    width: 3
                  })
                })
              },
            };

            var vectorSource = new ol.source.Vector({
              format: new ol.format.OSMXML(),
              loader: function(extent, resolution, projection) {
                var epsg4326Extent =
                    ol.proj.transformExtent(extent, projection, 'EPSG:4326');
                var client = new XMLHttpRequest();
                client.open('POST', 'https://overpass-api.de/api/interpreter');
                client.addEventListener('load', function() {
                  var features = new ol.format.OSMXML().readFeatures(client.responseText, {
                    featureProjection: map.getView().getProjection()
                  });
                  vectorSource.addFeatures(features);
                });
                var query = '(node(' +
                    epsg4326Extent[1] + ',' + epsg4326Extent[0] + ',' +
                    epsg4326Extent[3] + ',' + epsg4326Extent[2] +
                    ');rel(bn)->.foo;way(bn);node(w)->.foo;rel(bw););out meta;';
                client.send(query);
              },
              strategy: ol.loadingstrategy.bbox
            });

            var vector = new ol.layer.Vector({
              source: vectorSource,
              style: function(feature) {
                for (var key in styles) {
                  var value = feature.get(key);
                  if (value !== undefined) {
                    for (var regexp in styles[key]) {
                      if (new RegExp(regexp).test(value)) {
                        return styles[key][regexp];
                      }
                    }
                  }
                }
                return null;
              }
            });
            var raster = new ol.layer.Tile({
              source: new ol.source.BingMaps({
                imagerySet: 'Aerial',
                key: 'AlV-CVG2BSoc6SbMgnaXPIK-i4otW2ZrwkSvlD4Ko151k0eoc9uREOjDrThGubAz'
              })
            });
            var long = 78.486671,lat=17.385044
            map = new ol.Map({
              layers: [raster, vector],
              target: document.getElementById('map'),
              controls: ol.control.defaults({
                attributionOptions: {
                  collapsible: false
                }
              }),
              view: new ol.View({
                center:ol.proj.transform([longs,lats],'EPSG:4326', 'EPSG:3857'),
                maxZoom: 19,
                zoom: 17
              })
            })
        });
})