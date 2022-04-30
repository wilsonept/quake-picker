// Включаем строгий режим.
"use strict"


/**
 * Тестируем работу с websocket
 */
export function testSocket() {
        
  // create websocket instance
  let mySocket = new WebSocket("ws://127.0.0.1:5000/get_state");

  mySocket.onmessage = function (event) {
      console.log(event.data)
      document.getElementsByTagName('h1')[0].innerText = event.data
  }
  
  return mySocket;
}

