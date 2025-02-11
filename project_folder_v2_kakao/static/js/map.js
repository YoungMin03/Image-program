// 서버에서 전달받은 locations 데이터를 가져옴
var mapElement = document.getElementById('map');
var locations = JSON.parse(mapElement.dataset.locations);

var mapContainer = document.getElementById('map'),
    mapOption = { 
        center: new kakao.maps.LatLng(37.5665, 126.9780),
        level: 8
    };

var openInfowindow = null; // 현재 열린 인포윈도우 추적

var map = new kakao.maps.Map(mapContainer, mapOption);

var markers = [];
var linePath = [];

locations.forEach(function(loc) {
    var position = new kakao.maps.LatLng(loc.lat, loc.lng);
    linePath.push(position);
    
    var marker = new kakao.maps.Marker({
        position: position,
        map: map
    });
    
    var iwContent = `
        <div style="padding:5px;width:200px;">
            <img src="/uploads/${loc.filename}" style="width:100%;border-radius:4px;margin-bottom:8px">
            <p style="margin:4px 0">촬영시간: ${loc.time}</p>
            <p style="margin:4px 0">위도: ${loc.lat}</p>
            <p style="margin:4px 0">경도: ${loc.lng}</p>
        </div>`;
    
    var infowindow = new kakao.maps.InfoWindow({
        content: iwContent
    });
    
    kakao.maps.event.addListener(marker, 'click', function() {
        if (openInfowindow) {
            openInfowindow.close();
        }
        
        if (openInfowindow !== infowindow) {
            infowindow.open(map, marker);
            openInfowindow = infowindow;
        } else {
            openInfowindow = null;
        }
    });
    
    markers.push(marker);
});

if (linePath.length > 0) {
    map.setCenter(linePath[0]);
    
    var polyline = new kakao.maps.Polyline({
        path: linePath,
        strokeWeight: 5,
        strokeColor: 'blue',
        strokeOpacity: 0.7,
        strokeStyle: 'solid'
    });
    
    polyline.setMap(map);
}