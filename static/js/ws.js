import { sendRequest, newBody, updatePage } from "/static/js/utils.js"

// Включаем строгий режим.
"use strict"



/**
 * Открывает веб-сокет и оборачивает его в Promise.
 * @param {String} uri
 * @returns {Promise}
 */
export function openWS(uri) {
  
  return new Promise(function(resolve, reject) {
    // Создаем веб-сокет.
    const mySocket = new WebSocket(uri)

    mySocket.onopen = () => {
      console.log("[ ws ] Подключение успешно.")
      console.log("[ ws ] Запрашиваю состояние игры.")
      const body = newBody("get")
      sendRequest(body, mySocket)
      resolve(mySocket)
    }

    mySocket.onclose = (event) => {
      console.log("[ ws ] Подключение закрыто.")
      console.log(event)
    }

    mySocket.onerror = (error) => {
      reject(error)
    }

    mySocket.onmessage = (event) => {
      console.log("[ ws ] Принимаю сообщение.")
      // Сохраняем данные в localStorage.
      localStorage.setItem("gameState", event.data)
      // Запускаем цепочку обновления страницы.
      updatePage()
    }
  })
}
