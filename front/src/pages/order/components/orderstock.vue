<style>
.base-info-font-size {
  font-size: 1em;
}
</style>
<template>
  <q-dialog ref="dialog">
    <q-card style="min-width: 450px">
      <q-card-section>
        <div class="row">
          <q-img class="col-3" contain :src="stock.goods.goods_image">
            <div v-if="packages" class="no-padding absolute-top text-center text-italic text-body2 base-info-font-size">
              {{$t('order.view_details.package')}}
            </div>
          </q-img>
          <div class="col-9">
            <div class="q-ma-md">{{$t('order.view_details.stock_status')}}: {{$t('order.view_details.stock_status_options.'+stock.stock_status)}}</div>
            <div class="q-ma-md">{{$t('goods.view_goodslist.goods_code')}}: {{stock.goods.goods_code}}</div>
            <div class="q-ma-md">{{$t('order.view_details.need_stock_qty')}}: {{stock.stock_qty}}</div>
          </div>
        </div>
        <template v-if="packages">
          <q-separator class="q-mb-xs"/>
          <div class="row" :key="pkg.id" v-for="pkg in packages">
            <q-img class="col-3" contain :src="pkg.image_url"/>
            <div class="col-9">
              <div class="q-ma-md">{{$t('order.view_details.stock_status')}}: {{$t('order.view_details.stock_status_options.'+pkg.stock.stock_status)}}</div>
              <div class="q-ma-md">{{$t('goods.view_goodslist.goods_code')}}: {{pkg.stock.goods.goods_code}}</div>
              <div class="q-ma-md">{{$t('order.view_details.need_stock_qty')}}: {{pkg.stock.stock_qty}}</div>
            </div>
          </div>
        </template>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>
<script>
export default {
  name: 'OrderStock',
  data () {
    return {}
  },
  props: {
    stock: {
      type: Object,
      require: true
    },
    packages: {
      type: Array,
      require: false
    }
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  }
}
</script>
