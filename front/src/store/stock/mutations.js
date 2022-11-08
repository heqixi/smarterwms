import {ADD_OR_UPDATE_STOCK_LIST, STOCK_STATUS} from './types';

export default {
  get_stock_of_goods:({getters, state}) => async (goods) => {
    console.log("get goods from of goods ", goods);
    let stockList = getters.get_stock_of_goods(goods);
    console.log("get goods from of goods result", stockList)
  },

  [ADD_OR_UPDATE_STOCK_LIST](state, stockList) {
    stockList.forEach(stock => {
      let status = stock.stock_status;
      let targetList = undefined;
      switch (status) {
        case STOCK_STATUS.damage:
          targetList = state.stockDamage;
          break;
        case STOCK_STATUS.to_purchase:
          targetList = state.stockToPurchase;
          break;
        case STOCK_STATUS.purchased:
          targetList = state.stockPurchased;
          break;
        case STOCK_STATUS.reserve:
          targetList = state.stockReserve;
          break;
        case STOCK_STATUS.ship:
          targetList = state.stockShip;
          break;
        case STOCK_STATUS.back_order:
          targetList = state.shockBackOrder;
          break;
        default:
          //
      }
      if (targetList != undefined) {
        for(var i = 0; i < targetList.length; i++) {
          if (targetList[i].id == stock.id) {
            targetList.splic(i, 1);
            break;
          }
        }
        targetList.push(stock);
      }
      for (var i = 0; i < state.stockAll.length; i++) {
        if (state.stockAll[i].id == stock.id) {
          targetList.splice(i, 1);
          break;
        }
      }
      state.stockAll.push(stock);
    })
  }

}
