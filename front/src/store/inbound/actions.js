import {
  getauth,
  postauth,
  putauth,
  deleteauth,
  ViewPrintAuth
} from "boot/axios_request";

import { getNextPhase } from "./helper";
import {
  ACTION_MOVE_TO_NEXT_PHASE,
  ADD_GOODS_TO_PURCHASE,
  MOVE_TO_NEXT_PHASE,
  ACTION_ADD_GOODS_TO_PURCHASE,
  ACTION_SAVE_PURCHASE_LIST,
  ACTION_SAVE_PRESORT_LIST,
  ANS_PATH,
  ACTION_ASYNC_GET_ANS_LIST,
  INIT_ASN_LIST,
  ACTION_UPDATE_ASN_LIST,
  ADD_ASN_ORDER,
  ACTION_ADD_ANS_ORDER,
  ACTION_RETRIEVE_ASN_OBJ,
  ACTION_DELETE_ASN_OBJ,
  PHASE_TYPE,
  REMOVE_ITEM_IN_PHASE, ANS_DETAIL_MODEL
} from './types'

export default {
  async [ACTION_ASYNC_GET_ANS_LIST]({ commit }, params) {
    let path = ANS_PATH + "list/" +
      "?asn_details=1&asn_supplier=details&asn_order=1&asn_details_purchase=1&asn_details_goods=1" +
      "&goods_stocks=aggregation&purchases=true&supplier=true"
    if (params.status !== undefined) {
      path += '&asn_status=' + params.status
    }
    if (params.path) {
      path = params.path
    }
    let response = await getauth(path, {});
    let result = commit(INIT_ASN_LIST, response.results);
    return response;
  },

  [ACTION_MOVE_TO_NEXT_PHASE]({ commit }, currentPhase, index) {
    let nextPhase = getNextPhase(currentPhase);
    if (!nextPhase) {
      throw new Error(
        `Action ACTION_MOVE_TO_NEXT_PHASE illegal phase ${currentPhase}`
      );
    }
    commit(MOVE_TO_NEXT_PHASE, currentPhase, index);
  },

  [ACTION_ADD_GOODS_TO_PURCHASE]({ commit }, goods) {
    commit(ADD_GOODS_TO_PURCHASE, goods);
  },

  async [ACTION_SAVE_PURCHASE_LIST]({ commit, state }) {
    console.log("begin to save purchase list");
    let asnListToSave = [];
    state.goodsToPurchaseList.forEach(asnObj => {
      if (asnObj.new || asnObj.update) {
        var asnObjToSave = {
          partial: true,
          creater: asnObj.creater,
          asn_code: asnObj.asn_code,
          asn_status: asnObj.asn_status,
          total_qty: asnObj.total_qty,
          total_cost: asnObj.total_cost,
          total_weight: asnObj.total_weight,
          supplier: asnObj.supplier.id,
          id: asnObj.id // 如果没有id,后台会创建新记录，有则会更新
        };
        asnObjToSave.details = [];
        asnObj.details.forEach(asnDetails => {
          if (asnDetails.new || asnDetails.update) {
            var asnDetailsToSave = {
              partial: true,
              goods: asnDetails.goods.id,
              goods_qty: asnDetails[ANS_DETAIL_MODEL.goods_qty],
              goods_actual_qty: asnDetails[ANS_DETAIL_MODEL.goods_qty],
              goods_cost: asnDetails.goods_cost,
              purchase: asnDetails.purchase.id,
              id: asnDetails.id,
              is_delete: asnDetails.id && asnDetails.goods_qty <= 0
            };
            asnObjToSave.details.push(asnDetailsToSave);
          }
        });
        asnListToSave.push(asnObjToSave);
      }
    });

    const asnListSaved = await postauth(ANS_PATH + "list/", asnListToSave);
    // 把服务器返回的ID赋值给数据
    console.log('save asn data ', asnListSaved)
    asnListSaved.forEach(asnObjSave => {
      let localObj = state.goodsToPurchaseList.find(item => {
        return item.asn_code == asnObjSave.asn_code;
      });
      if (localObj !== undefined) {
        localObj.new = false;
        localObj.update = false;
        localObj.id = asnObjSave.id;
        asnObjSave.details.forEach(detailSaved => {
          let localDetail = localObj.details.find(
            item => item.goods.id === detailSaved.goods
          );
          if (localDetail !== undefined) {
            localDetail.id = detailSaved.id;
            localDetail.goods_qty = detailSaved.goods_qty;
            localDetail.new = false
            localDetail.update = false
          }
        });
        for (let i = localObj.details.length - 1; i >= 0; i--) {
          if (localObj.details[i].goods_qty <= 0) {
            localObj.details.splice(i, 1)
          }
        }
        console.log('after save local asnObj ', localObj)
      }
    });
    console.log("save list success ", asnListSaved);
  },

  async [ACTION_SAVE_PRESORT_LIST]({ commit, state }) {
    console.log("begin to save purchase list");
    let asnListToSave = [];
    state.goodsToSortedList.forEach(asnObj => {
      if (asnObj.new || asnObj.update) {
        var asnObjToSave = {
          partial: true,
          creater: asnObj.creater,
          asn_code: asnObj.asn_code,
          asn_status: asnObj.asn_status,
          total_qty: asnObj.total_qty,
          total_cost: asnObj.total_cost,
          total_weight: asnObj.total_weight,
          supplier: asnObj.supplier.id,
          id: asnObj.id // 如果没有id,后台会创建新记录，有则会更新
        };
        asnObjToSave.details = [];
        asnObj.details.forEach(asnDetails => {
          if (asnDetails.new || asnDetails.update) {
            var asnDetailsToSave = {
              partial: true,
              goods: asnDetails.goods.id,
              goods_qty: asnDetails[ANS_DETAIL_MODEL.goods_qty],
              goods_actual_qty: asnDetails.goods_actual_qty,
              goods_damage_qty: asnDetails.goods_damage_qty,
              goods_more_qty: asnDetails.goods_more_qty,
              goods_shortage_qty: asnDetails.goods_shortage_qty,
              goods_cost: asnDetails.goods_cost,
              purchase: asnDetails.purchase.id,
              id: asnDetails.id,
              is_delete: asnDetails.id && asnDetails.goods_qty <= 0
            };
            asnObjToSave.details.push(asnDetailsToSave);
          }
        });
        asnListToSave.push(asnObjToSave);
      }
    });

    const asnListSaved = await postauth(ANS_PATH + "list/", asnListToSave);
    console.log('save presorted data ', asnListSaved)
  },

  async [ACTION_DELETE_ASN_OBJ]({ commit }, id) {
    console.log("action_delete_asn_obj ", id);
    if (id === undefined) {
      throw new Error("please offer a valid id to delete asn obj");
    }
    let deleteAsn = await deleteauth(ANS_PATH + "list/" + id);
    console.log("delete asn obj of id ", id, " success  ", deleteAsn);
    let phase = undefined;
    if (deleteAsn.asn_status == 0) {
      phase = PHASE_TYPE.purchase;
    } else if (deleteAsn.asn_status == 1) {
      phase = PHASE_TYPE.waiting;
    } else if (deleteAsn.asn_status == 2) {
      phase = PHASE_TYPE.sort;
    } else if (deleteAsn.asn_status == 3) {
      phase = PHASE_TYPE.stock;
    }
    if (phase === undefined) {
      throw new Error(
        "action_delete_asn_obj illegal asn ",
        deleteAsn.asn_status
      );
    }
    commit(REMOVE_ITEM_IN_PHASE, { phase: phase, id: deleteAsn.id });
  },

  async [ACTION_UPDATE_ASN_LIST]({ commit, dispatch }, data) {
    console.log("ACTION_UPDATE_ASN_LIST ", data);
    let response = await putauth(ANS_PATH + "list/" + data.id + "/", data);
    console.log("ACTION_UPDATE_ASN_LIST response ", response);

    let newData = await getauth(
      ANS_PATH +
        "list/" +
        data.id +
        "?asn_details=1&asn_supplier=details&asn_order=1&asn_details_purchase=1&asn_details_goods=1&goods_stocks=aggregation&purchases=true",
      {}
    );
    console.log("get new data after update ", newData);
    commit(INIT_ASN_LIST, [newData]);
  },

  async [ACTION_ADD_ANS_ORDER]({ commit }, data) {
    console.log("ACTION_ADD_ANS_ORDER ", data);
    let response = await postauth(ANS_PATH + "order/", data);
    console.log("put order object to asn object response ", response);
    commit(ADD_ASN_ORDER, data);
  },

  async [ACTION_RETRIEVE_ASN_OBJ]({ commit }, data) {
    console.log("action_retrieve_asn_obj ", data);
    let response = await getauth(ANS_PATH + "list/" + data.id + "/", data);
    console.log("action_retrieve_asn_obj response  ", response);
  }
};
