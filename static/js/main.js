import { updatePage, sendRequest, newBody } from "/static/js/utils.js"
import { openWS } from "/static/js/ws.js"

// Включаем строгий режим.
"use strict"


/*
* Режим работы - xhr.
  - Регистрируем запрос данных раз в 5 секунд.
  - Когда выполняется запрос мы получаем промис.
    Цепочка удачного запроса:
      - Сохраняем ответ в localStorage.
      - Перестраиваем страницу если необходимо.


* Режим работы - websocket.
  - Открываем websocket к серверу и запрашиваем состояние.
  - Когда приходят изменения:
      - Сохраняем ответ в localStorage.
      - Перестраиваем страницу если необходимо.
*/


function initApplication(mode) {
  // Режим работы приложения.
  self.appMode = mode

  if (appMode === "xhr") {
    // Запускаем авто обновление по интервалу.
    const pageAutoUpdate = setInterval(() => {
      // Останавливаем авто обновление страницы если оно больше не нужно.
      const gameStep = window.location.pathname.split("/")[1]
      if (gameStep === "results" || appMode === "ws") {
        try {
          clearInterval(pageAutoUpdate)
          return
        }
        catch {
          console.log("IntervalId не определена 'undefined'")
        }
      }
      const body = newBody("get")
      // Отправляем запрос и сохраняем ответ в localStorage затем 
      // запускает цепочку обновления страницы.
      sendRequest(body).then((response) => {
        localStorage.setItem("gameState", response.result)
      }).then(updatePage)
    }, 5000)
    
    // Сохраняем индекс интервала в localStorage.
    localStorage.setItem("pageAutoUpdate", pageAutoUpdate)

  } else if (appMode === "ws") {
    if (self.ws) {self.ws.close()}
    // Открываем сокет и сохраняем его глобально в объекте window.
    self.ws = openWS("ws://127.0.0.1:5000/ws")
  }
}

/**
 * Переключает режим работы приложения.
 */
export function switchMode() {
  if (appMode === "ws") {
    console.log("[ switchMode ] Режим приложения переключен в режим xhr")
    initApplication("xhr")
  } else {
    console.log("[ switchMode ] Режим приложения переключен в режим ws")
    initApplication("ws")
  }
}

initApplication("xhr")
