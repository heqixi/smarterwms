<template>
  <q-dialog ref="dialog" no-backdrop-dismiss>
    <q-card style="min-width: 600px">
      <q-card-section class="q-py-none">
        <q-banner class="q-pa-none">
          组合装产品编辑
        </q-banner>
        <q-separator/>
        <div class="row">
          <div class="col q-pa-xs">
            <q-input dense borderless value="选择主产品" readonly>
              <template v-slot:after>
                <q-btn dense class="float-right text-black" label="选择" @click="selectProduct"/>
              </template>
            </q-input>
            <div class="row q-my-md" :key="pkg.id" v-for="pkg in packages">
              <span class="col-4">
                <q-icon size="50px" :name="`img:${pkg.image}`"/>
              </span>
              <span class="col-8" style="display: table">
                <span class="full-height" style="display: table-cell; vertical-align: middle">
                  {{pkg.sku}}
                </span>
              </span>
            </div>
          </div>
          <q-separator vertical/>
          <div class="col q-pa-xs">
            <q-input dense borderless value="选择子产品" readonly>
              <template v-slot:after>
                <q-btn dense class="float-right text-black" label="选择" @click="selectGoods"/>
              </template>
            </q-input>
            <div class="row q-my-md" :key="item.id" v-for="item in items">
              <span class="col-4">
                <q-icon size="50px" :name="`img:${item.image}`"/>
              </span>
              <span class="col-8" style="display: table">
                <span class="full-height" style="display: table-cell; vertical-align: middle">
                  {{item.sku}}
                </span>
              </span>
            </div>
          </div>
        </div>
        <q-separator/>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide()"/>
        <q-btn :label="$t('submit')" @click="submit()" color="primary" text-color="white"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import ProductDialog from 'pages/store/components/productdialog'
import GoodsSearch from 'pages/order/components/goodssearch'

export default {
  name: 'PackageEditDialog',
  data () {
    return {
      packages: [],
      items: []
    }
  },
  methods: {
    selectGoods () {
      const _this = this
      _this.$q.dialog({
        component: GoodsSearch
      }).onOk(goodsList => {
        console.log('GoodsSearch', goodsList)
        if (goodsList && goodsList.length > 0) {
          console.log('goodsList', goodsList)
          goodsList.forEach(goods => {
            _this.items.push({
              uid: goods.id,
              product_type: 3,
              name: goods.goods_name,
              sku: goods.goods_code,
              image: goods.goods_image
            })
          })
        }
      })
    },
    selectProduct () {
      const _this = this
      _this.$q.dialog({
        component: ProductDialog
      }).onOk(productList => {
        if (productList && productList.length > 0) {
          productList.forEach(product => {
            if (product.store_product) {
              _this.packages.push({
                product_type: 2,
                uid: product.model_id,
                name: product.model_sku,
                sku: product.model_sku,
                image: product.image
              })
            } else {
              _this.packages.push({
                product_type: 1,
                uid: product.product_id,
                name: product.product_name,
                sku: product.product_sku,
                image: product.image_url
              })
            }
          })
        }
      })
    },
    submit () {
      const _this = this
      _this.$emit('ok', {
        packages: _this.packages,
        items: _this.items
      })
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  }
}
</script>

<style scoped>

</style>