let response_text = `{'id': 1, 'jsonrpc': '2.0', 'result': '{"current_action": "ban", "players": [{"nickname": "Ashot", "map_picks": [], "map_bans": [], "champ_picks": ["eisen"], "champ_bans": ["ranger"]}, {"nickname": "Avenue", "map_picks": [], "map_bans": [], "champ_picks": ["doom"], "champ_bans": ["galena"]}], "room_uuid": "7ad138ca-b89e-463d-8345-d7314fa76aa2", "seed": 2, "maps": ["The Molten Falls", "Ruins of Sarnath", "Vale of Pnath", "Awoken", "Corrupted Keep", "Exile", "Deep Embrace"], "champs": ["Anarki", "Athena", "BJ Blaskowitz", "Clutch", "Death Knight", "Doom", "Eisen", "Galena", "Keel", "Nyx", "Ranger", "Scalebearer", "Slash", "Sorlag", "Strogg", "Visor"], "current_player": "Avenue"}'}`
let currentObject // Переменная для champion или map
let currentStep = 0
let gameState
const steps = [
  'pick', 'pick', 'ban', 'ban', 'pick', 'pick', 'ban', 'ban', 'pick', 'pick'
]

const champions = [
  'nyx', 'anarky', 'slash', 'athena', 'ranger', 'visor',
  'galena', 'bj', 'doom', 'strogg', 'deathknight', 'eisen',
  'clutch', 'sorlag', 'scalebearer', 'keel'
]

function updateListeners () {
  // получаем список всех кнопок выбора
  const cards = document.querySelectorAll(".card")

  cards.forEach(button => {
    // Вешаем листенер нажатия на кнопки
    button.addEventListener('click', function (event) {
      // Отменяем поведение при клике по лейблу по умолчанию. Если этого не
      // сделать, то клик будет выполняться дважды. Один раз стандартный второй
      // тот который мы создали. Это приведет к двойному вызову данной функции.
      event.preventDefault()
      // Функция выполнится при нажатии. this это текущий элемент по которому
      // был произведен клик
      champOnClick(this)
    });
  });
}

function getBody(type, params) {
  let template

  if (type === 'set') {
    template = {
      "jsonrpc": "2.0",
      "method": "app.updateState",
      "params": {
          "room_uuid": window.location.pathname.split('/')[1],
          "action": params['action'],
          "nickname": params['nickname'],
          "object_type": params['object_type'],
          "choice": params['choice']
      },
      "id": 1
    }
  } else {
    template = {
      "jsonrpc": "2.0",
      "method": "app.getState",
      "params": {
          "room_uuid": window.location.pathname.split('/')[1],
      },
      "id": 1
    }
  }

  return template
}


// function showResults() {
//   const gameState = JSON.parse(localStorage.getItem('gameState'))

//   let index = 1
//   let maps = gameState.players[0].map_picks
//   gameState.players[1].map_picks.map(map => {
//     maps.splice(index, 0, map)
//     index = index + 2
//   })
// }

function champOnClick(obj) {

  // console.log('click')
  const object = JSON.parse(localStorage.getItem('gameState'))
  const objectType = object.current_object

  // добавляем класс card-active на кликнутую кнопку
  obj.classList.add('card-active')
  // отмечаем вложенный чекбокс
  let checkBox = obj.querySelector('.card input')
  checkBox.checked = true

  const cards = document.querySelectorAll('.card')
  cards.forEach(card => {
    card.classList.add('card-waiting')
  })

  const gameState = JSON.parse(localStorage.getItem('gameState'))
  const action = gameState.current_action
  const nickname = window.location.pathname.split('/')[2]
  const choice = obj.getAttribute('id')

  sendChoice(action, nickname, choice, objectType)
}


function updateClasses(parsedResponse) {
  const nickname = window.location.pathname.split('/')[2]
  parsedResponse.players.forEach(player => {
    
    if (window.currentObject === 'champ') {
      // Отмечаем забаненых чемпионов
      if (player.champ_bans) {
        player.champ_bans.forEach(champ => {
          let card = document.querySelector('#' + champ)
          card.classList.add('card-banned')
        })
      }
      
      // Отмечаем выбраных чемпионов
      if (player.champ_picks) {
        player.champ_picks.forEach(champ => {
          let card = document.querySelector('#' + champ)
          card.classList.add('card-picked')
        })
      }
      
      // Добавляем класс ожидания до тех пор пока не придет очередь выбирать.
      parsedResponse.champs.forEach(champ => {
        const card = document.querySelector('#' + champ.name)
        if (parsedResponse.current_player !== nickname) {
          card.classList.add('card-waiting')
        } else {
          card.classList.remove('card-waiting')
        }
      })
    }
    
    if (window.currentObject === 'map') {
      // Отмечаем забаненые карты
      if (player.map_bans) {
        player.map_bans.forEach(map => {
          let card = document.querySelector('#' + map)
          card.classList.add('card-banned')
        })
      }
      
      // Отмечаем выбраные карты
      if (player.map_picks) {
        player.map_picks.forEach(map => {
          let card = document.querySelector('#' + map)
          card.classList.add('card-picked')
        })
      }
      
      // Добавляем класс ожидания до тех пор пока не придет очередь выбирать.
      parsedResponse.maps.forEach(map => {
        const card = document.querySelector('#' + map.name)
        if (parsedResponse.current_player !== nickname) {
          card.classList.add('card-waiting')
        }
        else {
          card.classList.remove('card-waiting')
        }
      })
    }
  })

  // Меняем сообщение выбора
  let actionMessage = document.querySelector('main h1')
  actionMessage.innerText = `${parsedResponse.current_player} ${parsedResponse.current_action}`
  
  // удаляем класс card-active со всех кнопок и снимаем чекбоксы
  const cards = document.querySelectorAll('.card')
  cards.forEach(card => {
    card.classList.remove('card-active')
    card.querySelector('input').checked = false
  })
}


function sendRequest(body) {
  return new Promise((resolve, reject) => {
    const endPoint = "/api"
    const xhr = new XMLHttpRequest()

    xhr.open('POST', endPoint)

    xhr.responseType = 'json'
    xhr.setRequestHeader(
      "Content-Type",
      "application/json"
    )
    xhr.onload = () => {
      if (xhr.status >= 400) {
        reject(xhr.response)
      } else {
        resolve(xhr.response)
      }
    }

    xhr.onerror = () => {
      reject(xhr.response)
    }

    xhr.send(JSON.stringify(body))
  })
}

function renderTemplate(selector, parsedResponse) {
  let main = document.querySelector('main')
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

function rebuildPage(response) {
  
  localStorage.setItem('gameState', response.result)
  const parsedResponse = JSON.parse(response.result)

  if (parsedResponse.step === 16) {
    window.location.pathname = `/${parsedResponse.room_uuid}/results`
  }

  // Проверяем все ли игроки в комнате
  if (parsedResponse.players.length === 2) {
    // console.log('Все игроки в комнате, начинаем игру')
    
    let currentObject = parsedResponse.current_object
    
    // Отображаем нужный шаблон если необходимо
    if (currentObject != window.currentObject) {
      
      const selector = '#' + currentObject + 's'
      
      // Отображаем необходимый теплейт стадии игры.
      setTimeout(function() {
        renderTemplate(selector, parsedResponse)
      }, 4000)

      // Обновляем имя второго игрока на странице.
      // TODO Сделать в виде функции
      setTimeout(function() {
        let playerTwoNameBlock = document.querySelector('.red h1')
        const playerTwoName = parsedResponse.players[1].nickname
        playerTwoNameBlock.innerText = playerTwoName
      }, 4000)

      window.currentObject = currentObject
    }
    
    if (document.querySelector('.card')) {
      updateClasses(parsedResponse)
    }
    
  }
  else {
    console.log('Ждем второго игрока')
  }
}

function updatePage() {
  // Получает текущее состояние игры с сервера
  const body = getBody('get')
  sendRequest(body).then(rebuildPage)
}

// TODO sendChoice
function sendChoice(action, nickname, choice, objectType) {
  const body = getBody(
    "set", {
      "action": action,
      "nickname": nickname,
      "choice": choice,
      "object_type": objectType
    }
  )
  sendRequest(body).then(rebuildPage)
}

// Запускаем авто обновление
// TODO Разобраться как отключать авто обновление
if (window.location.pathname.split('/')[2] !== 'results') {
  const pageAutoUpdate = setInterval(updatePage, 5000)
}

if (typeof response !== 'undefined') {
  localStorage.setItem('gameState', response.result)
  const parsedResponse = JSON.parse(response.result)

  // TODO Условие должно быть сгенерировано на основе режима игры в комнате.
  if (parsedResponse.step >= 16) {
    clearInterval(pageAutoUpdate)
  }
}

