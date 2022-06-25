import { sendXHR } from "/static/js/xhr.js"

// Включаем строгий режим.
"use strict"


/**
 * Отправляет запрос на сервер согласно режиму работы приложения.
 * @param {Object} body
 * @param {Object} ws Веб-сокет, необходим если режим приложения "ws"
 * @returns {Promise} Только в случае работы в режиме "xhr"
 */
export function sendRequest(body, ws=null) {
  if (appMode === "xhr") {
    return sendXHR(body)

  } else if (appMode === "ws") {
    try {
      ws.send(JSON.stringify(body))
    } catch {
      self.ws = openWS("ws://127.0.0.1:5000/ws")
      self.ws.send(JSON.stringify(body))
    }
    console.log("[ sendRequest ] Отправляю сообщение через веб-сокет.")

  } else {
    console.log("Выбран не верный режим работы приложения.")
  }
  return
}


/**
 * Запускает цепочку обновления страницы.
 */
export function updatePage() {
  updateClasses()
  // Запускаем с задержкой, что бы при переходе на следующий этап выбора
  // было время разглядеть выбор оппонента.
  setTimeout(rebuildPage, 4000)
}


/**
 * Формирует тело для отправки на сервер в зависимости от типа.
 * Типы поддерживаемые приложением: get, update.
 * @param {String} type 
 * @param {Object} params 
 * @returns {Object}
 */
export function newBody(type, params) {
  let template

  // Update запрос.
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

    // Добавляем название карты если выбирается чемпион.
    const parsedResponse = JSON.parse(localStorage.getItem("gameState"))
    if (params["object_type"] === "champ") {
      const pickedMaps = getPickedMaps(parsedResponse)
      const pickedChamps = getPickedChamps(parsedResponse)
      const currentMap = getCurrentMap(pickedMaps, pickedChamps.length)
      template.params["map_sname"] = currentMap
    }

    if (appMode === "ws") {
      template.method = "ws.updateState"
    }

  // Get запрос.
  } else {
    template = {
      "jsonrpc": "2.0",
      "method": "app.getState",
      "params": {
        "room_uuid": window.location.pathname.split("/")[1],
      },
      "id": 1
    }
    if (appMode === "ws") {
      template.method = "ws.getState"
    }
  }
  return template
}


/**
 * Обновляет состояния карточек на основе распаршенного ответа сервера.
 * @param {Promise} response 
 */
function updateClasses() {

  let cards = document.querySelectorAll(".card")
  if (cards.length <= 0) {
    rebuildPage()
  }

  const nickname = window.location.pathname.split("/")[2]
  cards = document.querySelectorAll(".card")

  const responseData = localStorage.getItem("gameState")
  const parsedResponse = JSON.parse(responseData)

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

  if (parsedResponse.current_player === null) {
    console.log("[ updateClasses ] Ждем второго игрока.")
    return
  }

  let currentPlayer = parsedResponse.current_player
  if (currentPlayer != window.currentPlayer) {
    play("choice")
    window.currentPlayer = currentPlayer
  }

  // Добавляем карточке класс ожидания до тех пор пока до игрока не
  // дойдет очередь выбирать.
  if (parsedResponse.current_player.toLowerCase() !== nickname.toLowerCase()) {
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
  actionMessage.innerText = `
    ${parsedResponse.current_player} ${parsedResponse.current_action}`
  
  // удаляем класс card-active со всех кнопок и снимаем чекбоксы.
  cards.forEach(card => {
    card.classList.remove("card-active")
    card.querySelector("input").checked = false
  })
}


/**
 * Перестраивает на основе полученного ответа от сервера.
 */
function rebuildPage() {
  
  const responseData = localStorage.getItem("gameState")
  const parsedResponse = JSON.parse(responseData)

  // Если все шаги игры пройдены редирект на результаты.
  if (parsedResponse.current_object_type === "result") {
    window.location.pathname = `/results/${parsedResponse.room_uuid}`
    return
  }

  // Проверяем все ли игроки в комнате
  if (parsedResponse.players.length < 2) {
    console.log("[ rebuildPage ]:", "Ждем второго игрока.")
    return
  } else {
    const cards = document.querySelector(".card")
    if (cards === null) {
      console.log("[ rebuildPage ]:", "Все игроки в комнате, начинаем игру.")
      play("start")
    }
  }

  let currentObjectType = parsedResponse.current_object_type
  let currentPlayer = parsedResponse.current_player
  
  // Отображаем нужный шаблон если необходимо.
  if (currentObjectType != window.currentObjectType) {
    
    const selector = `#${currentObjectType}s`

    // Отображаем необходимый теплейт стадии игры.
    renderTemplate(selector, parsedResponse)

    // Обновляем имя второго игрока на странице.
    let playerTwoNameBlock = document.querySelector(".red h1")
    const playerTwoName = parsedResponse.players[1].nickname
    playerTwoNameBlock.innerText = playerTwoName

    // Меняем текстовый фон.
    const bg = document.querySelector(".custom__container")
    const clss = [
      "waiting-opponent",
      "picking-results", 
      "picking-maps",
      "picking-champs"
    ]
    bg.classList.remove(...clss)
    bg.classList.add(`picking-${currentObjectType}s`)

    window.currentObjectType = currentObjectType
    window.currentPlayer = currentPlayer
  }
}


/**
 * Заменяет текущее отображение в блоке main на отображение
 * шаблона по селектору.
 * @param {String} selector
 */
function renderTemplate(selector) {
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
  let body = newBody(
    "update",
    {
      "action": action,
      "nickname": nickname,
      "choice": choice,
      "object_type": objectType
    })
  if (appMode === "xhr") {
    sendRequest(body).then((response) => {
        localStorage.setItem("gameState", response.result)
    }).then(updateClasses).then(() => {
      setTimeout(rebuildPage, 4000)
    })
  } else if (appMode === "ws") {
    sendRequest(body, self.ws)
  } else {
    console.log("Выбран не верный режим работы приложения.")
  }
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
      // Функция выполнится при нажатии. this это текущий элемент
      // по которому был произведен клик.
      champOnClick(this)
    });
  });
}


/**
 * Заменяет действие при клике по кнопре "пригласить"
 * Сохраняет ссылку приглашения в буфер обмена.
 */
export function updateInviteListener () {
  const invite = document.querySelector(".invite")
  if (!invite) {return}

  invite.addEventListener("click", (event) => {
    event.preventDefault()
    const input = document.createElement("input");
    const route = window.location.host
    const room_uuid = window.location.pathname.split("/")[1]
    console.log(`${route}/join/${room_uuid}`)
    input.setAttribute("value", `http://${route}/join/${room_uuid}`)
    document.body.appendChild(input)
    input.select();
    const result = document.execCommand("copy")
    document.body.removeChild(input)
    return result
  })
}

/**
 * Функция выполняющаяся при клике по карточке карты/чемпиона.
 * @param {Object} obj 
 */
function champOnClick(obj) {

  const object = JSON.parse(localStorage.getItem("gameState"))
  const objectType = object.current_object_type

  // Добавляем класс card-active на кликнутую кнопку.
  obj.classList.add("card-active")
  // Отмечаем вложенный чекбокс.
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
 * Проигрывает звук.
 */
function play(soundId) {
  let snd = document.getElementById(soundId)
  snd.play();
}