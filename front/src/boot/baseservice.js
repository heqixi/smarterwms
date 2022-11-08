import { Loading, Notify } from 'quasar'
import { deleteauth, getauth, postauth } from 'boot/axios_request'

export default class BaseService {
  getPromise (method = '', url = '', params = {}, showLoading = true) {
    const _this = this;
    if (showLoading) {
      Loading.show();
    }
    if (method.toUpperCase() === 'GET') {
      if (params) {
        const keys = Object.keys(params);
        for (let i = 0; i < keys.length; i++) {
          const key = keys[i];
          if (_this.check(params[key])) {
            if (url.indexOf('?') === -1) {
              url += '?' + keys[i] + '=' + encodeURIComponent(params[keys[i]]);
            } else {
              url += '&' + keys[i] + '=' + encodeURIComponent(params[keys[i]]);
            }
          }
        }
      }
      return new Promise((resolve, reject) => {
        getauth(url).then(res => resolve(res), err => {
          _this.error(err);
          reject(err);
        }).finally(() => _this.f(showLoading));
      });
    }
    if (method.toUpperCase() === 'POST') {
      return new Promise((resolve, reject) => {
        postauth(url, params).then(res => resolve(res), err => {
          _this.error(err);
          reject(err);
        }).finally(() => _this.f(showLoading));
      });
    }
    if (method.toUpperCase() === 'DELETE') {
      if (params) {
        const keys = Object.keys(params);
        for (let i = 0; i < keys.length; i++) {
          const key = keys[i];
          if (_this.check(params[key])) {
            if (url.indexOf('?') === -1) {
              url += '?' + keys[i] + '=' + encodeURIComponent(params[keys[i]]);
            } else {
              url += '&' + keys[i] + '=' + encodeURIComponent(params[keys[i]]);
            }
          }
        }
      }
      return new Promise((resolve, reject) => {
        deleteauth(url).then(res => resolve(res), err => {
          _this.error(err);
          reject(err);
        }).finally(() => _this.f(showLoading));
      });
    }
    // eslint-disable-next-line no-throw-literal
    throw 'This request method is not currently supported';
  }

  throwError (err) {
    Notify.create({
      message: err,
      icon: 'close',
      color: 'negative'
    });
    throw new Error(err);
  }

  error (err) {
    Notify.create({
      message: err.detail ? err.detail : err.response.data ? err.response.data : err.message,
      icon: 'close',
      color: 'negative'
    });
  }

  f (showLoading) {
    if (showLoading) {
      Loading.hide();
    }
  }

  check (val) {
    if (val === undefined || val === null) {
      return false;
    }
    if (typeof (val) === 'string' && val.trim() === '') {
      return false;
    }
    return true;
  }
}
