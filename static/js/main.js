import {updatePage} from "/static/js/utils.js"
import {testSocket} from "/static/js/ws.js"

/*
* Режим работы - xhr.
  - Регистрируем запрос данных раз в 5 секунд.
  - Когда выполняется запрос мы получаем промис.
    - Цепочка удачного запроса.
      - Парсим ответ.
      - Перестраиваем страницу если необходимо.


* Режим работы - websocket.
  - Открываем websocket к серверу.
  - Когда приходят изменения:
      - Парсим ответ.
      - Перестраиваем страницу.
*/

// Режим работы приложения.
let appMode = "xhr"

if (appMode === "xhr") {
  // Запускаем авто обновление
  if (window.location.pathname.split("/")[2] !== "results") {
    const pageAutoUpdate = setInterval(updatePage, 5000)
  }

  if (typeof response !== "undefined") {
    localStorage.setItem("gameState", response.result)
    const parsedResponse = JSON.parse(response.result)

    // TODO Условие должно быть сгенерировано на основе режима игры в комнате.
    if (parsedResponse.step > 16) {
      clearInterval(pageAutoUpdate)
    }
  }
} else {
  const mySocket = testSocket()
  // TODO Переделать что бы websocket принимал JSON
  mySocket.send("update 129e833a-95e6-4563-8763-f01b5fa2785a")
}


// Всякая хрень.
window.onload = (event) => {
  function play() {
    let snd = document.getElementById("snd")
    snd.play();
  }
  play()
};