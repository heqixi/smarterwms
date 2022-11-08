import { putauth } from 'boot/axios_request'
import { Notify } from 'quasar'

class GoodsService {

  updateGoodsCode (goods, mergeDuplicate) {
    if (mergeDuplicate) {
      goods.merge_duplicate = mergeDuplicate
    }
    goods.partial = true
    return new Promise((resolve, reject) => {
      putauth('goods/' + goods.id + '/', goods).then(res => {
        console.log('update goods code success ', res)
        resolve(res)
      }).catch(err => {
        reject(err)
        Notify.create({
          message: '更新货号失败',
          icon: 'close',
          color: 'negative'
        })
      })
    })
  }
}


const goodsService = new GoodsService()

export default goodsService
