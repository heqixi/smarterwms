import { Notify } from 'quasar'
import BaseService from 'boot/baseservice'

const prepath = 'order';

export const MODIFY_REISSUE = 1;
export const MODIFY_REPLACE = 2;
class OrderService extends BaseService {
  togglePackage (uid, type) {
    if (uid && type) {
      return this.getPromise('POST', prepath + '/package/toggle', {
        uid: uid,
        order_package_type: type
      });
    } else {
      this.throwError('Missing params');
    }
  }

  cancelPackage (uid, type) {
    if (uid && type) {
      return this.getPromise('POST', prepath + '/package/cancel', {
        uid: uid,
        order_package_type: type
      });
    } else {
      this.throwError('Missing params');
    }
  }

  orderRemark (orderId, note) {
    if (orderId && note !== undefined && note !== null) {
      return this.getPromise('POST', prepath + '/remark', {
        order_id: orderId,
        note: note
      });
    } else {
      this.throwError('Missing params');
    }
  }

  stockMatching (params) {
    return this.getPromise('POST', prepath + '/stock_matching', params);
  }

  modelStockMatching (params) {
    return this.getPromise('POST', prepath + '/modify/model_stock_matching', params);
  }

  freedModelStock (params) {
    return this.getPromise('POST', prepath + '/modify/freed_model_stock', params);
  }

  freedStock (orderIdList) {
    return this.getPromise('POST', prepath + '/modify/freed_stock', { order_id_list: orderIdList });
  }

  changeGoods (detailId, goodsList) {
    if ((!goodsList || goodsList.length === 0) && detailId) {
      this.throwError('params error');
    }
    if (goodsList.length > 1) {
      this.throwError('货物只能替换一个');
    }
    return this.getPromise('POST', prepath + '/modify/change_goods', {
      detail_id: detailId,
      goods_id: goodsList[0].id,
      goods_name: goodsList[0].goods_name,
      goods_code: goodsList[0].goods_code
    });
  }

  partiallyShipment (orderIdList) {
    if (!orderIdList || orderIdList.length === 0) {
      this.throwError('order list must > 0');
    }
    return this.getPromise('POST', prepath + '/partially_shipment', { order_id_list: orderIdList });
  }

  forcedShipment (orderIdList) {
    if (!orderIdList || orderIdList.length === 0) {
      this.throwError('order list must > 0');
    }
    return this.getPromise('POST', prepath + '/forced_shipment', { order_id_list: orderIdList });
  }

  shipment (orderIdList) {
    if (!orderIdList || orderIdList.length === 0) {
      this.throwError('order list must > 0');
    }
    return this.getPromise('POST', prepath + '/shipment', { order_id_list: orderIdList });
  }

  syncShipmentOrder (params) {
    return this.getPromise('POST', prepath + '/sync/shipment', params);
  }

  syncOrder (params) {
    return this.getPromise('POST', prepath + '/sync', params);
  }

  // 订单修改
  deleteOrderModify (modifyId) {
    if (modifyId) {
      return this.getPromise('POST', prepath + '/modify/delete', { modifyId: modifyId });
    } else {
      Notify.create({
        message: 'Missing params modifyId',
        icon: 'close',
        color: 'negative'
      });
      // eslint-disable-next-line no-throw-literal
      throw 'Missing params modifyId';
    }
  }

  orderModify (params) {
    if (
      (!params || !params.orderId || !params.modifyType || !params.modelList || params.modelList.length <= 0) ||
      (params.modifyType === MODIFY_REPLACE && !params.replacedSku)
    ) {
      Notify.create({
        message: 'Missing params',
        icon: 'close',
        color: 'negative'
      });
      // eslint-disable-next-line no-throw-literal
      throw 'Missing params';
    }
    return this.getPromise('POST', prepath + '/modify', params);
  }

  getLogisticsFileUrl (orderList, openid) {
    return window.g.BaseUrl + '/' + prepath + '/get_order_logistics_file' +
      '?openid=' + openid + '&order_sn_list=' + orderList.join(',');
  }

  applyLogistics (params) {
    if (params.snList && params.snList.length > 0) {
      return this.getPromise('POST', prepath + '/apply_logistics', {
        shop_id: params.shopId,
        store_id: params.storeId,
        order_sn_list: params.snList
      });
    } else {
      this.throwError('Order List must > 0');
    }
  }

  getStatusList (that) {
    const statusArr = ['ready_to_ship', 'processed', 'shipped', 'to_confirm_receive', 'to_return', 'completed', 'unpaid', 'cancelled'];
    var statusList = [];
    statusList.push({
      label: that.$t('all'),
      value: ''
    });
    for (const i in statusArr) {
      const key = statusArr[i];
      statusList.push({
        label: that.$t('order.status.' + key),
        value: key.toUpperCase()
      });
    }
    return statusList;
  }

  getOrderList (params) {
    return this.getPromise('GET', prepath, params);
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }

  getOrderDetails (orderId) {
    return this.getPromise('GET', prepath + '/details', { order_id: orderId });
  }
}

const orderService = new OrderService();
export default orderService;
