let swiper;
setTimeout(() => {
  swiper = new Swiper(".swiper", {
    slidesPerView: 1,
    spaceBetween: 30,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev"
    }
  });

  const swiperSlides = document.querySelectorAll(".swiper-slide");
  let id = swiper.realIndex + 1;
  selectItem(id);
  swiper.on("slideChange", function() {
    id = swiper.realIndex + 1;
    selectItem(id);
  });
}, 1000);