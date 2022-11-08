<template>
  <q-dialog full-height ref="dialog">
    <CommonTable
      :table_list="products"
      :rowKey="rowKey"
      :topButtons="topButtons"
      :columns="columns"
      :numRows="numRows"
      :loading="loading"
      :table-style="tabeStyle ? tabeStyle : {width:'1200px', maxWidth:'1500px'}"
    />
  </q-dialog>
</template>

<script>

import CommonTable from 'components/Share/commontable'
import { getauth } from 'boot/axios_request'
import NewFormDialog from 'components/Share/newFormDialog'
import profitService from 'pages/fetchbox/services/profitservice'
import ProfitCalculatorDialog from 'src/pages/fetchbox/components/profitcalculatordialog'

export default {
  name: 'GoodsEditPriceDialog',
  data () {
    var _this = this
    return {
      numRows: 1,
      loading: false,
      selectedFormData: {
        discount: undefined
      },
      topButtons: [
        {
          name: 'batchUpdate',
          label: '批量修改',
          tip: '批量修改选择的商品价格',
          click: (productSelected) => {
            _this.editDiscountBatch(productSelected)
          }
        },
        {
          name: 'updateConform',
          label: '确认',
          tip: '修改选择的商品价格',
          click: () => {
            _this.$emit('ok', _this.products)
            _this.hide()
            // _this.updateDiscount(_this.products)
          }
        }
      ],
      columns: [
        {
          name: 'product_image',
          required: true,
          label: '图片',
          align: 'center',
          type: 'image',
          field: 'image',
          style: {
            width: '50px',
            height: '50px'
          }
        },
        {
          name: 'product_sku',
          required: true,
          label: 'SKU',
          align: 'center',
          type: 'text',
          field: 'sku',
          style: {
            width: '80px',
            maxWidth: '100px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'store_info',
          required: true,
          label: '店铺信息',
          align: 'center',
          type: 'text',
          field: 'self',
          style: {
            width: '100px',
            whiteSpace: 'normal'
          },
          fieldMap: priceInfo => {
            return priceInfo.type + '-' + priceInfo.area + '-' + priceInfo.store_name
          }
        },
        {
          name: 'variants_price_info',
          label: '变体价格信息',
          type: 'table',
          height: '200px',
          field: 'models',
          rowKey: 'model_id',
          align: 'center',
          rowHeight: 55,
          style: { width: '400px' },
          keepExpand: true,
          subColumns: [
            {
              name: 'variant_image',
              required: true,
              label: '变体图片',
              align: 'center',
              type: 'image',
              field: 'image',
              class: 'col-2'
            },
            {
              name: 'variant_sku',
              required: true,
              label: 'SKU',
              align: 'center',
              type: 'text',
              field: 'sku',
              class: 'col-3'
            },
            {
              name: 'original_price',
              required: true,
              label: '折前价',
              align: 'center',
              type: 'number',
              field: 'original_price',
              edit: _this.editOriginalPrice === true,
              class: 'col-2',
              onUpdate: (priceInfo, editModel, newPrice) => {
                console.log('on update origin price ', newPrice)
                const newPriceNumber = parseFloat(newPrice)
                return new Promise((resolve, reject) => {
                  if (isNaN(newPriceNumber)) {
                    _this.$q.notify({
                      message: '无效价格',
                      icon: 'close',
                      color: 'negative'
                    })
                  } else if (newPriceNumber <= 0 || newPriceNumber < editModel.current_price) {
                    _this.$q.notify({
                      message: '原价不能低于售价',
                      icon: 'close',
                      color: 'negative'
                    })
                    reject('')
                  } else {
                    editModel.original_price = newPriceNumber
                    resolve(newPriceNumber)
                    console.log('after update  origin price ', editModel)
                  }
                })
              }
            },
            {
              name: 'discount',
              required: true,
              label: '折扣',
              align: 'center',
              type: 'text',
              field: 'discount_percentage',
              edit: true,
              class: 'col-1',
              fieldMap: discountPercent => {
                return discountPercent * 100 + '%'
              }
            },
            {
              name: 'current_price',
              required: true,
              label: '当前售价',
              align: 'center',
              type: 'text',
              field: 'current_price',
              class: 'col-2',
              edit: true,
              onUpdate: (priceInfo, editModel, newPrice) => {
                const newPriceNumber = parseFloat(newPrice)
                if (isNaN(newPriceNumber)) {
                  _this.$q.notify({
                    message: '无效价格',
                    icon: 'close',
                    color: 'negative'
                  })
                  return
                }
                if (priceInfo.discount === undefined
                  || priceInfo.discount.discount_id === undefined
                  || priceInfo.discount.discount_id <= 0) {
                  return _this.getDiscountListAndUpdate(priceInfo).then(res => {
                    return _this.editModelPrice(priceInfo, editModel, newPriceNumber)
                  })
                } else {
                  return _this.editModelPrice(priceInfo, editModel, newPriceNumber)
                }
              }
            },
            {
              name: 'profit',
              required: true,
              label: '利润',
              align: 'center',
              type: 'text',
              field: 'profit',
              class: 'col-2'
            }
          ]
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
    editDiscountBatch (selectPriceInfo) {
      var _this = this
      if (selectPriceInfo.length <= 0) {
        _this.$q.notify({
          message: '至少选择一组商品',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const profitSettings = _this.getProfitSettings(selectPriceInfo[0])
      console.log('editDiscountBatch selectPriceInfo ', selectPriceInfo[0])
      _this.$q.dialog({
        component: ProfitCalculatorDialog,
        data: profitSettings,
        store: selectPriceInfo[0].store.uid
      }).onOk((priceAndProfit) => {
        console.log('on ok priceAndProfit ', priceAndProfit)
        const currentPrice = parseFloat(priceAndProfit.price)
        if (currentPrice < 0) {
          _this.$q.notify({
            message: '无效价格',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        selectPriceInfo.forEach(priceInfo => {
          if (priceInfo.discount === undefined
            || priceInfo.discount.discount_id === undefined
            || priceInfo.discount.discount_id <= 0) {
            _this.getDiscountListAndUpdate(priceInfo).then(res => {
              console.log('discount choise , now update price ', priceInfo)
              priceInfo.models.forEach(model => {
                if (_this.editOriginalPrice && model.discount_percentage < 1) {
                  _this.$set(model, 'original_price', (currentPrice / (1 - model.discount_percentage)).toFixed(0))
                }
                _this.editModelPrice(priceInfo, model, currentPrice)
                model.current_price = currentPrice
              })
            })
          } else {
            priceInfo.models.forEach(model => {
              if (_this.editOriginalPrice && model.discount_percentage < 1) {
                _this.$set(model, 'original_price', (currentPrice / (1 - model.discount_percentage)).toFixed(0))
              }
              _this.editModelPrice(priceInfo, model, currentPrice)
              model.current_price = currentPrice
            })
          }
        })
      })
    },
    getProfitSettings (productInfo) {
      const setting = {
        logistics_costs: 0,
        price: 0,
        weight: 0
      }
      if (productInfo.supplier) {
        setting.logistics_costs = productInfo.supplier.logistics_costs
      }
      if (productInfo.logistic) {
        setting.weight = productInfo.logistic.weight
      }
      productInfo.models.forEach(model => {
        if (model.stock && model.stock.price > setting.price) {
          setting.price = model.stock.price
        }
      })
      return setting
    },
    editModelPrice (priceInfo, editModel, newPrice) {
      var _this = this
      if (newPrice >= editModel.original_price) {
        this.$q.notify({
          message: '不能高于原价',
          icon: 'close',
          color: 'negative'
        })
        return new Promise((resolve, reject) => {
          resolve(editModel.current_price)
        })
      }
      return new Promise((resolve, reject) => {
        const discountId = editModel.discount_id
        if (discountId > 0) { // 表示有折扣
          priceInfo.discount.item_list[0].model_list.forEach(model => {
            if (model.model_id === editModel.model_id) {
              model.model_promotion_price = newPrice
              model.update = true
              editModel.current_price = newPrice
            }
          })
        } else {
          priceInfo.discount.item_list[0].model_list.push({
            model_id: editModel.model_id,
            model_original_price: editModel.original_price,
            model_promotion_price: newPrice,
            add: true
          })
          editModel.current_price = newPrice
        }
        resolve(newPrice)
        _this.updateModelProfit(priceInfo, editModel)
      })
    },
    getDiscountListAndUpdate (priceInfo) {
      var _this = this
      return new Promise((resolve, reject) => {
        _this.loading = true
        getauth('/store/discounts/?store_id=' + priceInfo.store_id, {}).then(discountList => {
          this.loading = false
          console.log('get store discount ', discountList)
          const formItems = [
            {
              name: 'discount',
              label: '选择折扣活动',
              type: 'select',
              field: 'discount',
              options: discountList,
              optionLabel: discount => {
                return discount.discount_name
              }
            }
          ]
          _this.$q.dialog({
            component: NewFormDialog,
            title: '请选择一个折扣分组',
            newFormData: _this.selectedFormData,
            newFormItems: formItems
          }).onOk(() => {
            console.log('on discount chose ', _this.selectedFormData)
            priceInfo.discount = {
              discount_id: _this.selectedFormData.discount.discount_id,
              discount_name: _this.selectedFormData.discount.discount_name,
              add: true,
              item_list: [
                {
                  item_id: priceInfo.item_id,
                  purchase_limit: 0, // 默认无购买限制
                  model_list: [
                    // {
                    //   model_id: editModel.model_id,
                    //   model_original_price: editModel.original_price,
                    //   model_promotion_price: newPrice,
                    //   add: true
                    // }
                  ]
                }
              ]
            }
            resolve(priceInfo.discount)
          })
        })
      })
    },
    updateModelProfit (product, model) {
      var _this = this
      if (product.store.profit_setting && product.supplier && product.logistic) {
        const calculate = JSON.parse(JSON.stringify(product.store.profit_setting))
        const profit = profitService.getNetProfit(calculate, model.current_price, 1,
          product.logistic.weight, model.stock.price, product.supplier.logistics_costs).toFixed(2)
        _this.$set(model, 'profit', profit)
      } else {
        _this.$set(model, 'profit', '--')
      }
    }
  },
  created () {
    console.log('create ', this.products)
    var _this = this
    this.products.forEach(product => {
      if (product.store.profit_setting && product.supplier && product.logistic) {
        const calculate = JSON.parse(JSON.stringify(product.store.profit_setting))
        product.models.forEach(model => {
          const profit = profitService.getNetProfit(calculate, model.current_price, 1,
            product.logistic.weight, model.stock.price, product.supplier.logistics_costs).toFixed(2)
          console.log('calculate model profit ', profit)
          _this.$set(model, 'profit', profit)
        })
      } else {
        product.models.forEach(model => {
          _this.$set(model, 'profit', '请完善商品信息')
        })
      }
      product.models.forEach(model => {
        if (model.current_price > 0 && model.original_price > 0) {
          _this.$set(model, 'discount_percentage', ((model.original_price - model.current_price) / model.original_price).toFixed(2))
        }
        if (product.store.area === 'VN') {
          _this.$set(model, 'discount_percentage', 0.45)
        } else {
          _this.$set(model, 'discount_percentage', 0.6)
        }
      })
    })
  },
  components: {
    CommonTable
  },
  props: ['products', 'rowKey', 'tabeStyle', 'modelKey', 'editOriginalPrice']
}
</script>

<style scoped>

</style>
