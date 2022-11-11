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
          field: 'image_url',
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
          field: 'product_sku',
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
          field: 'store',
          style: {
            width: '100px',
            whiteSpace: 'normal'
          },
          fieldMap: store => {
            return store.area + '-' + store.name
          }
        },
        {
          name: 'variants_price_info',
          label: '变体价格信息',
          type: 'table',
          height: '200px',
          field: 'variants',
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
              field: 'image_url',
              class: 'col-2'
            },
            {
              name: 'variant_sku',
              required: true,
              label: 'SKU',
              align: 'center',
              type: 'text',
              field: 'model_sku',
              class: 'col-3'
            },
            {
              name: 'original_price',
              required: true,
              label: '折前价',
              align: 'center',
              type: 'number',
              field: 'price_info',
              fieldMap: priceInfo => { return priceInfo.original_price },
              edit: _this.editOriginalPrice === true,
              class: 'col-2',
              onUpdate: (shopProduct, editModel, newPrice) => {
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
                    editModel.price_info.global_price = newPriceNumber
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
              field: 'price_info',
              fieldMap: priceInfo => { return priceInfo.current_price },
              class: 'col-2',
              edit: true,
              onUpdate: (shopProduct, editModel, newPrice) => {
                const newPriceNumber = parseFloat(newPrice)
                if (isNaN(newPriceNumber)) {
                  _this.$q.notify({
                    message: '无效价格',
                    icon: 'close',
                    color: 'negative'
                  })
                  return
                }
                if (!shopProduct.promotion_id) {
                  return _this.getDiscountListAndUpdate(shopProduct).then(res => {
                    return _this.editVariantPrice(shopProduct, editModel, newPriceNumber)
                  })
                } else {
                  return _this.editVariantPrice(shopProduct, editModel, newPriceNumber)
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
    editDiscountBatch (selectProducts) {
      var _this = this
      if (selectProducts.length <= 0) {
        _this.$q.notify({
          message: '至少选择一组商品',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const profitSettings = _this.getProfitSettings(selectProducts[0])
      console.log('editDiscountBatch selectPriceInfo ', selectProducts[0])
      _this.$q.dialog({
        component: ProfitCalculatorDialog,
        data: profitSettings,
        store: selectProducts[0].store.uid
      }).onOk((priceAndProfit) => {
        const currentPrice = parseFloat(priceAndProfit.price)
        if (currentPrice < 0) {
          _this.$q.notify({
            message: '无效价格',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        selectProducts.forEach(product => {
          if (!product.promotion_id) {
            _this.getDiscountListAndUpdate(product).then(res => {
              console.log('discount choise , now update price ', product)
              product.variants.forEach(variant => {
                _this.editVariantPrice(product, variant, currentPrice)
              })
            })
          } else {
            product.variants.forEach(variant => {
              _this.editVariantPrice(product, variant, currentPrice)
            })
          }
        })
      })
    },
    getProfitSettings (shopProduct) {
      const setting = {
        logistics_costs: 0,
        price: 0,
        weight: 0
      }
      if (shopProduct.supplier_info) {
        setting.logistics_costs = shopProduct.supplier_info.logistics_costs
      }
      setting.weight = shopProduct.weight
      shopProduct.variants.forEach(model => {
        if (model.price_info.global_price > setting.price) {
          setting.price = model.price_info.global_price
        }
      })
      return setting
    },
    editVariantPrice (product, variant, currentPrice) {
      const _this = this
      if (_this.editOriginalPrice && variant.discount_percentage < 1) {
        _this.$set(variant.price_info, 'original_price', (currentPrice / (1 - variant.discount_percentage)).toFixed(0))
      }
      if (currentPrice < variant.price_info.original_price) {
        _this.$set(variant.price_info, 'current_price', currentPrice)
      } else {
        this.$q.notify({
          message: '不能高于原价',
          icon: 'close',
          color: 'negative'
        })
      }
      _this.updateModelProfit(product, variant)
      return new Promise(resolve => {
        resolve(variant.price_info)
      })
    },
    getDiscountListAndUpdate (product) {
      var _this = this
      return new Promise((resolve, reject) => {
        _this.loading = true
        getauth('/store/discounts/?store_id=' + product.store.uid, {}).then(discountList => {
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
            product.promotion_id = _this.selectedFormData.discount.discount_id
            product.variants.forEach(variant => { variant.promotion_id = product.promotion_id })
            resolve(product)
          })
        })
      })
    },
    updateModelProfit (product, model) {
      var _this = this
      if (product.store.profit_setting && product.supplier_info) {
        const calculate = JSON.parse(JSON.stringify(product.store.profit_setting))
        const profit = profitService.getNetProfit(calculate, model.price_info.current_price, 1,
          product.weight, model.price_info.global_price, product.supplier_info.logistics_costs).toFixed(2)
        console.log('updateModelProfit ', model.current_price, product.weight, model.price_info.global_price, product.supplier_info.logistics_costs, profit)
        _this.$set(model, 'profit', profit)
      } else {
        console.log('upate model profit not set .....', product)
        _this.$set(model, 'profit', '--')
      }
    }
  },
  created () {
    console.log('create ', this.products)
    var _this = this
    this.products.forEach(product => {
      if (product.store.profit_setting && product.supplier_info) {
        const calculate = JSON.parse(JSON.stringify(product.store.profit_setting))
        product.variants.forEach(model => {
          const profit = profitService.getNetProfit(calculate, model.price_info.current_price, 1,
            product.weight, model.price_info.global_price, product.supplier_info.logistics_costs).toFixed(2)
          console.log('calculate model profit ', model.price_info.current_price, product.weight, model.price_info.global_price, product.supplier_info.logistics_costs, profit)
          _this.$set(model, 'profit', profit)
        })
      } else {
        product.variants.forEach(model => {
          _this.$set(model, 'profit', '请完善商品信息')
        })
      }
      product.variants.forEach(model => {
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
