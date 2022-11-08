export const STOCK_PATH = 'stock/list/'

export const STOCK_MODEL = {
  goods: 'goods',
  stock_status: 'stock_status',
  stock_qty: 'stock_qty'
}

export const STOCK_STATUS = {
  damage: -1,
  to_purchase: 0,
  purchased: 1,
  sorted: 2,
  on_hand: 3,
  reserve: 11,
  ship: 12,
  back_order: 13
}

export const STOCK_STATUS_NAME = {
  damage: '损坏库存',
  to_purchase: '待购买库存',
  purchased: '已购买库存',
  sorted: '已分拣库存',
  on_hand: '现有库存',
  reserve: '保留库存',
  ship: '已出货库存',
  back_order: '退货库存'
}

export const stockStatus2Str = function (stockStatus) {
  if (stockStatus === STOCK_STATUS.damage) {
    return STOCK_STATUS_NAME.damage
  } else if (stockStatus === STOCK_STATUS.to_purchase) {
    return STOCK_STATUS_NAME.to_purchase
  } else if (stockStatus === STOCK_STATUS.purchased) {
    return STOCK_STATUS_NAME.purchased
  } else if (stockStatus === STOCK_STATUS.sorted) {
    return STOCK_STATUS_NAME.sorted
  } else if (stockStatus === STOCK_STATUS.on_hand) {
    return STOCK_STATUS_NAME.on_hand
  } else if (stockStatus === STOCK_STATUS.reserve) {
    return STOCK_STATUS_NAME.reserve
  } else if (stockStatus === STOCK_STATUS.ship) {
    return STOCK_STATUS_NAME.ship
  } else if (stockStatus === STOCK_STATUS.back_order) {
    return STOCK_STATUS_NAME.back_order
  } else {
    throw new Error(`unknow stock status ${stockStatus}`)
  }
}

// getters
export const GET_STOCK_ON_HAND = 'get_stock_on_hand'

export const GET_STOCK_TO_PURCHASE = 'get_stock_to_purchase'

export const GET_STOCK_PURCHASED = 'get_stock_purchased'

export const GET_STOCK_DAMAGE = 'get_stock_damage'

export const GET_STOCK_RESERVE = 'get_stock_reserve'

export const GET_STOCK_SHIP = 'get_stock_ship'

export const GET_STOCK_BACK_ORDER = 'get_stock_back_order'

// mutations
export const ADD_OR_UPDATE_STOCK_LIST = 'append_stock_list'

// actions
export const ACTION_READ_STOCK = 'action_read_stock'
