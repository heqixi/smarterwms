import { Notify } from 'quasar'
import BaseService from 'boot/baseservice'

const prepath = 'store/product';

class ProductService extends BaseService {
  sycnProduct (params) {
    if (params.shop_id) {
      return this.getPromise('POST', prepath + '/sync', params);
    } else {
      Notify.create({
        message: 'Missing shopId',
        icon: 'close',
        color: 'negative'
      });
      // eslint-disable-next-line no-throw-literal
      throw 'Missing itemId or shopId';
    }
  }

  getProductPages (shopId, search) {
    if (shopId) {
      const url = prepath + '?ordering=-update_time&shop_id=' + shopId;
      return this.getPromise('GET', url, search);
    } else {
      Notify.create({
        message: 'Missing shopId',
        icon: 'close',
        color: 'negative'
      });
      // eslint-disable-next-line no-throw-literal
      throw 'Missing itemId or shopId';
    }
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }

  getProductByStatus (params) {
    return this.getPromise('GET', prepath + '/status', params);
  }
}
const productService = new ProductService();
export default productService;
