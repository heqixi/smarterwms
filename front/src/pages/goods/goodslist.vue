<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <CommonTable
        ref="goodsTable"
        :table_list="table_list"
        :row-key="rowKey"
        :columns="columns"
        :filterFn="filteredRows"
        :searchFn="getSearchList"
        :loading="loading"
        :numRows="numRows"
        :topButtons="topButtons"
        :getNextPage="getListNext"
        multiple-select="true"
        @refresh="reFresh"
      />
    </transition>
    <q-dialog v-model="newDataDialog">
      <NewForm
        :items="newFormItems"
        :newFormData="newFormItemData"
        @newDataSummit="onNewDataSummit"
        @newDataCancel="onNewDataCancel"
      />
    </q-dialog>
  </div>
</template>
<router-view/>

<script>
import {
  getauth,
  postauth
} from 'boot/axios_request'
import { LocalStorage } from 'quasar'
import CommonTable from '../../components/Share/commontable.vue'
import NewForm from '../../components/Share/newForm.vue'
import GoodsEditPriceDialog from 'src/pages/goods/components/goodsPriceEdit'
import NewProductsDialog from 'pages/goods/components/newProductsDialog'
import SelectStore from 'pages/goods/components/selectstoredialog'
import { CURRENCY_CODE } from 'src/store/goods/types'

export default {
  name: 'Pagegoodslist',

  data () {
    var _this = this
    return {
      newDataDialog: false,
      newFormItems: [],
      newFormItemData: {},
      onNewDataSummit: undefined,
      onNewDataCancel: undefined,
      goods_code: '',
      goods_desc: '',
      numRows: 0,
      openid: '',
      login_name: '',
      authin: '0',
      pathname: 'store/global/',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      viewForm: false,
      goodsClassForm: false,
      printObj: {
        id: 'printMe',
        popTitle: this.$t('inbound.asn')
      },
      table_list: [],
      search_task: undefined,
      tags_list: [],
      rowKey: 'id',
      supplier_list: [],
      topButtons: [
        {
          name: 'delete',
          label: '删除',
          tip: '删除选中商品',
          style: { width: '50px' },
          click: products => {
            if (products.length <= 0) {
              this.$q.notify({
                message: '请选择要删除的产品',
                icon: 'close',
                color: 'negative'
              })
              return
            }
            _this.deleteProducts(products)
          }
        },
        {
          name: 'editPrice',
          label: '批量改价',
          tip: '修改价格',
          click: (priceInfos) => {
            console.log('edit price info ', priceInfos)
            _this.productPriceEditPopup(priceInfos)
          }
        },
        {
          name: 'clone',
          label: '复制',
          tip: '复制已有产品为新品',
          click: products => {
            console.log('clone product ', products)
            _this.cloneProducts(products)
          }
        }
      ],
      checkboxGroup: [
        {
          name: 'status_selectors',
          label: '状态',
          checkboxes: [
            {
              name: 'edit',
              label: '待编辑'
            }
          ]
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
          style: 'width:100px'
        },
        {
          name: 'product_sku',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          field: 'product_sku',
          type: 'text',
          style: {
            width: '100px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'product_name',
          required: true,
          label: this.$t('goods.view_goodslist.goods_name'),
          align: 'center',
          type: 'longText',
          field: 'product_name',
          style: {
            width: '200px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'store_prices',
          label: '店铺信息',
          field: 'store_prices',
          type: 'table',
          rowHeight: 20,
          keepExpand: true,
          style: { textAlign: 'center', width: '400px', maxWidth: '400px' },
          subColumns: [
            {
              name: 'store',
              label: '店铺',
              field: 'store',
              class: 'col-4 text-center',
              style: { width: '200px', maxWidth: '200px', whiteSpace: 'normal', fontSize: '4px' },
              fieldMap: store => { return store.name + '(' + store.area + ')' }
            },
            {
              name: 'original_price',
              label: '原价',
              field: 'self',
              class: 'col-2 text-center',
              style: { width: '80px', maxWidth: '80px', whiteSpace: 'normal', fontSize: '8px' },
              fieldMap: priceInfo => { return _this.productPriceInfo2Str(priceInfo.original_price) }
            },
            {
              name: 'current_price',
              label: '售价',
              field: 'self',
              class: 'col-3 text-center',
              style: { width: '120px', whiteSpace: 'normal', fontSize: '8px' },
              fieldMap: priceInfo => { return _this.productPriceInfo2Str(priceInfo.current_price) }
            },
            {
              name: 'profit',
              label: '利润估计',
              field: 'profit',
              class: 'col-3'
            }
          ]
        },
        {
          name: 'status',
          label: '状态',
          field: 'product_status',
          align: 'center',
          style: 'width:50px',
          type: 'text',
          fieldMap: status => {
            if (status === 'PB') {
              return '已发布'
            } else if (status === 'PR') {
              return '可发布'
            } else if (status === 'ED') {
              return '待编辑'
            }
          }
        },
        {
          name: 'create_time',
          label: this.$t('createtime'),
          field: 'create_time',
          align: 'center',
          style: 'width:80px'
        },
        {
          name: 'action',
          label: this.$t('action'),
          type: 'actions',
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          align: 'center',
          actions: [
            {
              name: 'publish',
              label: '上架',
              tip: '发布产品',
              type: 'button-dropdown',
              style: { width: '50px', maxWidth: '80px' },
              subButtons: [
                {
                  name: 'publish_store',
                  label: '发布到店铺',
                  click: (product) => {
                    _this.selectStoreAndPublish(product)
                    console.log('publish store product, product ', product)
                  }
                }
              ]
            },
            {
              name: 'edit',
              label: '编辑',
              tip: '编辑产品',
              type: 'button',
              style: { width: '50px', maxWidth: '80px' },
              click: product => {
                _this.editProductPopup(product)
              }
            }
          ]
        }
      ],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      token: LocalStorage.getItem('openid')
    }
  },
  methods: {
    cloneProducts (products) {
      var _this = this
      if (products.length <= 0) {
        _this.$q.notify({
          message: '请选择产品',
          icon: 'check',
          color: 'green'
        })
        return
      }
      _this.loading = true
      const productIds = products.map(product => { return product.id })
      console.log('begin to clone products ', productIds)
      postauth('goods/product/clone', productIds).then(cloneProducts => {
        console.log('clone products ', cloneProducts)
        _this.loading = false
        _this.$q.notify({
          message: `成功复制 ${cloneProducts.length} 个产品`,
          icon: 'check',
          color: 'green'
        })
        cloneProducts.forEach(product => {
          _this.table_list.unshift(product)
        })
      }).catch(err => {
        _this.loading = false
        console.error('copy product fail ', err)
        _this.$q.notify({
          message: '复制产品失败',
          icon: 'close',
          color: 'negative'
        })
      })
    },
    async selectStoreAndPublish (product) {
      var _this = this
      if (product.status === 'ED') {
        _this.$q.notify({
          message: '请先完善发布信息',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      _this.$q.dialog({
        component: SelectStore,
        // data: merchants,
        title: '请选择店铺'
      }).onOk(stores => {
        console.log('select stores ', stores)
        if (stores.length <= 0) {
          _this.$q.notify({
            message: '请选择需要发布的商店',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        getauth(`goods/product/${product.id}/?models=true&publish=true&product_supplier=true&product_logistic=true`, {}).then(productWidthModels => {
          console.log('get product with models ', productWidthModels)
          const productModels = productWidthModels.models
          const productPriceInfo = []
          stores.forEach(store => {
            const models = JSON.parse(JSON.stringify(productModels))
            let discount
            const discountModelList = []
            models.forEach(model => {
              const storePrice = model.price_info.find(priceInfo => {
                return priceInfo.store_id === store.uid
              })
              const currentPrice = storePrice ? storePrice.current_price : 0
              const originalPrice = storePrice ? storePrice.original_price : 0
              discount = storePrice ? { discount_id: storePrice.discount_id } : { discount_id: 0 }
              if (!model.current_price) {
                _this.$set(model, 'current_price', currentPrice)
                _this.$set(model, 'discount', discount)
              }
              if (!model.original_price) {
                _this.$set(model, 'original_price', originalPrice)
              }
              model.model_id = store.uid + '_' + model.sku

              discountModelList.push({
                model_id: model.model_id,
                model_original_price: originalPrice,
                model_promotion_price: currentPrice
              })
            })
            const priceInfo = {
              area: store.area,
              // image: _this.product.image,
              // sku: _this.product.sku,
              models: models,
              currency: CURRENCY_CODE[store.area],
              type: 'shopee',
              store_id: store.uid,
              store_name: store.name,
              discount: {
                discount_id: discount ? discount.discount_id : 0,
                item_list: [{ model_list: discountModelList }]
              },
              store: store,
              supplier: productWidthModels.supplier,
              logistic: productWidthModels.logistic,
              sku: product.sku,
              image: product.image
            }
            productPriceInfo.push(priceInfo)
          })
          console.log('wrap price info  with models ', productPriceInfo)
          _this.$q.dialog({
            component: GoodsEditPriceDialog,
            products: productPriceInfo,
            rowKey: 'store_id',
            modelKey: 'sku',
            editOriginalPrice: true,
            tableStyle: {
              width: '1500px',
              maxWidth: '1500px'
            }
          }).onOk((priceInfos) => {
            console.log('edit priece result, ok ', priceInfos)
            _this.saveModelStorePrice(product, priceInfos)
          })
        })
      })
    },
    saveModelStorePrice (product, priceInfos) {
      var _this = this
      const priceInfo2Save = []
      const store2Publish = []
      priceInfos.forEach(priceInfo => {
        const storeId = priceInfo.store_id
        store2Publish.push(storeId)
        priceInfo.models.forEach(model => {
          const existStorePrice = model.price_info.find(info => {
            return info.store_id === storeId
          })
          if (!existStorePrice) {
            priceInfo2Save.push({
              store_id: storeId,
              current_price: model.current_price,
              original_price: model.original_price,
              product: model.id,
              discount_id: priceInfo.discount.discount_id,
              currency: priceInfo.currency
            })
          } else if (existStorePrice.original_price !== model.original_price ||
            existStorePrice.current_price !== model.current_price) {
            priceInfo2Save.push({
              current_price: model.current_price,
              original_price: model.original_price,
              discount_id: priceInfo.discount.discount_id,
              id: existStorePrice.id
            })
          }
        })
      })
      if (priceInfo2Save.length > 0) {
        console.log(' priceInfo2Save priece result, ok ', priceInfo2Save)
        postauth('publish/price', priceInfo2Save).then(res => {
          console.log('save or update model price ', res)
          _this.publishProduct(product, store2Publish)
        })
      } else {
        this.publishProduct(product, store2Publish)
      }
    },
    publishProduct (product, stores) {
      postauth(this.pathname + '/publish', { id: product.id, stores: stores }).then(res => {
        console.log('publish product res ', res)
      })
    },
    productPriceInfo2Str (priceInfo) {
      if (!priceInfo || !priceInfo || priceInfo.min <= 0 || priceInfo.max <= 0 || priceInfo.max < priceInfo.min) {
        return '--'
      }
      if (priceInfo.min === priceInfo.max) {
        return priceInfo.min
      }
      return priceInfo.min + ' - ' + priceInfo.max
    },
    productPriceEditPopup (products) {
      console.log('edit price of product ', products)
      var _this = this
      _this.$q.dialog({
        component: SelectStore,
        // data: merchants,
        title: '请选择店铺'
      }).onOk(stores => {
        if (stores.length <= 0) {
          _this.$q.notify({
            message: '请至少选择一个店铺',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        const storeUids = stores.map(store => { return store.uid })
        _this.getProductPriceInfo(products, storeUids).then(priceInfoList => {
          console.log('edit price GoodsEditPriceDialog ', priceInfoList, stores)
          priceInfoList.forEach(priceInfo => {
            stores.forEach(store => {
              if (priceInfo.store_id === store.uid) {
                priceInfo.store = store
              }
            })
          })
          console.log('edit price GoodsEditPriceDialog ', priceInfoList)
          _this.$q.dialog({
            component: GoodsEditPriceDialog,
            products: priceInfoList,
            rowKey: 'item_id',
            tableStyle: {
              width: '1500px',
              maxWidth: '1500px'
            }
          }).onOk((priceInfos) => {
            console.log('deleteWithRelativeEntry on ok')
            _this.updateDiscount(priceInfos)
          })
        })
      })
    },
    updateDiscount (priceInfoSelected) {
      const shopeeDiscountsForm = []
      let model2UpdateNum = 0
      priceInfoSelected.forEach(priceInfo => {
        if (priceInfo.type === 'shopee') {
          const discount = priceInfo.discount
          const discoutToSave = {
            discount_id: discount.discount_id,
            store_id: priceInfo.store_id,
            item_list: [
              {
                item_id: priceInfo.item_id,
                purchase_limit: 0,
                model_list: discount.item_list[0].model_list
              }
            ]
          }
          if (discount.add) {
            discoutToSave.add = true
            model2UpdateNum += discoutToSave.item_list[0].model_list.length
            shopeeDiscountsForm.push(discoutToSave)
          } else {
            const model2Add = discount.item_list[0].model_list.filter(model => {
              return model.add
            })
            if (model2Add.length > 0) {
              const discoutToSaveCopy = JSON.parse(JSON.stringify(discoutToSave))
              discoutToSaveCopy.add = true
              discoutToSaveCopy.item_list[0].model_list = model2Add
              model2UpdateNum += model2Add.length
              shopeeDiscountsForm.push(discoutToSaveCopy)
            }
            const model2Update = discount.item_list[0].model_list.filter(model => {
              return model.update
            })
            if (model2Update.length > 0) {
              const discoutToSaveCopy = JSON.parse(JSON.stringify(discoutToSave))
              discoutToSaveCopy.update = true
              model2UpdateNum += model2Update.length
              discoutToSaveCopy.item_list[0].model_list = model2Update
              shopeeDiscountsForm.push(discoutToSaveCopy)
            }
          }
        } else {
          throw Error('Only support update shopee product discount')
        }
      })
      debugger
      if (shopeeDiscountsForm.length > 0) {
        var _this = this
        console.log('update shopee discount ', shopeeDiscountsForm)
        _this.loading = true
        postauth('/store/product/discount', shopeeDiscountsForm).then(successCount => {
          _this.loading = false
          console.log('update shopee discount res', successCount)
          if (model2UpdateNum < successCount) {
            _this.$q.notify({
              message: `成功修改 ${successCount} 个变体价格，${model2UpdateNum - successCount} 个失败`,
              icon: 'close',
              color: 'negative',
              timeout: 5000
            })
          } else {
            _this.$q.notify({
              message: `成功修改 ${successCount} 个变体价格`,
              icon: 'check',
              color: 'green'
            })
          }
        })
      }
    },
    getProductPriceInfo (products, storeUids) {
      var _this = this
      const queryParams = products.map(product => product.id).join('&id=')
      const storeUidsParams = storeUids.join('&shop=')
      return new Promise((resole, reject) => {
        console.log('get product price info ', products)
        _this.loading = true
        getauth('goods/product/price/?id=' + queryParams + '&shop=' + storeUidsParams, {}).then(priceInfoList => {
          console.log('get product price info ', priceInfoList)
          resole(priceInfoList)
          _this.loading = false
        })
      })
    },
    editProductPopup (product) {
      console.log('edit prodcut pop up')
      const productId = product ? product.id : undefined
      var _this = this
      _this.$q.dialog({
        component: NewProductsDialog,
        productId: productId
      }).onOk((saveProduct) => {
        product.sku = saveProduct.baseInfo.sku
        product.desc = saveProduct.desc
        product.status = saveProduct.baseInfo.status
        product.image = saveProduct.baseInfo.image
      })
    },
    deleteProducts (products) {
      var _this = this
      const productIds = products.map(product => { return product.id })
      _this.loading = true
      console.log('delete products ', productIds)
      postauth(_this.pathname + '/delete', productIds).then(res => {
        console.log('delete goods success ', res)
        productIds.forEach(productId => {
          for (var i = _this.table_list.length - 1; i >= 0; i--) {
            if (_this.table_list[i].id === productId) {
              _this.table_list.splice(i, 1)
            }
          }
        })
        _this.loading = false
        _this.$refs.goodsTable.clearSelect()
      }).catch(err => {
        _this.loading = false
        _this.$q.notify({
          message: '删除产品失败',
          icon: 'close',
          color: 'negative'
        })
        console.log('delete goods fail ', err)
      })
    },
    filteredRows (product, searchTerm) {
      const codeMatch = product.sku.indexOf(searchTerm) > -1
      const tagMatch = false
      const nameMatch = product.name.indexOf(searchTerm) > -1
      return codeMatch || tagMatch || nameMatch
    },
    getList () {
      var _this = this
      _this.loading = true
      getauth(
        _this.pathname + '?type=1&product_status=NORMAL&store_prices=true',
        {}
      ).then(res => {
        console.log('get product List ', res.results, res.tags_list)
        _this.table_list = res.results
        _this.table_list.forEach(product => {
          product.publish = []
        })
        _this.numRows = res.count
        // _this.tags_list = res.tags_list
        // forTest
        _this.pathname_previous = res.previous
        _this.pathname_next = res.next
        _this.loading = false
      })
        .catch(err => {
          _this.loading = false
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
    },
    getSearchList (searchTerm) {
      var _this = this
      return new Promise((resolve, reject) => {
        if (searchTerm.length <= 0) {
          console.log('must seachch something')
          reject('already search')
          return
        }
        if (this.search_task) {
          console.log('clear time out')
          clearTimeout(this.search_task)
          this.search_task = undefined
        }
        this.search_task = setTimeout(() => {
          _this.loading = true
          console.log('getSearchList ', searchTerm)
          if (LocalStorage.has('auth')) {
            getauth(_this.pathname + `?tags=details&publish=true&shopee_store=true&search=${searchTerm}`, {})
              .then(res => {
                clearTimeout(this.search_task)
                _this.loading = false
                const products = res.results
                console.log('get search list result ', res.results)
                products.forEach(product => {
                  const exist = _this.table_list.find(exitProduct => {
                    return exitProduct.id === product.id
                  })
                  if (exist !== undefined) {
                    console.warn('duplicate goods find ', product.id)
                  } else {
                    _this.table_list.push(product)
                  }
                })
                resolve(products)
              })
              .catch(err => {
                clearTimeout(this.search_task)
                reject('get search list fail')
                _this.loading = false
                _this.$q.notify({
                  message: err.detail,
                  icon: 'close',
                  color: 'negative'
                })
              })
          }
        }, 800)
      })
    },
    getListPrevious () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getauth(_this.pathname_previous, {})
          .then(res => {
            _this.table_list = res.results
            _this.pathname_previous = res.previous
            _this.pathname_next = res.next
          })
          .catch(err => {
            _this.$q.notify({
              message: err.detail,
              icon: 'close',
              color: 'negative'
            })
          })
      } else {
      }
    },
    getListNext (size) {
      var _this = this
      this.loading = true
      let path = _this.pathname_next
      const url = new URL('http://' + path)
      const urlParams = new URLSearchParams(url.search)
      if (size > 0) {
        urlParams.set('limit', size)
        path = 'goods/product/?' + urlParams.toString()
      }
      return new Promise((resolve, reject) => {
        if (LocalStorage.has('auth')) {
          _this.loading = true
          getauth(path, {})
            .then(res => {
              const products = res.results
              products.forEach(product => {
                product.publish = [
                  {
                    store: 'juyigou.br',
                    price: 7.99,
                    profit: 1
                  },
                  {
                    store: 'juyigou.mx',
                    price: 28,
                    profit: 4
                  }
                ]
                const exist = _this.table_list.find(exitProduct => {
                  return exitProduct.id === product.id
                })
                if (exist !== undefined) {
                  console.warn('duplicate goods find ', product.goods_code)
                } else {
                  _this.table_list.push(product)
                }
              })
              _this.pathname_previous = res.previous
              _this.pathname_next = res.next
              _this.loading = false
            })
            // .catch(err => {
            //   _this.loading = false
            //   _this.$q.notify({
            //     message: err.detail,
            //     icon: 'close',
            //     color: 'negative'
            //   })
            // })
        } else {
          reject('not login in')
          _this.$q.notify({
            message: '请重新登录再操作',
            icon: 'close',
            color: 'negative'
          })
        }
      })
    },
    reFresh () {
      var _this = this
      _this.getList()
    }
  },
  created () {
    var _this = this
    if (LocalStorage.has('openid')) {
      _this.openid = LocalStorage.getItem('openid')
    } else {
      _this.openid = ''
      LocalStorage.set('openid', '')
    }
    if (LocalStorage.has('login_name')) {
      _this.login_name = LocalStorage.getItem('login_name')
    } else {
      _this.login_name = ''
      LocalStorage.set('login_name', '')
    }
    if (LocalStorage.has('auth')) {
      _this.authin = '1'
      _this.getList()
    } else {
      _this.authin = '0'
    }
  },
  mounted () {
    var _this = this
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + 'px'
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px'
    }
  },
  updated () {
  },
  destroyed () {
  },
  components: {
    CommonTable,
    NewForm,
    GoodsEditPriceDialog,
    NewProductsDialog
  }
}
</script>

<style>
.q-uploader {
  width: 100% !important;
}

.q-uploader__header {
  width: 100% !important;
}

.q-uploader__list {
  width: 100% !important;
}
</style>
