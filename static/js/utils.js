import {sendRequest} from "/static/js/xhr.js"

// Включаем строгий режим.
"use strict"


/**
 * Получает текущее состояние игры с сервера с помощью xhr запроса.
 */
export function updatePage() {
  const body = getBody("get")
  sendRequest(body).then(rebuildPage)
  sendRequest(body).then(getPickedMaps)
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
  const objectType = object.current_object

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

    if (params["object_type"] === "champ") {
      const pickedMaps = getPickedMaps()
      const pickedChampsCount = getPickedChampsCount()
      const currentMap = getCurrentMap(pickedMaps, pickedChampsCount)
      template.params["map_name"] = currentMap
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

  console.log(parsedResponse) // TEST

  // Если все шаги игры пройдены редирект на результаты.
  if (parsedResponse.currentObject === "result") {
    window.location.pathname = `/results/${parsedResponse.room_uuid}`
  }

  // Проверяем все ли игроки в комнате
  if (parsedResponse.players.length === 2) {
    console.log('Все игроки в комнате, начинаем игру')
    let currentObject = parsedResponse.current_object
    
    // Отображаем нужный шаблон если необходимо
    if (currentObject != window.currentObject) {
      
      // Отображаем необходимый теплейт стадии игры.
      const selector = `#${currentObject}s`
      setTimeout(function() {
        renderTemplate(selector, parsedResponse)
      }, 4000)

      // Обновляем имя второго игрока на странице.
      setTimeout(function() {
        let playerTwoNameBlock = document.querySelector(".red h1")
        const playerTwoName = parsedResponse.players[1].nickname
        playerTwoNameBlock.innerText = playerTwoName
      }, 4000)

      window.currentObject = currentObject
    }
    
    if (document.querySelector(".card")) {
      updateClasses(parsedResponse)
    }
    
  }
  else {
    console.log("Ждем второго игрока")
  }
}


/**
 * Обновляет состояния карточек на основе распаршенного ответа сервера.
 * @param {Object} parsedResponse 
 */
function updateClasses(parsedResponse) {
  const nickname = window.location.pathname.split("/")[2]

  let choiceObjects // Для объектов выбора игрока.
  parsedResponse.players.forEach(player => {
    
    // Определяем итерируемые объект по типу текущего объекта выбора.
    if (window.currentObject === "map") {
      choiceObjects = player.map_choices
    }
    else if (window.currentObject ==="champ") {
      choiceObjects = player.champ_choices
    }
    // Отмечаем забаненые карточки.
    if (choiceObjects.bans.length >= 1) {
      choiceObjects.bans.forEach(item => {
        let card = document.querySelector("#" + item.short_name)
        card.classList.add("card-banned")
      })
    }
    // Отмечаем выбраные карточки.
    if (choiceObjects.picks.length >= 1) {
        choiceObjects.picks.forEach(item => {
        let card = document.querySelector("#" + item.short_name)
        card.classList.add("card-picked")
      })
    }
    // Добавляем карточке класс ожидания до тех пор пока до игрока не
    // дойдет очередь выбирать.
    const cards = document.querySelectorAll(".card")
    if (parsedResponse.current_player !== nickname) {
      cards.forEach(card => {
        card.classList.add("card-waiting")
      })
    } else {
      cards.forEach(card => {
        card.classList.remove("card-waiting")
      })
    }
  })

  // Меняем сообщение выбора.
  let actionMessage = document.querySelector("main h1")
  actionMessage.innerText = `${parsedResponse.current_player} ${parsedResponse.current_action}`
  
  // удаляем класс card-active со всех кнопок и снимаем чекбоксы.
  const cards = document.querySelectorAll(".card")
  cards.forEach(card => {
    card.classList.remove("card-active")
    card.querySelector("input").checked = false
  })
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
  updateClasses(parsedResponse)
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
  sendRequest(body).then(rebuildPage)
}


/**
 * Получает список выбранных карт.
 * @returns {Array}
 */
function getPickedMaps() {
  const parsedResponse = JSON.parse(localStorage.getItem("gameState"))

  // Определяем по seed первого игрока и добавляем его в players.
  let playerIndex = parsedResponse.seed - 1
  let players = []
  players.push(parsedResponse.players[playerIndex])

  // Определяем индекс второго игрока и добавляем его в players.
  playerIndex === 0 ? playerIndex = 1: playerIndex = 0
  players.push(parsedResponse.players[playerIndex])
  // if (playerIndex === 0) {
  //   playerIndex = 1
  // } else {
  //   playerIndex = 0
  // }

  let maps = []
  let index = 0
  // Первый игрок будет иметь больше выбранных карты по определению.
  // Поэтому итерируемся по выбору первого игрока и после каждого его
  // выбора добавляем выбор второго игрока. На выходе получаем
  // отсортированный по очередности выбора список карт.
  players[0].map_choices.picks.map(map_choice => {
    maps.push(map_choice.short_name)
    try {
      maps.push(players[1].map_choices.picks[index].short_name)
      index += 1
    } catch {
      console.log('Все карты добавлены в массив.')
    }
  })

  // Получаем отсортированный по очередности выбора список карт.
  console.log(maps)
  return maps 
}


/**
 * Получает количество пиков чемпионов.
 * @returns {Number}
 */
function getPickedChampsCount() {
  const parsedResponse = JSON.parse(localStorage.getItem("gameState"))

  // Получаем количество выбранных персонажей путем перебора каждой
  // выбранной карты обоих игроков.
  let champPickCount = 0
  parsedResponse.players.map(player => {
    player.map_choices.picks.map(map_choice => {
      champPickCount += map_choice.champ_choices.picks.length
    })
  })

  return champPickCount
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
  const mapIndex = Math.floor(champPickCount / 2) - 1
  return sortedMaps[mapIndex]
}