import {
  GET_STOCK_ON_HAND,
  GET_STOCK_TO_PURCHASE,
  GET_STOCK_PURCHASED,
  GET_STOCK_RESERVE,
  GET_STOCK_SHIP,
  GET_STOCK_DAMAGE,
  GET_STOCK_BACK_ORDER
} from "./types";


export default {
  [GET_STOCK_ON_HAND] (state) {
    return state.stockOnHand;
  },

  [GET_STOCK_TO_PURCHASE] (state) {
    return state.stockOnHand;
  },

  [GET_STOCK_PURCHASED] (state) {
    return state.stockPurchased;
  },

  [GET_STOCK_RESERVE] (state) {
    return state.stockReserve;
  },

  [GET_STOCK_SHIP] (state) {
    return state.stockShip;
  },

  [GET_STOCK_DAMAGE] (state) {
    return state.stockDamage;
  },

  [GET_STOCK_BACK_ORDER] (state) {
    return state.shockBackOrder;
  },

  get_stock_of_goods: (state) => (goods_id) => {
    console.log("getters get stock of goods ", goods_id);
    return state.stockAll.filter(stock => stock.goods === goods_id);
  },

  get_spec_stock_of_goods: (state) => (status, goods_id) => {
    // TODO
  }
}
