import { Notify } from 'quasar'
import BaseService from 'boot/baseservice'

const prepath = 'store/global';

class GlobalProductService extends BaseService {
  updateGlobalSku (merchantId, globalList = []) {
    if (merchantId && globalList && globalList.length > 0) {
      return this.getPromise('POST', prepath + '/update/global_sku', {
        merchant_id: merchantId,
        global_product_list: globalList
      });
    } else {
      this.throwError('Missing merchant id and modelList must be > 0');
    }
  }

  getGlobalBrands (merchantId, categoryId, language) {
    if (merchantId && categoryId) {
      return this.getPromise('GET', prepath + '/brands', {
        merchant_id: merchantId,
        category_id: categoryId,
        language: language
      });
    } else {
      this.throwError('Missing merchant id or global product id');
    }
  }

  getGlobalAttributeList (merchantId, categoryId, language) {
    if (merchantId && categoryId) {
      return this.getPromise('GET', prepath + '/attributes', {
        merchant_id: merchantId,
        category_id: categoryId,
        language: language
      });
    } else {
      this.throwError('Missing merchant id or global product id');
    }
  }

  getGlobalProductInfo (merchantId, globalProductId) {
    if (merchantId && globalProductId) {
      return this.getPromise('GET', prepath + '/details', {
        merchant_id: merchantId,
        global_product_id: globalProductId
      });
    } else {
      this.throwError('Missing merchant id or global product id');
    }
  }

  sycnGlobalProduct (params) {
    if (params.merchant_id) {
      return this.getPromise('POST', prepath + '/sync', params);
    } else {
      this.throwError('Missing merchant_id');
    }
  }

  getGlobalProductList (merchantId, search = {}) {
    if (merchantId) {
      return this.getPromise('GET', prepath + '?merchant_id=' + merchantId, search);
    } else {
      this.throwError('Missing merchant_id');
    }
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }
}

const globalProductService = new GlobalProductService();
export default globalProductService;
