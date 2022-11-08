<template>
  <div style="width:1500px;max-width:1500px">
    <q-dialog :ref="refName">
      <q-card style="width:1500px;max-width:1500px">
        <goods-search-dialog
          ref="goods_table"
          :columns="columns"
          :topButtons="topButtons"
          :preSearch="preSearch"
          :path="path"
          :empty-data="emptyData"
          :defaultSelected="defaultSelected"
          :goods="goods"
          multiple-select="true"
        />
      </q-card>
    </q-dialog>
  </div>
</template>

<script>
import GoodsSearchDialog from 'components/Share/goodsSearchTable'
import GoodsSelected from './goodsSelectDialog'
import { postauth } from 'boot/axios_request'

export default {
  name: 'GoodsSearchForSupplier',
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
            _this.$emit('ok', { goods: selectedList, action: 'ok' })
            _this.hide()
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
            maxWidth: '80px',
            width: '80px'
          }
        },
        {
          name: 'goods_code',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          type: 'text',
          field: 'goods_code',
          style: {
            maxWidth: '100px',
            width: '100px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'product',
          required: true,
          label: '在线商品',
          align: 'center',
          type: 'table',
          keepExpand: true,
          field: 'products',
          style: {
            maxWidth: '150px',
            width: '150px',
            whiteSpace: 'normal'
          },
          fieldMap: products => { return products || [] },
          subColumns: [
            {
              name: 'product_sku',
              label: '关联全球商品',
              field: 'sku',
              type: 'text',
              class: 'col-7 text-center'
            },
            {
              name: 'action',
              label: this.$t('action'),
              type: 'actions',
              class: 'col-5 text-center',
              align: 'center',
              actions: [
                {
                  name: 'select_product',
                  label: '选择',
                  tip: '选择产品的全部子SKU',
                  click: (goods, product) => {
                    console.log('set as default purchase plan ', goods, product)
                    _this.selectProductGoods(goods, product)
                  }
                }
              ]
            }
          ]
        },
        {
          name: 'suppliers',
          required: true,
          label: '供应商',
          align: 'center',
          type: 'table',
          field: 'purchases',
          keepExpand: true,
          style: {
            maxWidth: '500px',
            width: '500px',
            whiteSpace: 'normal'
          },
          subColumns: [
            {
              name: 'supplier_name',
              label: '供应商名称',
              field: 'supplier',
              type: 'text',
              class: 'col-3 text-center',
              fieldMap: supplier => { return supplier.supplier_name }
            },
            {
              name: 'tag',
              label: '标签',
              field: 'tag',
              type: 'text',
              class: 'col-3 text-center'
            },
            {
              name: 'price',
              label: '价格',
              field: 'price',
              type: 'number',
              class: 'col-2 text-center'
            },
            {
              name: 'url',
              label: '链接',
              field: 'url',
              type: 'url',
              class: 'col-1 text-center'
            },
            {
              name: 'action',
              label: this.$t('action'),
              type: 'actions',
              class: 'col-3 text-center',
              align: 'center',
              actions: [
                {
                  name: 'set_default',
                  label: '设为默认',
                  tip: '设为默认',
                  click: (goods, purchasePlan) => {
                    console.log('set as default purchase plan ', goods, purchasePlan)
                    if (purchasePlan.level === 0) {
                      this.$q.notify({
                        message: '已经是默认采购链接',
                        icon: 'check',
                        color: 'green'
                      })
                      return
                    }
                    postauth('supplier/purchase/set_default', {
                      goods: goods.id,
                      purchase: purchasePlan.id
                    }).then(res => {
                      for (let i = 0; i < goods.purchases.length; i++) {
                        if (goods.purchases[i].id === purchasePlan.id) {
                          const defaultPurchase = goods.purchases.splice(i, 1)[0]
                          goods.purchases.unshift(defaultPurchase)
                          break
                        }
                      }
                    })
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  },
  methods: {
    addSelectGoods (goodsList, product) {
      const allLoadGoods = this.$refs.goods_table.getAllLoadGoods()
      goodsList.forEach(goods => {
        const exist = allLoadGoods.find(existGoods => { return existGoods.id === goods.id })
        if (!exist) {
          goods.products = [product]
          goods.purchases = []
          this.$refs.goods_table.prependGoods(goods)
        }
      })
      this.$refs.goods_table.addSelect(goodsList)
    },
    clearSelect () {
      this.$refs.goods_table.clearSelect()
    },
    show () {
      this.$refs[this.refName].show()
    },
    hide () {
      this.$refs[this.refName].hide()
    },
    selectProductGoods (goods, product) {
      var _this = this
      _this.$q.dialog({
        component: GoodsSelected,
        goods: product.goods
      }).onOk((selectGoods) => {
        if (!selectGoods.find(goodsSelected => { return goodsSelected.id === goods.id })) {
          selectGoods.push(goods)
        }
        console.log('emit goods, to select purchase ', selectGoods)
        _this.$emit('ok', { goods: selectGoods, action: 'addPurchase' })
      })
    }
  },
  created () {
    var _this = this
    if (this.additionalTopButtons) {
      this.additionalTopButtons.forEach(button => {
        _this.topButtons.push(button)
      })
    }
  },
  props: {
    sku: String,
    preSearch: String,
    path: String,
    additionalTopButtons: Array,
    emptyData: Boolean,
    refName: String,
    defaultSelected: Array,
    goods: Array
  }
}
</script>

<style scoped>

</style>
