<template>
  <q-dialog ref="dialog">
    <CommonTable
      :table_list="table_list"
      :rowKey="rowKey"
      :topButtons="topButtons"
      :columns="columns"
      :numRows="numRows"
      :loading="loading"
      :table-style="{width:'1000px', maxWidth:'1200px'}"
    />
  </q-dialog>
</template>

<script>

import CommonTable from 'components/Share/commontable'
import GoodsSearch from 'pages/order/components/goodssearch'
import { stockStatus2Str } from 'src/store/stock/types'
import { putauth } from 'boot/axios_request'

const GLOBAL_PRODUCT = '全球商品'

const GOODS_STOCK = '商品库存'

export default {
  name: 'GoodsDeleteDialog',
  data () {
    var _this = this
    return {
      rowKey: 'entity_code',
      numRows: 2,
      loading: false,
      table_list: [],
      topButtons: [
        {
          name: 'replace',
          label: '替换',
          tip: '批量关联实体',
          click: (selectEntites) => {
            _this.searchGoodsPopup(selectEntites)
          }
        }
      ],
      columns: [
        {
          name: 'entity_type',
          required: true,
          label: '实体类型',
          align: 'center',
          type: 'text',
          field: 'entity_type',
          style: 'width:100px'
        },
        {
          name: 'entity_code',
          required: true,
          label: '实体编码',
          align: 'center',
          type: 'text',
          field: 'entity_code',
          style: 'width:150px'
        },
        {
          name: 'entity_image',
          required: true,
          label: '图片',
          align: 'center',
          type: 'image',
          field: 'entity_image',
          style: 'width:100px'
        },
        {
          name: 'entity_num',
          label: '数量',
          field: 'entity_num',
          align: 'center',
          type: 'number',
          style: 'width:100px'
        },
        {
          name: 'entity_desc',
          label: '描述',
          align: 'center',
          type: 'text',
          field: 'entity_desc',
          style: 'width:100px'
        }
      ]
    }
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    searchGoodsPopup (entitys) {
      this.$q.dialog({
        component: GoodsSearch
      }).onOk((selectGoods) => {
        this.replaceGoodsOfEntity(selectGoods, entitys)
      })
    },
    replaceGoodsOfEntity (selectGoods, entitys) {
      var _this = this
      if (selectGoods.length <= 0) {
        _this.$q.notify({
          message: '请选择产品',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      if (selectGoods.length > 1) {
        _this.$q.notify({
          message: '只能选择一个产品',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const formData = {
        merge_to: selectGoods[0].id,
        merge: true
      }
      console.log('replace goods of entities ', formData)
      _this.loading = true
      putauth('goods/' + _this.data.goods.id + '/', formData).then(res => {
        _this.loading = false
        console.log('update goods success ', res)
      }).catch(err => {
        _this.loading = false
        console.log('update goods fail ', err)
      })
    }
  },
  created () {
    console.log('create ', this.data)
    if (this.data) {
      const globalProducts = this.data.global_products
      if (globalProducts) {
        const globalProductEntities = []
        globalProducts.forEach(product => {
          const existEntity = globalProductEntities.find(entity => {
            return entity.entity_code === product.sku
          })
          if (existEntity) {
            existEntity.entity_num += 1
          } else {
            globalProductEntities.push({
              entity_type: GLOBAL_PRODUCT,
              entity_code: product.sku,
              entity_num: 1,
              entity_image: product.image,
              entity_desc: `状态 ${product.status}`
            })
          }
        })
        this.table_list = this.table_list.concat(globalProductEntities)
      }
      const goodsStocks = this.data.stocks
      if (goodsStocks) {
        const stockEntities = []
        goodsStocks.forEach(stock => {
          const exist = stockEntities.find(entity => {
            return entity.entity_code === stockStatus2Str(stock.stock_status)
          })
          if (exist) {
            exist.entity_num += stock.stock_qty
          } else {
            stockEntities.push({
              entity_type: GOODS_STOCK,
              entity_code: stockStatus2Str(stock.stock_status),
              entity_num: 1,
              entity_image: '',
              entity_desc: ''
            })
          }
        })
        this.table_list = this.table_list.concat(stockEntities)
      }
    }
  },
  components: {
    CommonTable,
    GoodsSearch
  },
  props: ['data']
}
</script>

<style scoped>

</style>
