import {
  MODEL_NAME,
  ASN_STATUS,
  INIT_ASN_LIST,
  ADD_GOODS_TO_PURCHASE,
  REMOVE_ITEM_IN_PHASE,
  MOVE_TO_NEXT_PHASE,
  PHASE_TYPE,
  UPDATE_FIELD,
  ASN_MODEL,
  ANS_DETAIL_MODEL,
  ANS_DETAIL_GOODS_MODEL,
  ADD_ASN_ORDER,
  ACTION_UPDATE_ASN_LIST,
  ACTION_SAVE_PURCHASE_LIST,
  UPDATE_PRUCHASE_QTY,
  UPDATE_ACTUAL_QTY, ACTION_SAVE_PRESORT_LIST
} from './types'

import getters from './getters'

import { LocalStorage } from 'quasar'

import {
  getNextPhase, getGetterNameByPhase, uuidGenerator
} from './helper'

export default {

  [INIT_ASN_LIST] (state, asnlist) {
    console.log('INIT_ASN_LIST asnlist ', asnlist)
    asnlist.forEach(asnObj => {
      let asn_status = asnObj.asn_status
      let asnStateList = undefined
      if (asn_status === ASN_STATUS.purchase) {
        asnStateList = state.goodsToPurchaseList
      } else if (asn_status === ASN_STATUS.waiting) {
        asnStateList = state.goodsWaitingList
      } else if (asn_status === ASN_STATUS.sort) {
        asnStateList = state.goodsToSortedList
      } else if (asn_status === ASN_STATUS.stock) {
        asnStateList = state.goodsInStockList
      } else {
        throw Error('unknow asn status of asn id', asnObj.id)
      }
      for (var i = 0; i < asnStateList.length; i++) {
        if (asnStateList[i].id === asnObj.id) {
          asnStateList.splice(i, 1)
          break
        }
      }
      asnStateList.push(asnObj)
      // 获取每个产品的库存信息
      asnObj.details.forEach(item => {
        let goods = item.goods
        goods.purchase = item.purchase
        asnObj.stock_onhand = goods.stocks.stock_onhand
        asnObj.stock_consume = goods.stocks.stock_ship
        asnObj.stock_reserved = goods.stocks.stock_reserve
      })
      asnObj.details.sort((detailA, detailB) => {
        if (detailA.purchase.tag === detailB.purchase.tag) {
          return 0
        }
        if (detailA.purchase.tag > detailB.purchase.tag) {
          return 1
        }
        return -1
      })
    })
  },

  [ADD_GOODS_TO_PURCHASE] (state, goodsList) {
    console.log('mutations ADD_GOODS_TO_PURCHASE ', goodsList)
    let goodsToPurchaseList = state.goodsToPurchaseList
    goodsList.forEach(goods => {
      let find = false
      const purchaseNum = parseInt(goods.purchase_num) || 1 // 最小是1
      let asn_details = {
        new: true,
        goods: goods,
        goods_qty: purchaseNum,
        goods_actual_qty: purchaseNum,
        goods_shortage_qty: 0,
        goods_more_qty: 0,
        goods_damage_qty: 0,
        goods_cost: purchaseNum * parseFloat(goods.purchase.price),
        purchase: goods.purchase
      }
      console.log('add data ,detail ', asn_details)
      goodsToPurchaseList.forEach(asnObj => {
        // 判断是否已有供应商
        if (asnObj.supplier.id === asn_details.purchase.supplier.id) {
          find = true
          console.log('add good exit ', asnObj.supplier.supplier_name)
          // 判断是不是已有的产品
          const existDetails = asnObj.details
          let exist = false
          existDetails.forEach(item => {
            if (item.goods.goods_code === goods.goods_code) {
              exist = true
            }
          })
          if (exist) {
            console.log('goods exist ', goods.goods_code)
            return
          }
          console.log('goods ', goods.goods_code, ' not exist yet')
          asnObj.update = true // 用于增量更新到后台的标志位
          asnObj.details.push(asn_details)
          // asnObj.details.push(asn_details) //TODO
          // 更新ASN信息
          asnObj.stock_onhand += goods.stocks.stock_onhand
          asnObj.stock_consume += goods.stocks.stock_ship
          asnObj.stock_reserved += goods.stocks.stock_reserve
          asnObj.total_qty += parseInt(asn_details.goods_qty)
          asnObj.total_cost += asn_details.goods_cost
          asnObj.total_weight += asn_details.goods_qty * goods.goods_weight
        }
      })
      if (!find) {
        let date = new Date()
        let asn = 'ANS-' + date.getFullYear() + (date.getMonth() + 1) + date.getDate() + uuidGenerator(4,32)
        console.log('asn', asn)
        goodsToPurchaseList.push({
          new: true, // 用于增量更新到后台的标志位
          creater: LocalStorage.getItem('login_name'),
          asn_code: asn, // ASN 字段
          asn_status: ASN_STATUS.purchase, // // ASN 字段
          total_weight: asn_details.goods_qty * goods.goods_weight, // ASN 字段
          supplier: goods.purchase.supplier, // ASN 字段
          total_qty: parseInt(asn_details.goods_qty),
          total_cost: asn_details.goods_cost, // ASN 字段
          stock_onhand: goods.stocks.stock_onhand,
          stock_consume: goods.stocks.stock_ship,
          stock_reserved: goods.stocks.stock_reserve,
          details: [asn_details]
        })
      }
    })
    // this.dispatch(MODEL_NAME + ACTION_SAVE_PURCHASE_LIST)
  },

  // 删除元素
  [REMOVE_ITEM_IN_PHASE] (state, data) {
    console.log('mutations REMOVE_ITEM_IN_PHASE ', data)
    let phase = data.phase
    let id = data.id
    let targetPhase = undefined
    if (PHASE_TYPE.purchase === phase) {
      targetPhase = state.goodsToPurchaseList
    } else if (PHASE_TYPE.waiting == phase) {
      targetPhase = state.goodsWaitingList
    } else if (PHASE_TYPE.sort == phase) {
      targetPhase = state.goodsToSortedList
    } else if (PHASE_TYPE.stock == phase) {
      targetPhase = state.goodsInStockList
    } else {
      throw new Error('Illegal phase ', phase)
    }
    let index = -1
    targetPhase.forEach((item, asnIndex) => {
      if (item.id == id) {
        index = asnIndex
      }
    })
    if (index < 0 || index > targetPhase.length) {
      throw new Error('REMOVE_ITEM_IN_PHASE illegal index ', index)
    }
    targetPhase.splice(index, 1)
  },

  // 下一状态： 采购中 -> 已采购 -> 已到货 -> 已入库
  [MOVE_TO_NEXT_PHASE] (state, data) {
    console.log('move to next Phase 2 currentPhase ', data)
    let currentPhase = data.currentPhase
    let asn_id = data.asn_id
    let getterName = getGetterNameByPhase(currentPhase)
    let currentPhaseList = getters[getterName](state)
    if (currentPhaseList === undefined) {
      throw new Error('MOVE_TO_NEXT_PHASE illegal phase ', currentPhase)
    }
    let index = -1
    currentPhaseList.forEach((item, asnIndex) => {
      if (item.id === asn_id) {
        index = asnIndex
      }
    })
    if (index < 0 || index >= currentPhaseList.length) {
      throw new Error('mutations MOVE_TO_NEXT_PHASE illegal index', index)
    }
    let asnObject = currentPhaseList.splice(index, 1)[0]
    let nextPhase = getNextPhase(currentPhase)
    if (nextPhase === undefined) {
      throw new Error(`MOVE_TO_NEXT_PHASE could not decide next phase for currentPhase ${currentPhase}`)
    }
    getterName = getGetterNameByPhase(nextPhase)
    let nextPhaseList = getters[getterName](state)
    asnObject[ASN_MODEL.asn_status] += 1
    nextPhaseList.push(asnObject)

    // 把采购单状态同步到服务端
    let dataToUpdate = {
      partial: true,
      id: asnObject[ASN_MODEL.id],
      asn_status: asnObject[ASN_MODEL.asn_status]
    }
    this.dispatch(MODEL_NAME + ACTION_UPDATE_ASN_LIST, dataToUpdate)
  },

  [ADD_ASN_ORDER] (state, data) {
    console.log('ADD_ASN_ORDER ', data)
    let asnObj = state.goodsToPurchaseList.find(item => {
      return item.id === data.asn
    })
    if (asnObj === undefined) {
      throw new Error(`ADD_ASN_ORDER asn object of id ${data.asn_id} not found`)
    }
    asnObj.order = data
  },

  [UPDATE_FIELD] (state, item) {
    console.log('UPDATE_FIELD ', item)
    let type = item.phase
    let whichAsn = item.row_id
    let detailsId = item.subrow_id
    let fieldName = item.field_name
    let value = item.value
    let asnObj = undefined
    if (type == PHASE_TYPE.purchase) {
      asnObj = state.goodsToPurchaseList.find(asn => {
        return asn.id == whichAsn
      })
    }
    if (asnObj == undefined) {
      throw new Error('asn object not found ,param ', item)
    }
    if (detailsId > -1) {
      let detailObj = asnObj.details[0]
      if (detailObj == null) {
        throw new Error('asn detail of ans object not found ', item)
      }
      if (fieldName == ANS_DETAIL_MODEL.goods_qty) {
        // 更新 进货单 的统计信息
        let diff = value - detailObj[ANS_DETAIL_MODEL.goods_qty]
        asnObj.total_qty += diff
        // cost 更新
        asnObj.total_cost += detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.supplier].price * diff
        asnObj.total_weight += detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.goods_weihgt] * diff
        detailObj[ANS_DETAIL_MODEL.goods_qty] = value
        return objectToUpdate
      }
    }
  },

  [UPDATE_PRUCHASE_QTY] (state, item) {
    const asnObj = state.goodsToPurchaseList.find(asn => {
      return asn.id === item.asnId
    })
    if (asnObj === undefined) {
      throw new Error('asn object not found ,param ', item)
    }
    const detailObj = asnObj.details.find(details => {
      return details.id === item.detailsId
    })
    if (detailObj === undefined) {
      throw new Error('asn detail object not found ,param ', item.detailsId)
    }
    console.log('mutation update qyt ', asnObj, detailObj, item)
    // 更新 进货单 的统计信息
    const diff = item.newQty - detailObj[ANS_DETAIL_MODEL.goods_qty]
    asnObj.total_qty += diff
    // cost 更新
    const costDiff = (detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.purchase].price * diff)
    const weightDiff = (detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.goods_weight] * diff)
    console.log('mutation update qty diff ', costDiff, weightDiff)
    asnObj.total_cost += costDiff
    asnObj.total_weight += weightDiff
    detailObj[ANS_DETAIL_MODEL.goods_qty] = item.newQty
    detailObj[ANS_DETAIL_MODEL.goods_actual_qty] = item.newQty
    asnObj.update = true
    detailObj.update = true
    this.dispatch(MODEL_NAME + ACTION_SAVE_PURCHASE_LIST)
  },

  [UPDATE_ACTUAL_QTY] (state, item) {
    const asnObj = state.goodsToSortedList.find(asn => {
      return asn.id === item.asnId
    })
    if (asnObj === undefined) {
      throw new Error('asn object not found ,param ', item)
    }
    const detailObj = asnObj.details.find(details => {
      return details.id === item.detailsId
    })
    if (detailObj === undefined) {
      throw new Error('asn detail object not found ,param ', item.detailsId)
    }
    if (item.goods_actual_qty !== undefined) {
      detailObj[ANS_DETAIL_MODEL.goods_actual_qty] = item.goods_actual_qty
      const diff = detailObj[ANS_DETAIL_MODEL.goods_qty] - item.goods_actual_qty
      if (diff > 0) {
        detailObj[ANS_DETAIL_MODEL.goods_shortage_qty] = diff
      }
      if (diff < 0) {
        detailObj[ANS_DETAIL_MODEL.goods_more_qty] = diff
      }
    }
    if (item.goods_damage_qty > 0) {
      detailObj[ANS_DETAIL_MODEL.goods_damage_qty] = item.goods_damage_qty
    }
    asnObj.update = true
    detailObj.update = true
    this.dispatch(MODEL_NAME + ACTION_SAVE_PRESORT_LIST)
  }
}
