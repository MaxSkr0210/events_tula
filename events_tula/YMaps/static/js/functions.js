//Найти мероприятия
const findGeo = (name) => {
  const arr = [];

  mer.forEach((geo) => {
    if (geo.description.indexOf(name) >= 0) {
      arr.push(geo);
    }
  });

  return arr;
};

const mets = [];

//Добавить гео точку
const addGeo = (map, mer) => {
  mer.forEach((geo) => {
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

//Добавление элемента на страницу
const addElement = (data) => {
  const [date_start, time_start] = data.start_date.split("T");
  const [date_end, time_end] = data.end_date.split("T");
  const template = `
  <div class="swiper-slide">
  <div class="card">
    <div class="header" style="background-image: url(${data.img});">
      <div class="mid">
        <div class="info">
          <h1>${data.event_name}</h1>
          <div class="date">
            <img src="./static/images/Calendar.png" alt="картинка" />
            ${date_start} | ${time_start}-${time_end}
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
              <img src="./static/images/gold_locations.png" alt="" />
              Тула
              <img src="./static/images/start.png" alt="" />
              25 мероприятий
            </div>
          </div>
          <div class="subsribe">
            <button class="btn subBtn" id="${data.id - 1}">Подписаться</button>
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
  </div>
</div>`;

  list.innerHTML += template;

  const btns = document.querySelectorAll(".subBtn");

  btns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("id");
      TG.sendData(JSON.stringify(mer[id]));
    });
  });
};
