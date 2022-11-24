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
import mediaService from 'pages/goods/services/mediaservice'

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
      pathPrefix: 'store/global/',
      pathname: 'store/global/?product_status=EDIT,PUBLISH_READY&type=1&store_detail=true',
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
          name: 'store',
          label: '店铺',
          field: 'store',
          align: 'center',
          class: 'col-4 text-center',
          type: 'text',
          style: { width: '200px', maxWidth: '200px', whiteSpace: 'normal', fontSize: '4px' },
          fieldMap: store => { return store.name}
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
            } else if (status === 'PUBLISH_READY') {
              return '可发布'
            } else if (status === 'EDIT') {
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
        const storeIds = stores.map(store => { return store.id }).join(',')
        getauth(`shopee/publish/product/shop?id=${product.id}&stop_id=${storeIds}&models=true&supplier_info=true&product_medias=true&options=true`, {})
          .then(globalProduct => {
            console.log('get product with models ', globalProduct)
            const productPriceInfo = []
            stores.forEach(store => {
              const shopProduct = globalProduct.shop_products.find(p => { return p.store.id === store.id })
              shopProduct.variants.forEach(variant => {
                const globalVariant = globalProduct.variants.find(v => { return v.model_sku === variant.model_sku })
                variant.image_url = globalVariant.image
                variant.price_info = variant.price_info || {
                  original_price: undefined,
                  current_price: undefined,
                  global_price: undefined
                }
                variant.price_info.global_price = globalVariant.price_info ? globalVariant.price_info.original_price : undefined
                // Usually, all variants of same shop product should share same promotion_id
                shopProduct.promotion_id = variant.promotion_id ? variant.promotion_id : shopProduct.promotion_id
                shopProduct.supplier_info = globalProduct.supplier_info
              })
              shopProduct.store = store
              productPriceInfo.push(shopProduct)
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
              _this.saveModelStorePrice(globalProduct, priceInfos)
            })
          })
      })
    },
    saveModelStorePrice (globalProduct, shopProducts) {
      var _this = this
      const store2Publish = shopProducts.map(product => { return product.store.id })
      if (shopProducts.length > 0) {
        console.log(' priceInfo2Save priece result, ok ', shopProducts)
        postauth('shopee/publish/product/price', shopProducts).then(res => {
          console.log('save or update model price ', res)
          _this.publishProduct(globalProduct, store2Publish)
        })
      } else {
        this.publishProduct(globalProduct, store2Publish)
      }
    },
    async publishProduct (product, stores) {
      product.medias.sort((x, y) => { return x.index - y.index })
      const image2publish = []
      product.medias.forEach(media => {
        if (image2publish.length < 8 && (media.image_id || media.url)) {
          image2publish.push(media)
        }
      })

      const image2Fetch = image2publish.filter(media => { return !media.image_id })
      await this.fetchProductImageRecursieve(image2Fetch, 0)

      const option2FetchImage = product.option_items.filter(item => {
        const option = product.options.find(opt => { return opt.id === item.store_product_option })
        return option.index === 0 && !item.image_id
      })
      await this.fetchOptionImageRecursieve(option2FetchImage, 0)
      if (image2Fetch.length || option2FetchImage.length) {
        const mediaInfo = {
          product_media: image2Fetch,
          option_media: option2FetchImage
        }
        console.log('publish media image ', mediaInfo)
        const res = await postauth('shopee/publish/media', mediaInfo)
        console.log('publish media res ', res)
      }
      // publish product
      postauth('shopee/publish/product/publish', { id: product.id, stores: stores }).then(res => {
        console.log('publish product res ', res)
      })
    },
    async fetchProductImageRecursieve (mediaList, i) {
      if (i >= mediaList.length) {
        return
      }
      const fetchResult = await mediaService.imgUrlToFile(mediaList[i].url)
      mediaList[i].file = fetchResult.fileBytes
      mediaList[i].filename = fetchResult.filename
      await this.fetchProductImageRecursieve(mediaList, i + 1)
    },
    async fetchOptionImageRecursieve (mediaList, i) {
      if (i >= mediaList.length) {
        return
      }
      const fetchResult = await mediaService.imgUrlToFile(mediaList[i].image_url)
      mediaList[i].file = fetchResult.fileBytes
      mediaList[i].filename = fetchResult.filename
      await this.fetchOptionImageRecursieve(mediaList, i + 1)
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
      postauth(_this.pathPrefix + '/delete', productIds).then(res => {
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
      getauth(_this.pathname, {}).then(res => {
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
