<template>
  <q-dialog ref="dialog" class="relative-position" full-width>
    <q-card class="shadow-24" v-if="!loading">
      <q-bar
        class="bg-light-blue-10 text-white rounded-borders"
        style="height: 50px">
        <div>{{ $t('newtip') }}</div>
        <q-space/>
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip content-class="bg-amber text-black shadow-4">
            {{
              $t('index.close')
            }}
          </q-tooltip>
        </q-btn>
      </q-bar>
      <q-card-section class="scroll">
        <GoodsSupplierInfo
          :supplier="product.supplier"
          @onChange="onSupplierInfoChange"
        />
        <q-separator dark vertical inset/>

        <Goodscategory
        :category="product.category"
        @merchantChange="onMerchantChange"
        />

        <q-separator dark vertical inset/>

        <GoodsBaseInfo
          :productBaseInfo="product.baseInfo"
          :category="product.category"
        />

        <q-separator dark vertical inset/>

        <GoodsImageInfo
          :data="product.images"
          :image-options="product.image_options"
          @onChange="onImagesChange"
        />

        <q-separator dark vertical inset/>

        <Goodspecification
          :main-sku="product.sku"
          :specifications="product.specifications"
          :models="product.models"
          :image-options="product.image_options"
          @removeSpec="onSpecificationRemove"
        />

        <q-separator dark vertical inset/>

        <LogisticsInfo
          :logistic="product.logistic"
        />
      </q-card-section>

      <div style="float: right; padding: 15px 15px 15px 0">
        <q-btn-group push>
          <q-btn
            color="white"
            text-color="black"
            style="margin-right: 25px"
            @click="newDataCancel()">{{ $t('cancel') }}
          </q-btn>
          <q-btn color="white" text-color="black" @click="newDataSubmit()">
            保存
          </q-btn>
          <q-btn color="white" text-color="black" @click="newDataSubmit(true)">
            保存并发布
          </q-btn>
        </q-btn-group>
      </div>
    </q-card>
    <q-inner-loading :showing="loading">
    </q-inner-loading>
  </q-dialog>

</template>

<script>
import GoodsBaseInfo from './goodsbaseinfo.vue'
import GoodsSupplierInfo from './goodsupplierInfo.vue'
import LogisticsInfo from './logisticsinfo'
import Goodspecification from './goodspecification.vue'
import GoodsImageInfo from 'pages/goods/components/goodsImageInfo'
import Goodscategory from 'pages/goods/components/goodscategory'
import { LocalStorage } from 'quasar'
import { getauth, postauth } from 'boot/axios_request'

import mediaService from 'pages/goods/services/mediaservice'
import NewFormDialog from 'components/Share/newFormDialog'

export default {
  name: 'NewProductsDialog',
  data () {
    return {
      loading: false,
      pathName: 'shopee/publish/',
      login_name: LocalStorage.getItem('login_name'),
      token: LocalStorage.getItem('openid'),
      currentMerchant: undefined,
      product: {
        baseInfo: {
          sku: '',
          name: '',
          desc: '',
          second_hand: false
        },
        sku: '',
        name: '',
        desc: '',
        second_hand: false,
        supplier: {
          url: '123'
        },
        specifications: [],
        status: 'ED',
        images: [],
        models: [],
        category: undefined,
        logistic: {
          product_w: undefined,
          product_h: undefined,
          product_d: undefined,
          weight: undefined,
          days_deliver: 3
        },
        image_options: []
      },
      upload_path_name: baseurl + 'goodsmedia/image/'
    }
  },
  methods: {
    onMerchantChange (merchant) {
      console.log('on merchant change', merchant)
      this.currentMerchant = merchant
      if (this.currentMerchant) {
        if (this.currentMerchant.platform === 1) {
          this.getShopeeProductInfo(this.productId, merchant)
        }
      }
    },
    onSupplierInfoChange (value, field) {
      this.product.supplier[field] = value
      this.product.supplier.update = true
      console.log('on supplier info change ', this.product.supplier)
    },
    // onLogisticInfoChange (value, field) {
    //   console.log('on logistic change ', value, field)
    //   this.product.logistic[field] = value
    //   this.product.logistic.update = true
    // },
    onSpecificationRemove (spec) {
      console.log('on Spec remove ', spec)
      if (!this.product.removeSpecification) {
        this.product.removeSpecification = []
      }
      this.product.removeSpecification.push(spec)
    },
    onImagesChange (images) {
      console.log('on images chage', images)
      var _this = this
      _this.product.images = images
    },
    wrapBaseInfo (formData) {
      if (this.product.specifications.length <= 0) {
        if (this.product.mode !== 'SG') {
          this.product.mode = 'SG' // 单变体模式
          this.product.update = true
        }
      } else {
        if (this.product.mode !== 'MT') {
          this.product.mode = 'MT' // 多变体模式
          this.product.update = true
        }
      }
      const firstImage = formData.images.sort((x, y) => {
        return x.index - y.index
      }).find(image => {
        return image.url !== undefined
      })
      formData.sku = this.product.baseInfo.sku
      formData.name = this.product.baseInfo.name
      formData.desc = this.product.baseInfo.desc
      formData.second_hand = this.product.second_hand
      formData.image = firstImage ? firstImage.url : undefined
      formData.mode = this.product.mode
      formData.status = this.product.status
    },
    wrapSupplierInfo (formData) {
      formData.supplier = {
        url: this.product.supplier.url,
        logistics_costs: this.product.supplier.logistics_costs,
        min_purchase_num: this.product.supplier.min_purchase_num,
        delivery_days: this.product.supplier.delivery_days,
        product: this.productId.id
      }
    },
    wrapImageInfo (formData) {
      formData.images = []
      this.product.images.forEach((image, index) => {
        formData.images.push({
          url: image.url,
          index: index
        })
      })
    },
    wrapModelInfo (formData) {
      formData.models_info = []
      this.product.models.filter(x => { return !x.is_delete }).forEach((model, index) => {
        const modelObj = {
          name: model.name,
          sku: model.sku,
          stock: {
            stock_qty: model.stock.stock_qty,
            price: model.stock.price
          },
          price_info: model.price_info
        }
        const sortedOption = []
        model.options.filter(x => {
          return !x.is_delete
        }).sort((x, y) => {
          return x.specification.index - y.specification.index
        }).forEach((option, optIndex) => {
          sortedOption.push(option.index)
        })
        modelObj.options_index = sortedOption.join(',')
        formData.models_info.push(modelObj)
      })
    },
    wrapSpecificatonInfo (formData) {
      // 先检查一遍时候是order
      formData.specifications = []
      this.product.specifications.filter(spec => { return !spec.is_delete }).forEach((spec, index) => {
        const spcObj = {
          name: spec.name,
          index: index,
          options: []
        }
        spec.options.filter(opt => { return !opt.is_delete }).forEach((option, optIndex) => {
          spcObj.options.push({
            name: option.name,
            image: option.image,
            index: optIndex
          })
        })
        formData.specifications.push(spcObj)
      })
    },
    wrapLogisticInfo (formData) {
      const logistic = this.product.logistic
      formData.logistic = {
        product_w: logistic.product_w,
        product_h: logistic.product_h,
        product_d: logistic.product_d,
        weight: logistic.weight,
        days_deliver: logistic.days_deliver,
        id: logistic.id
      }
    },
    wrapCategoryInfo (formData) {
      formData.category = {}
      const category = this.product.category
      if (!category) {
        return
      }
      const attributeValues = []
      console.log('wrap atrribute values ', category.attributes)
      if (category.attributes) {
        category.attributes.forEach(attribute => {
          let values
          if (Array.isArray(attribute.value)) {
            values = attribute.value
          } else {
            values = attribute.value ? [attribute.value] : []
          }
          values.forEach(value => {
            if (value.value_id) {
              attributeValues.push({
                attribute_id: attribute.attribute_id,
                display_value_name: value.display_value_name,
                value_id: value.value_id,
                multiple: attribute.multiple
              })
            }
          })
        })
      }
      let leafCategory = category
      while (leafCategory.sub_category) {
        leafCategory = leafCategory.sub_category
      }
      const brandInfo = {
        brand_id: category.brand_info.brand.brand_id,
        display_brand_name: category.brand_info.brand.display_brand_name
      }
      formData.category = {
        merchant_id: category.merchant.uid,
        category_id: leafCategory.category_id,
        attribute_values: attributeValues,
        brand: brandInfo
      }
    },
    newDataCancel () {
      console.log('newDataCancel')
      this.hide()
    },
    async newDataSubmit (publishStore) {
      console.log('newDataSubmit')
      var _this = this
      const product2Save = { id: this.product.id, publish: publishStore }
      if (_this.product.status === 'ED') {
        if (_this.isReadyToPublish()) {
          console.log('product is ready to publish ')
          product2Save.status = 'PR'
          _this.product.status = 'PR'
        }
      }
      this.loading = true
      try {
        this.wrapImageInfo(product2Save)
        // await this.fetchProductImageFile(product2Save) // 顺序不能调乱
        // await this.fetctOptionImageFile()
        this.wrapSpecificatonInfo(product2Save)
        this.wrapBaseInfo(product2Save)
        this.wrapSupplierInfo(product2Save)
        this.wrapModelInfo(product2Save)
        this.wrapLogisticInfo(product2Save)
        this.wrapCategoryInfo(product2Save)
      } catch (err) {
        this.loading = false
        console.log('save product fail ', err)
        this.$q.notify({
          message: '保存失败',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      let pathName = _this.pathName
      if (_this.currentMerchant && _this.currentMerchant.platform === 1) {
        pathName = 'shopee/publish/'
        product2Save.merchant = {
          id: _this.currentMerchant.id
        }
        product2Save.global_product_id = this.productId
      }
      console.log('new data summit ', product2Save)
      product2Save.creater = this.login_name
      postauth(pathName, product2Save).then(productSaved => {
        console.log('update product success ', productSaved)
        _this.product.id = productSaved.id
        _this.loading = false
        _this.$emit('ok', _this.product)
        _this.hide()
      }).catch(err => {
        _this.loading = false
        console.log('save product fail ', err)
      })
    },
    isReadyToPublish () {
      if (!this.product.images || this.product.images.length < 3) {
        this.$q.notify({
          message: '产品图片信息不完整',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      if (!this.product.baseInfo.sku || this.product.baseInfo.sku.length <= 0) {
        this.$q.notify({
          message: '缺少产品SKU',
          icon: 'close',
          color: 'negative'
        })
        return false
      }

      if (!this.product.baseInfo.name || !this.product.baseInfo.desc || this.product.baseInfo.name.length <= 0) {
        this.$q.notify({
          message: '产品名称,描述不完整',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      if (this.product.baseInfo.name.length > 32) {
        this.$q.notify({
          message: '产品名称过长',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      if (!this.product.logistic.weight || this.product.logistic.weight <= 0) {
        this.$q.notify({
          message: '缺少产品重量',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      for (let i = 0; i < this.product.specifications.length; i++) {
        const spec = this.product.specifications[i]
        if (spec.options.length <= 0) {
          this.$q.notify({
            message: `请至少为规格 ${spec.name} 设置一个选项`,
            icon: 'close',
            color: 'negative'
          })
          return false
        }
      }
      if (this.product.specifications && this.product.specifications.length > 0) {
        this.product.specifications[0].options.forEach(option => {
          if (!option.is_delete && !option.image) {
            this.$q.notify({
              message: '规格图片不完整',
              icon: 'close',
              color: 'negative'
            })
            return false
          }
        })
      }
      let allStockQty = 0
      const validModels = this.product.models.filter(model => { return !model.is_delete })
      if (validModels.length > 50) {
        this.$q.notify({
          message: '变体数量不能超过50个',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      for (let i = 0; i < this.product.models.length; i++) {
        const model = this.product.models[i]
        if (model.is_delete) {
          continue
        }
        if (!model.stock.stock_qty || !model.stock.price) {
          this.$q.notify({
            message: '变体价格/库存信息不完整',
            icon: 'close',
            color: 'negative'
          })
          return false
        }
        allStockQty += model.stock.stock_qty
      }
      if (allStockQty > 500000) {
        this.$q.notify({
          message: '库存总数不能超过50万',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      if (!this.product.category) {
        this.$q.notify({
          message: '缺少类别信息',
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      // 检查类别信息
      const root = this.product.category
      let leafCategory = root
      while (leafCategory.sub_category) {
        leafCategory = leafCategory.sub_category
      }
      if (leafCategory.has_children) {
        this.$q.notify({
          message: `商店 ${root.merchant.name} 的类别不完整`,
          icon: 'close',
          color: 'negative'
        })
        return false
      }
      const catetoryAttrbutes = root.attributes || []
      for (let i = 0; i < catetoryAttrbutes.length; i++) {
        const attribute = catetoryAttrbutes[i]
        if (attribute.is_mandatory) {
          const attrebuteValue = attribute.value
          if (!attrebuteValue || (Array.isArray(attrebuteValue) && attrebuteValue.length <= 0)) {
            console.log('missing madatory attribute value ,', attribute)
            this.$q.notify({
              message: '缺少必要的类别属性值',
              icon: 'close',
              color: 'negative'
            })
            return false
          }
        }
      }
      return true
    },
    async fetctOptionImageFile () {
      const specifications = this.product.specifications
      if (specifications.length <= 0) {
        console.log('no need to fetch option image')
        return
      }
      const firstLevelSpec = specifications.find(spec => {
        // 只有第一个规格的选项有图片
        return spec.index === 0
      })
      if (!firstLevelSpec || !firstLevelSpec.options) {
        console.log('no need to fetch option image, no first level spec')
        return
      }
      const toFetch = firstLevelSpec.options.filter(option => {
        if (option.is_delete) {
          return false
        }
        if (!option.option_media) {
          option.option_media = {
            url: option.image,
            media: undefined,
            update: true
          }
          option.update = true
        }
        const optionMedia = option.option_media
        return (option.image &&
          (optionMedia.media === undefined || optionMedia.media === null))
      })
      if (toFetch.length <= 0) {
        console.log('no need to fetch option image, to fetch is empty')
        return
      }
      firstLevelSpec.update = true
      await this.fetctOptionImageRecursieve(toFetch, 0)
    },
    async fetctOptionImageRecursieve (options, i) {
      if (i >= options.length) {
        return
      }
      const fetchResult = await mediaService.imgUrlToFile(options[i].image)
      options[i].option_media.file = fetchResult.fileBytes
      options[i].option_media.filename = fetchResult.filename
      options[i].update = true
      await this.fetctOptionImageRecursieve(options, i + 1)
    },
    async fetchProductImageFile (product2Save) {
      console.log(' fetch images ,', product2Save)
      if (!product2Save.images || product2Save.images.length <= 0) {
        return
      }
      const image2Fetch = product2Save.images.filter(image => {
        return image.url && !image.media && !image.is_delete
      })
      if (image2Fetch.length <= 0) {
        return
      }
      console.log('begin to fetch images ', image2Fetch)
      await this.fetchImageRecursive(image2Fetch, 0)
    },
    async fetchImageRecursive (images, i) {
      if (i >= images.length) {
        return
      }
      const result = await mediaService.imgUrlToFile(images[i].url)
      images[i].file = result.fileBytes
      images[i].filename = result.filename
      images[i].update = true
      await this.fetchImageRecursive(images, i + 1)
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    getProductInfo (productId) {
      if (this.currentMerchant) {
        if (this.currentMerchant.platform === 1) {
          this.getShopeeProductInfo(productId, this.currentMerchant)
        }
      } else {
        this.getGlobalProductInfo(productId)
      }
    },
    getGlobalProductInfo (productId) {
      var _this = this
      const queryParam = '?models=true&images=true&images_options=true&model_options=true&product_specification=true&product_media=true&product_supplier=true&product_logistic=true&product_category=true'
      getauth('product/' + productId + '/' + queryParam).then(product => {
        _this.unwrapProductInfo(product)
      }).catch(err => {
        console.log('get global product info fail ', err)
      })
    },
    getShopeeProductInfo (productId, store, force = false) {
      var _this = this
      const path = `shopee/publish/product?global_product_id=${productId}&store_id=${store.id}&force=${force}`
      _this.loading = true
      getauth(path).then(product => {
        if (!product) {
          _this.$q.dialog({
            component: NewFormDialog,
            title: `商品尚未认领到${store.name},是否现在认领？`
          }).onOk(() => {
            console.log('clain product to store ?')
            if (!force) {
              _this.getShopeeProductInfo(productId, store, true)
            } else {
              _this.loading = false
              console.error('Recusive call!!')
            }
          })
        } else {
          _this.loading = false
          _this.unwrapShopeeProductInfo(product, store)
        }
      }).catch(err => {
        _this.loading = false
        console.log('get shopee product fail ', err)
      })
    },
    unwrapShopeeProductInfo (product, store) {
      console.log('shopee product', product)
      this.product.logistic.product_w = product.width
      this.product.logistic.product_h = product.height
      this.product.logistic.product_d = product.length
      this.product.logistic.weight = product.weight
      this.product.logistic.days_deliver = product.days_to_ship
      this.product.baseInfo.desc = product.description.replaceAll('\n', '</br>')
      this.product.baseInfo.name = product.product_name
      this.product.baseInfo.sku = product.product_sku
      this.product.images = product.medias.filter(m => {
        return m.type === 2
      }).map(image => {
        return {
          index: image.index,
          url: image.url
        }
      }).sort((x, y) => { return x.index - y.index })

      this.product.category = product.category || {
        id: undefined,
        merchant: {
          id: store.id,
          uid: store.uid,
          name: store.name
        },
        merchant_id: store.id,
        category_id: undefined,
        sub_category: undefined,
        attributes: [],
        brand_info: {
          brand: {
            brand_id: 0,
            display_brand_name: 'NoBrand',
            original_brand_name: 'NoBrand'
          }
        }
      }
      product.specifications = product.options.map(option => {
        return {
          name: option.name,
          index: option.index,
          options: product.option_items.filter(opt => {
            return opt.store_product_option === option.id
          }).map(opt => {
            return {
              name: opt.name,
              index: opt.index,
              image: opt.image_url
            }
          }).sort((x, y) => { return x.index - y.index })
        }
      }).sort((x, y) => { return x.index - y.index })
      this.product.specifications = product.specifications
      this.product.models = product.variants.map(variant => {
        return {
          sku: variant.model_sku,
          name: variant.model_sku,
          options: variant.option_item_index.split(',').map((optIndex, index) => {
            const option = product.specifications[index].options.find(opt => { return opt.index + '' === optIndex })
            option.specification = product.specifications[index]
            return option
          }),
          stock: {
            stock_qty: variant.stock_info.current_stock,
            price: variant.price_info.original_price
          },
          option_item_index: variant.option_item_index
        }
      }).sort((x, y) => { return x.option_item_index - y.option_item_index })
      console.log('this product ', this.product)
    },
    unwrapProductInfo (product) {
      console.log('get product before ', product)
      if (product.desc && product.desc.length > 0) {
        product.desc = product.desc.replaceAll('\n', '</br>')
      }
      if (!product.logistic) {
        product.logistic = {
          product_w: undefined,
          product_h: undefined,
          product_d: undefined,
          weight: undefined,
          days_deliver: 3
        }
      }
      this.product.baseInfo.desc = product.desc.replaceAll('\n', '</br>')
      this.product.baseInfo.name = product.name
      this.product.baseInfo.sku = product.sku

      this.product.images = product.images
      this.product.category = undefined

      this.product.specifications = product.specifications.sort((specA, specB) => {
        return specA.index - specB.index
      })
      this.product.specifications.forEach(spec => {
        spec.options.sort((optA, optB) => {
          return (optA.specification.index * 100 + optA.index) - (optB.specification.index * 100 + optB.index)
        })
      })

      this.product.models = product.models
      this.product.models.forEach(model => {
        model.options.sort((optA, optB) => {
          return (optA.specification.index * 100 + optA.index) - (optB.specification.index * 100 + optB.index)
        })
      })
      this.product.models.sort((modelA, modelB) => {
        return modelA.options.reduce((index, option) => { return index + option.index + option.specification.index }, '') -
          modelB.options.reduce((index, option) => { return index + option.index + option.specification.index }, '')
      })
    }
  },
  created () {
    var _this = this
    if (this.productId) {
      console.log('on new product Dialog on create ', this.productId)
      _this.getProductInfo(this.productId)
    }
  },
  props: ['productId'],
  components:
    {
      GoodsImageInfo,
      GoodsBaseInfo,
      GoodsSupplierInfo,
      LogisticsInfo,
      Goodspecification,
      Goodscategory
    }
}

</script>

<style scoped>

</style>
