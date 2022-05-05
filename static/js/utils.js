import {sendRequest} from "/static/js/xhr.js"

// Включаем строгий режим.
"use strict"


/**
 * Получает текущее состояние игры с сервера с помощью xhr запроса.
 */
export function updatePage() {
  if (window.location.pathname.split("/")[1] === "results") {
    const IntervalId = localStorage.getItem("pageAutoUpdate")
    clearInterval(IntervalId)
    return
  }
  const body = getBody("get")
  sendRequest(body).then(updateClasses).then(rebuildPage)
}


/**
 * Обновляем листенер клика на карточках карт/чемпионов.
 */
function updateListeners () {
  // получаем список всех карточек выбора.
  const cards = document.querySelectorAll(".card")

  cards.forEach(button => {
    // Вешаем листенер нажатия на кнопки.
    button.addEventListener("click", function (event) {
      // Отменяем поведение при клике по лейблу по умолчанию. Если этого
      // не сделать, то клик будет выполняться дважды. Один раз
      // стандартный второй тот который мы создали. Это приведет к
      // двойному вызову данной функции.
      event.preventDefault()
      // Функция выполнится при нажатии. this это текущий элемент по которому
      // был произведен клик
      champOnClick(this)
    });
  });
}


/**
 * Функция выполняющаяся при клике по карточке карты/чемпиона.
 * @param {Object} obj 
 */
function champOnClick(obj) {

  const object = JSON.parse(localStorage.getItem("gameState"))
  const objectType = object.current_object_type

  // добавляем класс card-active на кликнутую кнопку
  obj.classList.add("card-active")
  // отмечаем вложенный чекбокс
  let checkBox = obj.querySelector(".card input")
  checkBox.checked = true

  const cards = document.querySelectorAll(".card")
  cards.forEach(card => {
    card.classList.add("card-waiting")
  })

  const gameState = JSON.parse(localStorage.getItem("gameState"))
  const action = gameState.current_action
  const nickname = window.location.pathname.split("/")[2]
  const choice = obj.getAttribute("id")

  sendChoice(action, nickname, choice, objectType)
}


/**
 * Формирует тело для отправки на сервер в зависимости от типа.
 * Типы поддерживаемые приложением: get, update.
 * @param {String} type 
 * @param {Object} params 
 * @returns 
 */
function getBody(type, params) {
  let template

  if (type === "update") {
    template = {
      "jsonrpc": "2.0",
      "method": "app.updateState",
      "params": {
          "room_uuid": window.location.pathname.split("/")[1],
          "action": params["action"],
          "nickname": params["nickname"],
          "object_type": params["object_type"],
          "choice": params["choice"]
      },
      "id": 1
    }

    const parsedResponse = JSON.parse(localStorage.getItem("gameState"))

    if (params["object_type"] === "champ") {
      const pickedMaps = getPickedMaps(parsedResponse)
      const pickedChamps = getPickedChamps(parsedResponse)
      const currentMap = getCurrentMap(pickedMaps, pickedChamps.length)
      template.params["map_sname"] = currentMap
    }

  } else {
    template = {
      "jsonrpc": "2.0",
      "method": "app.getState",
      "params": {
          "room_uuid": window.location.pathname.split("/")[1],
      },
      "id": 1
    }
  }
  return template
}


/**
 * Перестраивает на основе полученного ответа от сервера.
 * @param {Promise} response 
 */
function rebuildPage(response) {
  
  localStorage.setItem("gameState", response.result)
  const parsedResponse = JSON.parse(response.result)

  console.log("[rebuildPage]:", parsedResponse) // TEST

  // Если все шаги игры пройдены редирект на результаты.
  if (parsedResponse.current_object_type === "result") {
    window.location.pathname = `/results/${parsedResponse.room_uuid}`
    return
  }

  // Проверяем все ли игроки в комнате
  if (parsedResponse.players.length < 2) {
    console.log("[rebuildPage]:", "Ждем второго игрока.")
    return
  }

  console.log("[rebuildPage]:", "Все игроки в комнате, начинаем игру.")
  let currentObjectType = parsedResponse.current_object_type
  
  // Отображаем нужный шаблон если необходимо.
  if (currentObjectType != window.currentObjectType) {
    
    // Отображаем необходимый теплейт стадии игры.
    const selector = `#${currentObjectType}s`
    setTimeout(function() {
      renderTemplate(selector, parsedResponse)
    }, 4000)

    // Обновляем имя второго игрока на странице.
    setTimeout(function() {
      let playerTwoNameBlock = document.querySelector(".red h1")
      const playerTwoName = parsedResponse.players[1].nickname
      playerTwoNameBlock.innerText = playerTwoName
    }, 4000)

    window.currentObjectType = currentObjectType
  }
}


/**
 * Обновляет состояния карточек на основе распаршенного ответа сервера.
 * @param {Promise} response 
 * @returns {Promise}
 */
function updateClasses(response) {

  localStorage.setItem("gameState", response.result)
  const parsedResponse = JSON.parse(response.result)

  console.log("[ updateClasses ]:", parsedResponse) // TEST

  const nickname = window.location.pathname.split("/")[2]
  const cards = document.querySelectorAll(".card")

  console.log("[ updateClasses ]:", cards) // TEST
  if (cards.length <= 0) {
    return response
  }

  // Объединяем итерируемые объекты.
  let choices = {
    "mapChoices": {
      "items": parsedResponse.map_choices,
      "propName": "map_short_name"
    },
    "champChoices": {
      "items": parsedResponse.champ_choices,
      "propName": "champ_short_name"
    }
  }

  console.log("[ updateClasses ]:", choices) // TEST

  // Отмечаем забаненые/выбранные объекты которые сейчас на странице.
  for (const [key, value] of Object.entries(choices)) {
    if (value["items"].length > 0) {
      for (const item of value["items"]) {
        let card = document.querySelector("#" + item[value["propName"]])
        if (card !== null) {
          let cls
          item.action === "ban" ? cls = "card-banned" : cls = "card-picked"
          card.classList.add(cls)
        }
      }
    }
  }

  // Добавляем карточке класс ожидания до тех пор пока до игрока не
  // дойдет очередь выбирать.
  if (parsedResponse.current_player !== nickname) {
    cards.forEach(card => {
      card.classList.add("card-waiting")
    })
  } else {
    cards.forEach(card => {
      card.classList.remove("card-waiting")
    })
  }

  // Меняем сообщение выбора.
  let actionMessage = document.querySelector("main h1")
  actionMessage.innerText = `${parsedResponse.current_player} ${parsedResponse.current_action}`
  
  // удаляем класс card-active со всех кнопок и снимаем чекбоксы.
  cards.forEach(card => {
    card.classList.remove("card-active")
    card.querySelector("input").checked = false
  })

  return response
}


/**
 * Заменяет текущее отображение в блоке main на отображение
 * шаблона по селектору.
 * @param {String} selector
 * @param {Object} parsedResponse 
 */
function renderTemplate(selector, parsedResponse) {
  let main = document.querySelector("main")
  const template = document.querySelector(selector)
  // Клонируем template.
  const tempClone = template.content.cloneNode(true)
  // Очищаем основной блок.
  main.innerHTML = ""
  // Вставляем клон в основной блок.
  main.appendChild(tempClone)
  updateListeners()
}


/**
 * Отправляем выбор пользователя на сервер с помощью xhr запроса.
 * @param {String} action ban или pick.
 * @param {String} nickname имя игрока.
 * @param {String} choice короткое наименование карты или чемпиона.
 * @param {String} objectType map или champ
 */
function sendChoice(action, nickname, choice, objectType) {
  let body = getBody(
    "update", {
      "action": action,
      "nickname": nickname,
      "choice": choice,
      "object_type": objectType
    })
  console.log(body)
  sendRequest(body).then(updateClasses).then(rebuildPage)
}


/**
 * Получает список выбранных карт.
 * @param {Object} parsedResponse
 * @returns {Array}
 */
function getPickedMaps(parsedResponse) {

  let maps = []
  parsedResponse.map_choices.forEach(mep => {
    if (mep.action === "pick") {
      maps.push(mep.map_short_name)
    }
  })

  return maps 
}


/**
 * Получает количество пиков чемпионов.
 * @returns {Number}
 */
function getPickedChamps(parsedResponse) {
  // Получаем количество выбранных персонажей путем перебора каждой
  // выбранной карты обоих игроков.
  if (parsedResponse.champ_choices.length === 0) {
    return []
  }

  let pickedChamps = []
  parsedResponse.champ_choices.forEach(champ => {
    if (champ.action === "pick") {
      pickedChamps.push(champ)
    }
  })

  return pickedChamps
}


/**
 * Возвращает название карты для которой выполняется выбор персонажа.
 * @param {Object} sortedMaps
 * @param {Number} champPickCount
 * @returns {String}
 */
function getCurrentMap(sortedMaps, champPickCount) {
  // Если персонажи не выбирались значит первая карта.
  if (champPickCount === 0) {
    return sortedMaps[0]
  }

  // Получаем индекс карты.
  const mapIndex = Math.floor(champPickCount / 2)
  return sortedMaps[mapIndex]
}