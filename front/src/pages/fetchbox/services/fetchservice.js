import BaseService from 'boot/baseservice'

const prepath = 'store'

const fetchBoxPrePath = 'fetch'

class FetchService extends BaseService {
  getFetchMedias (fetchId) {
    return this.getPromise('GET', fetchBoxPrePath + '/medias', { fetch_id: fetchId });
  }

  deleteArea (id) {
    return this.getPromise('DELETE', prepath + '/area', { id: id });
  }

  saveArea (params) {
    return this.getPromise('POST', prepath + '/area', params);
  }

  getAreaList (params) {
    return this.getPromise('GET', prepath + '/area', params);
  }

  receiveProduct (ids) {
    return this.getPromise('POST', fetchBoxPrePath + '/receive', { fetch_list: ids});
  }

  getFetchList (params) {
    return this.getPromise('GET', fetchBoxPrePath, params);
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }

  getOrderDetails (orderId) {
    return this.getPromise('GET', prepath + '/details', { order_id: orderId });
  }
}

const fetchService = new FetchService();
export default fetchService;
