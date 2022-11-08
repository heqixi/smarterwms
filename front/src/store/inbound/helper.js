import {PHASE_TYPE, GET_GOODS_TO_PURCHASE,GET_GOODS_WAITING, GET_GOODS_TO_SORT, GET_GOODS_IN_STOCK, ANS_PATH} from "./types";

import {SessionStorage, LocalStorage } from "quasar";
import {getauth, postauth, putauth, deleteauth} from "boot/axios_request";


const getNextPhase = function (currentPhase) {
  if (PHASE_TYPE.purchase == currentPhase) {
    return PHASE_TYPE.waiting;
  } else if (PHASE_TYPE.waiting == currentPhase) {
    return PHASE_TYPE.sort;
  } else if (PHASE_TYPE.sort == currentPhase) {
    return PHASE_TYPE.stock;
  }
  return undefined;
}

const getGetterNameByPhase = function(currentPhase) {
  if (PHASE_TYPE.purchase == currentPhase) {
    return GET_GOODS_TO_PURCHASE;
  } else if (PHASE_TYPE.waiting == currentPhase) {
    return GET_GOODS_WAITING;
  } else if (PHASE_TYPE.sort == currentPhase) {
    return GET_GOODS_TO_SORT;
  } else if (PHASE_TYPE.stock == currentPhase) {
    return GET_GOODS_IN_STOCK;
  } else {
    return undefined;
  }
}

const getStockQty = function(goods, status) {
  return goods.stock.reduce((total, stockRecord) => {
    if (status.indexOf(stockRecord.stock_status) > -1) {
      total += stockRecord.stock_qty;
    }
    return total;
  }, 0);
}

const aggregateStockQty = function(asnDetailsList, status) {
  console.log("aggregateStockQty ", asnDetailsList);
  return asnDetailsList.reduce((total, details) => {
    return total + getStockQty(details.goods, status);
  }, 0);
}

const saveList = async function(dataList) {
  let formData = {}
  formData.creater = LocalStorage.getItem("login_name");
  formData.data = dataList
  console.log("save list begin ", res.detail);
  let res = await postauth(ANS_PATH + "list/", formData);
  console.log("save list success ", res.detail);
  return res;
}

const uuidGenerator = function(len, radix) {
  var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.split('');
  var uuid = [], i;
  radix = radix || chars.length;

  if (len) {
    // Compact form
    for (i = 0; i < len; i++) uuid[i] = chars[0 | Math.random() * radix];
  } else {
    // rfc4122, version 4 form
    var r;
    // rfc4122 requires these characters
    uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
    uuid[14] = '4';

    // Fill in random data.  At i==19 set the high bits of clock sequence as
    // per rfc4122, sec. 4.1.5
    for (i = 0; i < 36; i++) {
      if (!uuid[i]) {
        r = 0 | Math.random() * 16;
        uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r];
      }
    }
  }
  const uuidStr = uuid.join('')
  console.log('generate uuid ', uuidStr)
  return uuidStr;
}

export {
  getNextPhase,
  getGetterNameByPhase,
  aggregateStockQty,
  getStockQty,
  uuidGenerator
}
