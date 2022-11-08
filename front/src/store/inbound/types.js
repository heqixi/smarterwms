// getters
export const MODEL_NAME = 'inbound/';

export const ANS_PATH = "asn/";

export const PHASE_TYPE = {
  purchase: '待下单',
  waiting: '采购中',
  sort: '待分拣',
  stock: '已入库'
};

export const ASN_STATUS = {
  purchase: 0,
  waiting: 1,
  sort: 2,
  stock: 3
};

export const ASN_MODEL = {
  id: 'id',
  asn_code: 'asn_code',
  asn_status: 'asn_status',
  total_qty: 'total_qty',
  total_weight: 'total_weight',
  total_cost: 'total_cost',
  supplier: 'supplier',
  bar_code: 'bar_code',
  transportation_fee: 'transportation_fee'
}

export const ANS_DETAIL_MODEL = {
  id: 'id',
  asn: 'asn',
  goods: 'goods',
  goods_qty: 'goods_qty',
  goods_actual_qty: 'goods_actual_qty',
  goods_shortage_qty: 'goods_shortage_qty',
  goods_more_qty: 'goods_more_qty',
  goods_damage_qty: 'goods_damage_qty',
  goods_cost: 'goods_cost',
  stock: 'stock'
}

export const ANS_DETAIL_GOODS_MODEL = {
  goods_code: 'goods_code',
  goods_weight: 'goods_weight',
  goods_id: 'goods_id',
  stock: 'stock',
  purchase: 'purchase',
  supplier_info: 'supplier_info',
  variants: 'variants'
}



// getters
export const GET_GOODS_TO_PURCHASE = 'get_goods_to_purchase';

export const GET_GOODS_WAITING = 'get_goods_waiting';

export const GET_GOODS_TO_SORT = 'get_goods_to_sort';

export const GET_GOODS_IN_STOCK = 'get_goods_in_stock';

export const GET_GOODS_BY_PHASE = 'get_goods_by_phase';

export const GET_GOODS_BY_ID = 'get_goods_by_id';

// mutations
export const ADD_GOODS_TO_PURCHASE = 'add_goods_to_purchase';

export const ASYNC_INIT_LIST = 'async_init_list';

export const REMOVE_ITEM_IN_PHASE = 'remove_item_in_phase';

export const MOVE_TO_NEXT_PHASE = 'move_to_next_phase';

export const FROM_PURCHASE_TO_WAITING = 'from_purchase_to_watting';

export const FROM_WAITING_TO_SORT = 'from_waiting_to_sort';

export const FROM_SORT_TO_STOCK = "from_sort_to_stock";

export const SAVE_PURCHASE_LIST = "save_purchase_list";

export const INIT_ASN_LIST = "init_asn_list";

export const UPDATE_FIELD = "update_field";

export const UPDATE_PRUCHASE_QTY = 'update_pruchase_qty';

export const UPDATE_ACTUAL_QTY= 'update_actual_qty';

export const ADD_ASN_ORDER = "add_order_url";

export const UPDATE_ASN_LIST = "update_asn_list";

export const DELETE_ASN_OBJ = 'DELETE_ASN_OBJ';

// actions

export const ACTION_MOVE_TO_NEXT_PHASE = 'action_move_to_next_phase';

export const ACTION_ADD_GOODS_TO_PURCHASE = "action_add_goods_to_purchase";

export const ACTION_SAVE_PURCHASE_LIST = "action_save_purchase_list";

export const ACTION_SAVE_PRESORT_LIST = "action_save_presort_list";

export const ACTION_ASYNC_GET_ANS_LIST = "action_async_get_ans_list";

export const ACTION_ADD_ANS_ORDER = "action_add_ans_order"

export const ACTION_UPDATE_ASN_DETAILS = "action_update_asn_details";

export const ACTION_UPDATE_ASN_LIST = "action_update_asn_list";

export const ACTION_ADD_ASN_DETAILS = "action_update_asn_details";

export const ACTION_RETRIEVE_ASN_OBJ = 'action_retrieve_asn_obj';

export const ACTION_DELETE_ASN_OBJ = 'action_delete_asn_obj';

