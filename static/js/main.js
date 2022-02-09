// получаем список всех кнопок выбора
const buttons = document.querySelectorAll(".card")
const checkBoxes = document.querySelectorAll("input [type=checkbox]")

function champOnClick(obj) {
  // удаляем у класс card-active со всех кнопок
  buttons.forEach(btn => btn.classList.remove('card-active'));
  // добавляем класс card-active на кликнутую кнопку
  obj.classList.add('card-active');
  // отмечаем вложенный чекбокс
  let checkBox = obj.querySelector('.card input')
  checkBox.checked = true
  checkBox.disabled = true
  setTimeout(nextStep, 1000, obj)
}

function nextStep(obj) {
  // удаляем у класс card-active со всех кнопок
  obj.classList.remove('card-active')
  if (currentStep >= steps.length) {
    currentStep = 0
  }
  if (steps[currentStep] === 'pick') {
    // добавляем класс card-picked на кликнутую кнопку
    obj.classList.add('card-picked')
    currentStep = currentStep + 1
    return
  }
  
  if (steps[currentStep] === 'ban') {
    // добавляем класс card-banned на кликнутую кнопку
    obj.classList.add('card-banned')
    currentStep = currentStep + 1
    return
  }
}

let currentStep = 0
const steps = [
  'pick', 'pick', 'ban', 'ban', 'pick', 'pick', 'ban', 'ban', 'pick', 'pick'
]

const champions = [
  'nyx', 'anarky', 'slash', 'athena', 'ranger', 'visor',
  'galena', 'bj', 'doom', 'strogg', 'deathknight', 'eisen',
  'clutch', 'sorlag', 'scalebearer', 'keel'
]

buttons.forEach(button => {
  // вешаем листенер нажатия на кнопки
  button.addEventListener('click', function (event) {
    // отменяем поведение при клике по умолчанию
    event.preventDefault()
    // функция выполнится при нажатии. this это текущий элемент по которому был 
    // произведен клик
    champOnClick(this)
  });
});


// Пробуем местные классы.
class Card {

  constructor(name) {
    this.name = name
    this.picked = false
    this.banned = false
    this.active = false
  }

  // getter DOM элемента класса
  get getDOMObject() {
    return window.document.getElementById(this.name)
  }

  // setter для self.picked
  set picked(value) {
    if (value === true) {
      this.getDOMObject.classList.add('card-picked')
    }
    else {
      this.getDOMObject.classList.remove('card-picked')
    }
  }

  // setter для self.banned
  set banned(value) {
    if (value === true) {
      this.getDOMObject.classList.add('card-banned')
    }
    else {
      this.getDOMObject.classList.remove('card-banned')
    }
  }

  // setter для self.active
  set active(value) {
    if (value === true) {
      this.getDOMObject.classList.add('card-active')
    }
    else {
      this.getDOMObject.classList.remove('card-active')
    }
  }
}

let nyxCard = new Card('nyx')
