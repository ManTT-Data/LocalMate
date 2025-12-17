import Cookies from "js-cookie";

export function setCookie(key, value, options) {
  Cookies.set(key, value, options);
}

export function getCookie(key) {
  return Cookies.get(key);
}

export function removeCookie(key) {
  Cookies.remove(key);
}
