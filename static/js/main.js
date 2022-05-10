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

// Режим работы приложения.
self.appMode = "ws"

if (appMode === "xhr") {

  // Запускаем авто обновление по интервалу.
  const pageAutoUpdate = setInterval(() => {
    const body = newBody("get")
    // Отправляем запрос и сохраняем ответ в localStorage затем 
    // запускает цепочку обночления страницы.
    sendRequest(body).then((response) => {
      localStorage.setItem("gameState", response.result)
    }).then(updatePage)
  }, 5000)
  
  // Сохраняем индекс интервала в localStorage.
  localStorage.setItem("pageAutoUpdate", pageAutoUpdate)

} else if (appMode === "ws") {
  // Открываем сокет и сохраняем его глобально в объекте window.
  self.ws = openWS("ws://127.0.0.1:5000/ws")
}

// Всякая хрень.
// window.onload = (event) => {
//   function play() {
//     let snd = document.getElementById("snd")
//     snd.play();
//   }
//   play()
// };