// получаем список всех кнопок выбора
let buttons = document.querySelectorAll(".card")

function champOnClick(obj) {
  // удаляем у класс card-active со всех кнопок
  buttons.forEach(btn => btn.classList.remove('card-active'));
  // добавляем класс card-active на кликнутую кнопку
  obj.classList.add('card-active');
  // выбираем вложенный в кликнутый элемент div и берем из него класс персонажа
  // chosenHeroClass = obj.getElementsByTagName('div')[0].classList[1];
  // удаляем последний класс из списка
  // choiceIcon.remove(
  //   choiceIcon[choiceIcon.length - 1]
  // );
}

checkBox = document.querySelector('#champ')
buttons.forEach(button => {
  // вешаем листенер нажатия на кнопки
  button.addEventListener('click', function () {
  // функция выполнится при нажатии.
    // this это текущий элемент по которому был произведен клик
    champOnClick(this)
    checkBox.checked = true
    checkBox.disabled = true
    console.log(checkBox.disabled)
    console.log(checkBox.checked)
  });
});