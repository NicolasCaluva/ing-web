// Initialize Google Map on school detail page using data attributes on #map
// Exposes global function expected by Google API callback
window.initSchoolDetailMap = function(){
  var el = document.getElementById('map');
  if (!el) return;
  var lat = parseFloat(el.dataset.lat);
  var lng = parseFloat(el.dataset.lng);
  var name = el.dataset.name || '';
  var address = el.dataset.address || '';

  var hasCoords = !isNaN(lat) && !isNaN(lng);
  var center = hasCoords ? {lat: lat, lng: lng} : {lat: -34.6037, lng: -58.3816};
  var map = new google.maps.Map(el, { center: center, zoom: hasCoords ? 15 : 5 });

  function placeMarkerAndInfo(position){
    var marker = new google.maps.Marker({ position: position, map: map, title: name });
    if (name || address) {
      var content = '<div>' +
        (name ? '<strong>' + name + '</strong><br/>' : '') +
        (address ? address : '') +
      '</div>';
      var info = new google.maps.InfoWindow({ content: content });
      marker.addListener('click', function(){ info.open({ anchor: marker, map: map, shouldFocus: false }); });
      info.open({ anchor: marker, map: map, shouldFocus: false });
    }
  }

  if (hasCoords) {
    placeMarkerAndInfo(center);
  } else if (address) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: address }, function(results, status){
      if (status === 'OK' && results[0] && results[0].geometry) {
        var loc = results[0].geometry.location;
        var pos = {lat: loc.lat(), lng: loc.lng()};
        map.setCenter(pos);
        map.setZoom(15);
        placeMarkerAndInfo(pos);
      }
    });
  }
};
