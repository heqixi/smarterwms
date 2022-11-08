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
      pathname: 'product',
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
          name: 'new',
          label: '新增',
          tip: '新增商品',
          icon: 'add',
          click: () => {
            _this.editProductPopup()
          }
        },
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
          field: 'image',
          style: 'width:100px'
        },
        // {
        //   name: 'tags',
        //   required: true,
        //   label: '标签',
        //   align: 'center',
        //   options: 'tagsOptions',
        //   field: 'tags',
        //   multiple: true,
        //   edit: true,
        //   type: 'select',
        //   style: {
        //     width: '200px',
        //     whiteSpace: 'normal'
        //   },
        //   optionLabel: tagObj => {
        //     if (tagObj == undefined || tagObj.length <= 0) {
        //       return '添加标签'
        //     }
        //     return tagObj.tag
        //   },
        //   newValue: goods => {
        //     return new Promise((resolve, reject) => {
        //       _this.newGoodsTag(goods).then(tag => {
        //         resolve(tag)
        //       })
        //     })
        //   },
        //   onUpdate: (goods, newValue) => {
        //     return _this.updateGoodsTags(goods, newValue)
        //   }
        // },
        {
          name: 'product_sku',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          field: 'sku',
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
          field: 'name',
          style: {
            width: '200px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'store',
          label: '店铺',
          field: 'store',
          align: 'center',
          class: 'col-4 text-center',
          style: { width: '200px', maxWidth: '200px', whiteSpace: 'normal', fontSize: '4px' },
          fieldMap: store => { return store.name + '(' + store.area + ')' }
        },
        {
          name: 'status',
          label: '状态',
          field: 'status',
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
                  name: 'publish_all',
                  label: '发布到所有店铺',
                  click: (product) => {
                    console.log('publish all, product ', product)
                  }
                },
                {
                  name: 'publish_global_product',
                  label: '发布到全球商品',
                  click: (product) => {
                    console.log('publish global product, product ', product)
                  }
                },
                {
                  name: 'publish_store',
                  label: '发布到店铺商品',
                  click: (product) => {
                    _this.selectStoreAndPublish(product)
                    console.log('publish store product, product ', product)
                  }
                }
              ],
              click: product => {
                // _this.publishProduct(product)
              }
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
      if (product.status === 'PB') {
        _this.$q.notify({
          message: '商品已经发布，请刷新页面',
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
    editProductPopup (product) {
      const productId = product ? product.id : undefined
      var _this = this
      _this.$q.dialog({
        component: NewProductsDialog,
        productId: productId
      }).onOk((saveProduct) => {
        product.sku = saveProduct.sku
        product.desc = saveProduct.desc
        product.status = saveProduct.status
        product.image = saveProduct.image
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
        _this.pathname +
        '?tags=details&status__in=PR,ED',
        {}
      ).then(res => {
        console.log('get product List ', res)
        _this.table_list = res.results
        _this.numRows = res.count
        // _this.tags_list = res.tags_list
        // forTest
        _this.pathname_previous = res.previous
        _this.pathname_next = res.next
        _this.loading = false
      }).catch(err => {
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
            getauth(_this.pathname + `?tags=details&purchases=details&supplier=details&variants=details&variants_limit=2&search=${searchTerm}`, {})
              .then(res => {
                clearTimeout(this.search_task)
                _this.loading = false
                const products = res.results
                console.log('get search list result ', res.results)
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
    },
    getStoreInfo () {

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
