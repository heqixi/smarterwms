import BaseService from 'boot/baseservice';

const prepath = 'order/record';

class OrderRecordService extends BaseService {
  getBatchList (type) {
    return this.getPromise('GET', prepath, { type: type });
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }
}

const orderRecordService = new OrderRecordService();
export default orderRecordService;