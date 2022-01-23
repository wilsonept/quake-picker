// получаем список всех кнопок выбора
let buttons = document.querySelectorAll("div.card-image-wrapper")

function champOnClick(obj) {
  // удаляем у класс card-active со всех кнопок
  buttons.forEach(btn => btn.classList.remove('card-active'));
  // добавляем класс card-active на кликнутую кнопку
  obj.classList.add('card-active');

}

buttons.forEach(button => {
  // вешаем листенер нажатия на кнопки
  button.addEventListener('click', function () {
  // функция выполнится при нажатии.
    // this это текущий элемент по которому был произведен клик
    champOnClick(this)
  });
});
