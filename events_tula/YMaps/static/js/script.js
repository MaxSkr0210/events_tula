let myMap;
let circle;
let ourCoords;
let map;
let categories;

const deleteControls = [
  "trafficControl",
  "searchControl",
  "scaleLine",
  "typeSelector",
];

const mer = JSON.parse(document.querySelector(("#events")).textContent)

/*let mer = [
  // {
  //   id: 1,
  //   event_name: "Событие 1",
  //   description: "dfgsdfgsdgsdfg",
  //   price: 200,
  //   address: "улица Охотный Ряд, 2, Москва, 103265",
  //   img: "https://dfstudio-d420.kxcdn.com/wordpress/wp-content/uploads/2019/06/digital_camera_photo-1080x675.jpg",
  //   start_date: "2023-06-12T14:55",
  //   end_date: "2023-06-13T14:55",
  // },
  {
    id: 1,
    event_name: "Лекция Савина",
    description: "БЕГИТЕ ГЛУПЦЫ",
    price: 1000,
    address: "проспект Ленина, 92, Тула, 300012",
    img: "https://dfstudio-d420.kxcdn.com/wordpress/wp-content/uploads/2019/06/digital_camera_photo-1080x675.jpg",
    start_date: "2023-06-12T14:55",
    end_date: "2023-06-13T14:55",
  },
  {
    id: 2,
    event_name: "Событие 2",
    description: "dfgsdfgssasdasddgsdfg",
    price: 100,
    address: "Советская улица, 14А, Тула, 300041",
    img: "https://dfstudio-d420.kxcdn.com/wordpress/wp-content/uploads/2019/06/digital_camera_photo-1080x675.jpg",
    start_date: "2023-06-12T14:55",
    end_date: "2023-06-13T14:55",
  },
];
*/
const coords = [];
const myMer = [];

const list = document.querySelector(".swiper-wrapper");

ymaps.ready(init);

function init() {
  const geolocationControl = new ymaps.control.GeolocationControl({
    options: {
      float: "right",
    },
  });
  const geolocation = ymaps.geolocation;
  myMap = new ymaps.Map(
    "map",
    {
      center: [55.76, 37.64], // Москва
      zoom: 10,
      controls: [geolocationControl],
    },
    {
      searchControlProvider: "yandex#search",
    }
  );
  map = myMap;

  deleteControls.forEach((control) => {
    myMap.controls.remove(control);
  });

  geolocation
    .get({
      provider: "browser",
      mapStateAutoApply: true,
    })
    .then(function (result) {
      result.geoObjects.options.set("preset", "islands#redCircleIcon");

      ourCoords = result.geoObjects;
      myMap.geoObjects.add(ourCoords);

      circle = new ymaps.Circle([ourCoords.position, 200], null, {
        fillColor: "#DB709377",
        strokeColor: "#990066",
      });

      myMap.geoObjects.add(circle);
      const c = circle.geometry._coordinates;
      coords.forEach((m) => {
        if (
          ymaps.coordSystem.geo.getDistance(c, m.cords) <
          Number(items[index].innerText)
        ) {
          myMer.push(m);
        }
      });
    });
}

const slide = document.querySelector("#slide");
const slideContainer = document.querySelector("#search");
const radius = document.querySelector("#radius");

function selectItem(i) {
  const id = Number(i);
  coords.forEach((geo) => {
    if (geo.id === Number(id)) {
      myMap.setCenter(geo.cords);
    }
  });
}
