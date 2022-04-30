// Включаем строгий режим.
"use strict"


/**
 * Отправляет фоновый запрос на сервер.
 * @param {object} body 
 * @returns {Promise}
 */
export function sendRequest(body) {
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