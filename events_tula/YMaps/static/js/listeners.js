let up = true;

const search = document.querySelector("#search");
const arrow = document.querySelector("#arrow");
const input = document.querySelector(".search");

//Поиск мероприятий
input.addEventListener("input", async () => {
  const data = input.value;
  changeMarks(myMap, data);
});

//Открытие и закрытие меню
arrow.addEventListener("click", () => {
  if (!up) {
    search.style.top = 400 + "px";
    arrow.style.transform = "rotate(180deg)";
  } else {
    console.log(123);
    arrow.style.transform = "rotate(0deg)";
    search.style.top = 60 + "px";
  }
  up = !up;
});

//Выбор расстояния
const select = document.querySelector(".radius");
select.addEventListener("change", () => {
  const radius = Number(select.value);
  circle.geometry.setRadius(radius);
  printMark(myMap, events, radius);
});
