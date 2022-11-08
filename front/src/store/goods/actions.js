import { getauth } from "src/boot/axios_request";
import {STOCK_PATH} from "./types";


export default {
  get_stock_of_goods:({getters, state}, goods) => {
    console.log("get goods from of goods ", goods);
    let stockList = getters.get_stock_of_goods(goods.id);
    console.log("get goods from of goods result", stockList);
    return stockList
  },

  action_get_stock_from_backend: async ({commit}, params) => {
    console.log("get stock from  backend ", params);
    let response = await getauth(STOCK_PATH + '?' + params);
    console.log("get stock from backend response ", response);
    commit(ADD_OR_UPDATE_STOCK_LIST, response.results);

  }
}
