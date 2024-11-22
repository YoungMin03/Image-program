// // 지도에 마커와 경로를 표시하는 함수
// function displayRoute(locations) {
//     // locations: [{lat, lng, time, filename}, ...]
    
//     // 시간순으로 정렬
//     locations.sort((a, b) => new Date(a.time) - new Date(b.time));
    
//     // 마커 추가
//     locations.forEach(loc => {
//         L.marker([loc.lat, loc.lng])
//         .bindPopup(`<img src="/uploads/${loc.filename}" width="200"><br>
//                     촬영시간: ${loc.time}`)
//         .addTo(map);
//     });
    
//     // 경로 그리기
//     const path = locations.map(loc => [loc.lat, loc.lng]);
//     L.polyline(path, {color: 'red'}).addTo(map);
// }