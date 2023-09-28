let myMap;
let circle;
let ourCoords;
let radius;

const deleteControls = [
  "trafficControl",
  "searchControl",
  "scaleLine",
  "typeSelector",
];

const events = JSON.parse(document.querySelector("#events").textContent);
const myEvents = [];
const list = document.querySelector(".events");
const dropDownInput = document.querySelector(".dropdown__input-hidden");

//   MAP
function init() {
  const geolocationControl = new ymaps.control.GeolocationControl({
    options: {
      float: "right",
    },
  });
  const geolocation = ymaps.geolocation;

  geolocation
    .get({
      provider: "browser",
      mapStateAutoApply: true,
    })
    .then((result) => {
      result.geoObjects.options.set("preset", "islands#redCircleIcon");

      ourCoords = result.geoObjects;

      //Создание карты
      myMap = new ymaps.Map(
        "map",
        {
          center: ourCoords.position,
          zoom: 15,
          controls: [geolocationControl],
        },
        {
          searchControlProvider: "yandex#search",
        }
      );

      //Добавление нашей геометки

      deleteControls.forEach((control) => {
        myMap.controls.remove(control);
      });

      myMap.geoObjects.add(
        new ymaps.Placemark(
          ourCoords.position,
          {},
          {
            preset: "islands#circleIcon",
            iconColor: "red",
          }
        )
      );

      //вывод всех мериприятий в радиусе 200 м
      printMark(myMap, events, 200);

      //создание и вывод окружности
      circle = new ymaps.Circle([ourCoords.position, 200], null, {
        fillColor: "#DB709377",
        strokeColor: "#990066",
      });

      myMap.geoObjects.add(circle);
    });
}

ymaps.ready(init);

//    DROPDOWN

// Полифилл для метода forEach для NodeList
if (window.NodeList && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = (callback, args) => {
    args = args || window;
    for (var i = 0; i < this.length; i++) {
      callback.call(args, this[i], i, this);
    }
  };
}

document.querySelectorAll(".dropdown").forEach((dropDownWrapper) => {
  const dropDownBtn = dropDownWrapper.querySelector(".dropdown__button");
  const dropDownList = dropDownWrapper.querySelector(".dropdown__list");
  const dropDownListItems = dropDownList.querySelectorAll(
    ".dropdown__list-item"
  );
  const dropDownInput = dropDownWrapper.querySelector(
    ".dropdown__input-hidden"
  );

  dropDownBtn.addEventListener("click", function (e) {
    dropDownList.classList.toggle("dropdown__list--visible");
    this.classList.add("dropdown__button--active");
  });

  dropDownListItems.forEach((listItem) => {
    listItem.addEventListener("click", function (e) {
      e.stopPropagation();
      dropDownBtn.innerText = this.innerText;
      dropDownBtn.focus();
      dropDownInput.value = this.dataset.value;
      dropDownList.classList.remove("dropdown__list--visible");
      radius = Number(this.dataset.value);
      circle.geometry.setRadius(radius);
      printMark(myMap, events, radius);
    });
  });

  document.addEventListener("click", (e) => {
    if (e.target !== dropDownBtn) {
      dropDownBtn.classList.remove("dropdown__button--active");
      dropDownList.classList.remove("dropdown__list--visible");
    }
  });
});
