<template>
  <q-dialog ref="dialog" full-width>
    <q-card class="full-width">
      <goods-search-dialog
        :columns="columns"
        :topButtons="topButtons"
        :preSearch="preSearch"
      />
    </q-card>
  </q-dialog>
</template>
<script>
import GoodsSearchDialog from 'src/components/Share/goodsSearchTable'
import goodsService from 'src/pages/goods/services/goodsService'
import { STOCK_STATUS } from 'src/store/stock/types'
import { postauth } from 'boot/axios_request'

export default {
  name: 'GoodsSearch',
  components: { GoodsSearchDialog },
  data () {
    const _this = this
    return {
      topButtons: [
        {
          name: 'confirm',
          label: `${this.$t('submit')}`,
          tip: `${this.$t('submit')}`,
          click: selectedList => {
            console.log('selectedList, ', selectedList.length)
            _this.$emit('ok', selectedList)
            _this.hide()
          }
        },
        {
          name: 'cancel',
          label: '取消',
          tip: '下次再选',
          click: selectedList => {
            console.log('cancel selectedList, ', selectedList.length)
            _this.$refs.dialog.hide()
          }
        }
      ],
      columns: [
        {
          name: 'goods_image',
          required: true,
          label: '图片',
          align: 'center',
          type: 'image',
          field: 'goods_image',
          style: {
            maxWidth: '150px',
            width: '150px'
          }
        }, {
          name: 'stock_onhand',
          label: '现有库存',
          field: 'stocks',
          align: 'center',
          type: 'number',
          sortable: true,
          edit: true,
          style: {
            maxWidth: '100px',
            width: '100px'
          },
          fieldMap: stocks => {
            return stocks.stock_onhand
          },
          onUpdate: _this.updateStockOnHand,
          setter: (stocks, newStock) => {
            stocks.stock_onhand = newStock
          }
        },
        {
          name: 'goods_code',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          type: 'text',
          field: 'goods_code',
          edit: true,
          style: {
            maxWidth: '200px',
            width: '200px',
            whiteSpace: 'normal'
          },
          onUpdate (goods, newVal) {
            return new Promise((resolve, reject) => {
              goods.goods_code = newVal
              goodsService.updateGoodsCode(goods, true).then(goodsUpdated => {
                if (goods.id !== goodsUpdated.id) {
                  goods.id = goodsUpdated.id
                }
                resolve(newVal)
              })
            })
          }
        },
        {
          name: 'goods_name',
          required: true,
          label: this.$t('goods.view_goodslist.goods_name'),
          align: 'center',
          type: 'longText',
          field: 'goods_name',
          class: 'goods_name',
          style: {
            maxWidth: '300px',
            width: '300px',
            whiteSpace: 'normal'
          }
        }
      ]
    }
  },
  props: {
    sku: String,
    preSearch: String
  },
  emits: [
    // REQUIRED
    'ok',
    'cancel',
    'update'
  ],
  methods: {
    submit (data) {
      this.$emit('ok', data)
      this.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    updateStockOnHand (goods, num) {
      var _this = this
      console.log('updateStockOnHand from goods searcg', goods, num)
      const stockObj = {
        creater: _this.login_name,
        openid: _this.openid,
        goods: goods.id,
        stock_status: STOCK_STATUS.on_hand,
        stock_qty: num
      }
      return new Promise((resolve, reject) => {
        postauth('stock/list/', stockObj).then(stockSaved => {
          console.log('create / update stock obj success ', stockSaved)
          goods.stocks.stock_onhand = num
          resolve(num)
        })
      })
    },
  }
}
</script>
