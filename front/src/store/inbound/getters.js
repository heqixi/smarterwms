import {GET_GOODS_BY_ID, GET_GOODS_TO_PURCHASE, GET_GOODS_WAITING, GET_GOODS_TO_SORT, GET_GOODS_IN_STOCK, GET_GOODS_BY_PHASE, PHASE_TYPE}  from './types'


// function getGoodsToPurchase (state) {
//   return state.goodsToPurchaseList;
// }

export default {
  [GET_GOODS_TO_PURCHASE] (state) {
    return state.goodsToPurchaseList;
  },

  [GET_GOODS_WAITING] (state) {
    return state.goodsWaitingList;
  },

  [GET_GOODS_TO_SORT] (state) {
    return state.goodsToSortedList;
  },

  [GET_GOODS_IN_STOCK] (state) {
    return state.goodsInStockList;
  },

  get_goods_by_id: (state) => (phase, id) => {
    console.log("get asn obj by id ", phase, id);
    if (phase == PHASE_TYPE.purchase) {
      return state.goodsToPurchaseList.find((item) => {return item.id == id});
    }
    return undefined;
  },

  [GET_GOODS_BY_PHASE] (state, getters, currentPhase) {
    // console.log("getters ,", getters);
    // if (getters == undefined) {
    //   console.log("getters is undifined");
    // }
    // if (PHASE_TYPE.purchase == currentPhase) {
    //   return getters[GET_GOODS_TO_PURCHASE](state);
    // } else if (PHASE_TYPE.waiting == currentPhase) {
    //   return getters[GET_GOODS_WAITING](state);
    // } else if (PHASE_TYPE.sort == currentPhase) {
    //   return getters[GET_GOODS_TO_SORT](state);
    // } else if (PHASE_TYPE.stock == currentPhase) {
    //   return getters[GET_GOODS_IN_STOCK](state);
    // } else {
    //   return undefined;
    // }
  },
}
