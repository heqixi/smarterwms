import BaseService from 'boot/baseservice'

const prepath = 'store/package';

class ProductPackageService extends BaseService {
  removePackage (id) {
    return this.getPromise('DELETE', prepath + '/remove', { package_id: id });
  }

  newPackage (params) {
    return this.getPromise('POST', prepath + '/new', params);
  }

  getPackageList (params) {
    return this.getPromise('GET', prepath, params);
  }

  getListPrevOrNext (url) {
    return this.getPromise('GET', url);
  }
}

const productPackageService = new ProductPackageService();
export default productPackageService;