<template>
  <q-dialog ref="dialog" full-width :no-backdrop-dismiss="true">
    <q-card>
      <q-card-section>
        <product-properties :options="propertiesOptions"></product-properties>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide()"></q-btn>
        <q-btn :label="$t('submit')" @click="submit()" color="primary" text-color="white"></q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script>
import globalProductService from 'pages/store/services/globalproductservice'
import ProductProperties from 'pages/store/components/productproperties'
export default {
  name: 'GlobalProdcutView',
  components: { ProductProperties },
  data () {
    return {
      propertiesOptions: {
        merchantId: null,
        categoryId: null,
        attributeList: [],
      },
      itemData: {}
    }
  },
  props: {
    merchantId: {
      type: String,
      require: true
    },
    id: {
      type: Number,
      require: false
    }
  },
  methods: {
    submit () {
      const _this = this
      _this.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  },
  mounted () {
    const _this = this;
    if (_this.id && _this.merchantId) {
      globalProductService.getGlobalProductInfo(_this.merchantId, _this.id)
        .then(itemData => {
          _this.itemData = itemData
          _this.propertiesOptions.merchantId = _this.merchantId
          _this.propertiesOptions.attributeList = _this.itemData.attribute_list
          _this.propertiesOptions.categoryId = _this.itemData.category_id;
          _this.propertiesOptions.brand = _this.itemData.brand;
        })
    }
  }
}
</script>
