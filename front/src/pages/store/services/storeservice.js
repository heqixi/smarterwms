import { Notify } from 'quasar'
import BaseService from 'boot/baseservice'

const prepath = 'store';
class StoreService extends BaseService {
  refreshToken (storeId) {
    return this.getPromise('POST', prepath + '/refresh_token/', { storeId: storeId });
  }

  getShopeeAuthUrl (auth) {
    // eslint-disable-next-line no-unused-vars
    let url = prepath + '/auth';
    if (auth.storeId) {
      url += '?storeId=' + auth.storeId
    } else if (auth.partnerId && auth.partnerKey) {
      url += '?partnerId=' + auth.partnerId + '&partnerKey=' + auth.partnerKey
    } else {
      Notify.create({
        message: 'Missing auth params',
        icon: 'close',
        color: 'negative'
      });
      // eslint-disable-next-line no-throw-literal
      throw 'Missing auth params';
    }
    return this.getPromise('GET', url).then(res => {
      if (res.url) {
        return res.url;
      } else {
        Notify.create({
          message: 'Error Url',
          icon: 'close',
          color: 'negative'
        });
        // eslint-disable-next-line no-throw-literal
        throw 'Error Url';
      }
    });
  }

  deleteStore (storeId) {
    return this.getPromise('DELETE', prepath + '/' + storeId + '/');
  }

  getStorePages () {
    return this.getPromise('GET', prepath + '/?ordering=-update_time');
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }

  getStoreList (type) {
    return this.getPromise('GET', prepath + '/all/', { type: type || 2 });
  }
}
const storeService = new StoreService();
export default storeService;
