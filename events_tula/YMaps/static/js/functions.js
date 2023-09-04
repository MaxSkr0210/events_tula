//Найти мероприятия
const findGeo = (events, name) => {
  const arr = [];

  events.forEach((geo) => {
    const event = geo.event_name.toLowerCase();
    if (event.indexOf(name.toLowerCase()) >= 0) {
      arr.push(geo);
    }
  });

  return arr;
};

//Очистить карту и список мероприятий
const clearMarks = (map) => {
  myEvents.length = 0;

  while (list.firstChild) {
    list.removeChild(list.firstChild);
  }

  map.geoObjects.each((placemark, index) => {
    if (index > 1) {
      map.geoObjects.remove(placemark);
    }
  });
};

//Поставить метки на карту
const addGeo = (map, events) => {
  events.forEach((geo) => {
    addElement(geo);
    const newGeo = new ymaps.Placemark(
      geo.cords,
      {
        balloonContent: geo.event_name,
      },
      {
        iconLayout: "default#image",
        iconImageHref: "static/images/самовар2.png",
        iconImageSize: [23, 25],
      }
    );

    map.geoObjects.add(newGeo);
  });
};
//создание меток
const printMark = (map, events, radius) => {
  // clearMarks(map);

  events.forEach((event) => {
    ymaps.geocode(event.address).then((res) => {
      const myGeoObject = res.geoObjects.get(0);
      const cords = myGeoObject.geometry.getCoordinates();

      const center = circle.geometry._coordinates;
      const m = { ...event, cords };

      if (ymaps.coordSystem.geo.getDistance(center, m.cords) <= radius) {
        myEvents.push(m);
        addGeo(myMap, [m]);
      }
    });
  });
};
//изменить метки
const changeMarks = (map, data) => {
  clearMarks(map);
  const searchedEl = findGeo(myEvents, data);
  addGeo(map, searchedEl);
};

//Добавление элемента на страницу
const addElement = (data) => {
  const [date_start, time_start] = data.start_date.split("T");
  const [date_end, time_end] = data.end_date.split("T");
  const template = `
  <div class="event_item">
    <div class="header" style="background-image: url(${data.img});">
      <div class="mid">
        <div class="info">
          <h1>${data.event_name}</h1>
          <div class="date">
            <img src="./static/images/Calendar.png" alt="картинка" />
            ${date_start} | ${time_start.replace("Z", "")}-${time_end.replace(
    "Z",
    ""
  )}
          </div>
        </div>
      </div>
    </div>
    <div class="body">
      <div class="mid">
        <div class="priceAndSubs">
          <div class="price">
            <span class="pr gray small">Цена</span>
            <p>
              <span class="gold big">${data.price}₽</span
              >
            </p>
          </div>
        </div>
        <div class="event">
          <div class="rating">
            <p>${data.event_name}</p>
            <div class="gold" style="font-size: 11px">
              <img src="./static/images/placeholder.svg" alt="" />
              Тула
              <img src="./static/images/star.svg" alt="" />
              25 мероприятий
            </div>
          </div>
          <div class="subsribe">
            <button class="btn subBtn" id="${data.id}">Подписаться</button>
          </div>
        </div>
        <div class="description">
          ${data.description}
        </div>
        <div class="mainButton">
          <button class="btn">Купить билеты</button>
        </div>
      </div>
  </div>
</div>`;

  list.innerHTML = template + list.innerHTML;

  const btns = document.querySelectorAll(".subBtn");

  btns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("id");
      const event = events.findIndex((item) => item.id === id);
      TG.sendData(JSON.stringify(event));
    });
  });
};
