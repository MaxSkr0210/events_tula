let up = true;

const input = document.querySelector("input");
input.addEventListener("input", async () => {
  const data = input.value;
  myMap.geoObjects.removeAll();

  if (data.trim() === "") {
    while (list.firstChild) {
      list.removeChild(list.firstChild);
    }

    addGeo(myMap, a);
    return;
  }
  const searchedEl = findGeo(data);
  while (list.firstChild) {
    list.removeChild(list.firstChild);
  }

  addGeo(myMap, searchedEl);
});

const search = document.querySelector("#search");
const arrow = document.querySelector("#arrow");

arrow.addEventListener("click", () => {
  if (!up) {
    search.style.top = 550 + "px";
    arrow.style.transform = "rotate(180deg)";
    up = true;
  } else {
    arrow.style.transform = "rotate(0deg)";
    search.style.top = 0;
    up = false;
  }
});

const items = document.querySelectorAll(".radius_item");
items.forEach((item, index) => {
  item.addEventListener("click", () => {
    while (list.firstChild) {
      list.removeChild(list.firstChild);
    }
    myMer.length = 0;
    mer.forEach((geo) => {
      map.geoObjects.removeAll();

      ymaps.geocode(geo.address).then((res) => {
        var firstGeoObject = res.geoObjects.get(0);
        var cords = firstGeoObject.geometry.getCoordinates();

        const c = circle.geometry._coordinates;
        const m = { ...geo, cords };

        if (
          ymaps.coordSystem.geo.getDistance(c, m.cords) <
          Number(items[index].innerText)
        ) {
          myMer.push(m);

          addGeo(myMap, [m]);
        }
      });
    });

    myMap.geoObjects.add(ourCoords);
    circle = new ymaps.Circle(
      [ourCoords.position, Number(items[index].innerText)],
      null,
      {
        fillColor: "#DB709377",
        strokeColor: "#990066",
      }
    );

    myMap.geoObjects.add(circle);
  });
});
