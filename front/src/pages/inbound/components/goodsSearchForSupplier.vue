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
        },
        {
          name: '添加',
          label: '添加产品',
          tip: '添加产品',
          click: selectedGoods => {
            let path = 'goods/?group=true'
            const goodsExcludeParams = _this.$refs.goods_table.getAllLoadGoods().map(g => { return g.id }).join('&exclude=')
            if (goodsExcludeParams) {
              path += `&exclude=${goodsExcludeParams}`
            }
            _this.$q.dialog({
              component: GoodsSelected,
              path: path
            }).onOk((selectGoods) => {
              console.log('add select goods to purchase plan ', selectGoods)
              _this.$emit('ok', { goods: selectGoods })
              const goodsOfPurchased = _this.$refs.goods_table.getAllLoadGoods()
              selectGoods.forEach(goods => {
                if (!goodsOfPurchased.find(g => g.id === goods.id)) {
                  _this.$refs.goods_table.prependGoods(goods)
                }
              })
            })
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
          name: 'group',
          required: true,
          label: '在线商品',
          align: 'center',
          type: 'table',
          keepExpand: true,
          field: 'group',
          style: {
            maxWidth: '150px',
            width: '150px',
            whiteSpace: 'normal'
          },
          fieldMap: products => { return products || [] },
          subColumns: [
            {
              name: 'group_name',
              label: '分组名称',
              field: 'name',
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
                  tip: '选择同一分组的其他货物',
                  click: (goods, group) => {
                    console.log('select goods in same group ', goods, group)
                    _this.selectGroupGoods(goods, group)
                  }
                }
              ]
            }
          ]
        }
        // {
        //   name: 'suppliers',
        //   required: true,
        //   label: '供应商',
        //   align: 'center',
        //   type: 'table',
        //   field: 'purchases',
        //   keepExpand: true,
        //   style: {
        //     maxWidth: '500px',
        //     width: '500px',
        //     whiteSpace: 'normal'
        //   },
        //   subColumns: [
        //     {
        //       name: 'supplier_name',
        //       label: '供应商名称',
        //       field: 'supplier',
        //       type: 'text',
        //       class: 'col-3 text-center',
        //       fieldMap: supplier => { return supplier.supplier_name }
        //     },
        //     {
        //       name: 'tag',
        //       label: '标签',
        //       field: 'tag',
        //       type: 'text',
        //       class: 'col-3 text-center'
        //     },
        //     {
        //       name: 'price',
        //       label: '价格',
        //       field: 'price',
        //       type: 'number',
        //       class: 'col-2 text-center'
        //     },
        //     {
        //       name: 'url',
        //       label: '链接',
        //       field: 'url',
        //       type: 'url',
        //       class: 'col-1 text-center'
        //     },
        //     {
        //       name: 'action',
        //       label: this.$t('action'),
        //       type: 'actions',
        //       class: 'col-3 text-center',
        //       align: 'center',
        //       actions: [
        //         {
        //           name: 'set_default',
        //           label: '设为默认',
        //           tip: '设为默认',
        //           click: (goods, purchasePlan) => {
        //             console.log('set as default purchase plan ', goods, purchasePlan)
        //             if (purchasePlan.level === 0) {
        //               this.$q.notify({
        //                 message: '已经是默认采购链接',
        //                 icon: 'check',
        //                 color: 'green'
        //               })
        //               return
        //             }
        //             postauth('supplier/purchase/set_default', {
        //               goods: goods.id,
        //               purchase: purchasePlan.id
        //             }).then(res => {
        //               for (let i = 0; i < goods.purchases.length; i++) {
        //                 if (goods.purchases[i].id === purchasePlan.id) {
        //                   const defaultPurchase = goods.purchases.splice(i, 1)[0]
        //                   goods.purchases.unshift(defaultPurchase)
        //                   break
        //                 }
        //               }
        //             })
        //           }
        //         }
        //       ]
        //     }
        //   ]
        // }
      ]
    }
  },
  methods: {
    clearSelect () {
      this.$refs.goods_table.clearSelect()
    },
    show () {
      this.$refs[this.refName].show()
    },
    hide () {
      this.$refs[this.refName].hide()
    },
    selectGroupGoods (goods, group) {
      var _this = this
      _this.$q.dialog({
        component: GoodsSelected,
        goods: group.goods
      }).onOk((selectGoods) => {
        if (!selectGoods.find(goodsSelected => { return goodsSelected.id === goods.id })) {
          selectGoods.push(goods)
        }
        console.log('emit select goods of same group', selectGoods)
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
