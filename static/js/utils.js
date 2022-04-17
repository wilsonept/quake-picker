import {sendRequest} from "/static/js/xhr.js"


/**
 * Получает текущее состояние игры с сервера с помощью xhr запроса.
 */
export function updatePage() {
  const body = getBody("get")
  sendRequest(body).then(rebuildPage)
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
 * @param {object} obj 
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
 * @param {object} params 
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

  if (parsedResponse.step > 16) {
    window.location.pathname = `/${parsedResponse.room_uuid}/results`
  }

  // Проверяем все ли игроки в комнате
  if (parsedResponse.players.length === 2) {
    // console.log('Все игроки в комнате, начинаем игру')
    
    let currentObject = parsedResponse.current_object
    
    // Отображаем нужный шаблон если необходимо
    if (currentObject != window.currentObject) {
      
      const selector = "#" + currentObject + "s"
      
      // Отображаем необходимый теплейт стадии игры.
      setTimeout(function() {
        renderTemplate(selector, parsedResponse)
      }, 4000)

      // Обновляем имя второго игрока на странице.
      // TODO Сделать в виде функции
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
 * @param {object} parsedResponse 
 */
function updateClasses(parsedResponse) {
  const nickname = window.location.pathname.split("/")[2]
  parsedResponse.players.forEach(player => {
    
    if (window.currentObject === "champ") {
      // Отмечаем забаненых чемпионов
      if (player.champ_bans) {
        player.champ_bans.forEach(champ => {
          let card = document.querySelector("#" + champ)
          card.classList.add("card-banned")
        })
      }
      
      // Отмечаем выбраных чемпионов
      if (player.champ_picks) {
        player.champ_picks.forEach(champ => {
          let card = document.querySelector("#" + champ)
          card.classList.add("card-picked")
        })
      }
      
      // Добавляем класс ожидания до тех пор пока
      // не придет очередь выбирать.
      parsedResponse.champs.forEach(champ => {
        const card = document.querySelector("#" + champ.name)
        if (parsedResponse.current_player !== nickname) {
          card.classList.add("card-waiting")
        } else {
          card.classList.remove("card-waiting")
        }
      })
    }
    
    if (window.currentObject === "map") {
      // Отмечаем забаненые карты
      if (player.map_bans) {
        player.map_bans.forEach(map => {
          let card = document.querySelector("#" + map)
          card.classList.add("card-banned")
        })
      }
      
      // Отмечаем выбраные карты
      if (player.map_picks) {
        player.map_picks.forEach(map => {
          let card = document.querySelector("#" + map)
          card.classList.add("card-picked")
        })
      }
      
      // Добавляем класс ожидания до тех пор пока
      // не придет очередь выбирать.
      parsedResponse.maps.forEach(map => {
        const card = document.querySelector("#" + map.name)
        if (parsedResponse.current_player !== nickname) {
          card.classList.add("card-waiting")
        }
        else {
          card.classList.remove("card-waiting")
        }
      })
    }
  })

  // Меняем сообщение выбора
  let actionMessage = document.querySelector("main h1")
  actionMessage.innerText = `${parsedResponse.current_player} ${parsedResponse.current_action}`
  
  // удаляем класс card-active со всех кнопок и снимаем чекбоксы
  const cards = document.querySelectorAll(".card")
  cards.forEach(card => {
    card.classList.remove("card-active")
    card.querySelector("input").checked = false
  })
}

/**
 * Заменяет текущее отображение в блоке main на
 * отображение шаблона по селектору.
 * @param {String} selector
 * @param {object} parsedResponse 
 */
function renderTemplate(selector, parsedResponse) {
  let main = document.querySelector("main")
  const template = document.querySelector(selector)
  // клонируем template
  const tempClone = template.content.cloneNode(true)
  // очищаем основной блок
  main.innerHTML = ""
  // вставляем клон в основной блок
  main.appendChild(tempClone)

  updateClasses(parsedResponse)
  updateListeners()
}


/**
 * Отправляем выбор пользователя на сервер с помощью xhr запроса.
 * @param {String} action 
 * @param {String} nickname 
 * @param {String} choice 
 * @param {String} objectType 
 */
function sendChoice(action, nickname, choice, objectType) {
  const body = getBody(
    "update", {
      "action": action,
      "nickname": nickname,
      "choice": choice,
      "object_type": objectType
    }
  )
  sendRequest(body).then(rebuildPage)
}
