<template>
  <q-dialog ref="dialog" full-width>
    <q-layout view="hHh lpr fFf" container class="bg-white full-height">
      <q-header elevated class="bg-white text-black">
        <q-toolbar>
          <q-toolbar-title>
            {{ $t('order.view_orderrecord.order_record') }}
          </q-toolbar-title>
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page padding class="q-pa-md full-width">
          <global-prodcut-view ref="product"></global-prodcut-view>
        </q-page>
      </q-page-container>
      <q-footer elevated class="bg-white text-black text-right" style="padding: 5px">
        <q-btn :label="$t('cancel')" @click="hide()"/>
        <q-btn :label="$t('submit')" @click="submit()" color="primary" text-color="white"/>
      </q-footer>
    </q-layout>
  </q-dialog>
</template>

<script>
import GlobalProdcutView from 'pages/store/globalproductlist'
export default {
  name: 'ProductDialog',
  components: { GlobalProdcutView },
  data () {
    return {}
  },
  methods: {
    submit () {
      const _this = this
      _this.$emit('ok', _this.$refs.product.search_form.selected)
      this.hide()
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
