<template>
  <q-dialog ref="dialog" no-backdrop-dismiss>
    <q-layout view="hHh lpr fFf" container class="full-width bg-white">
      <q-header elevated class="bg-white text-black">
        <q-toolbar>
          <q-toolbar-title>
            {{ $t('store.view_global.batch_edit_global_sku') }}
            <q-btn-group class="float-right" push unelevated>
              <q-input dense v-model="globalSku" :label="$t('store.view_global.global_item_sku')" style="margin-right: 5px"/>
              <q-btn dense :label="$t('settings')" @click="setting"/>
            </q-btn-group>
          </q-toolbar-title>
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page padding class="q-pa-md full-width">
          <div class="row scroll-y" style='padding: 5px 0' :key="model.id" v-for="model in updateGlobalList">
            <q-img class="col-4" :src="model.image_url" ratio="1"/>
            <div class="col-8" style="padding-left: 10px">
              <q-input readonly :value="model.product_id" :label="$t('store.view_global.global_item_id')"/>
              <q-input readonly :value="model.product_name" :label="$t('store.view_global.global_item_name')"/>
              <q-input v-model="model.product_sku" :value="model.product_sku" :label="$t('store.view_global.global_item_sku')"/>
            </div>
          </div>
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
export default {
  name: 'UpdateGlobalSku',
  data () {
    return {
      globalSku: '',
      updateGlobalList: []
    }
  },
  props: {
    globalList: {
      type: Array,
      require: true
    }
  },
  methods: {
    hide () {
      this.$refs.dialog.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    submit () {
      this.$emit('ok', this.updateGlobalList)
      this.hide()
    },
    setting () {
      const _this = this
      console.log('_this.globalSku', _this.globalSku)
      this.updateGlobalList.forEach(model => {
        model.product_sku = _this.globalSku
      })
    }
  },
  created () {
    this.updateGlobalList = JSON.parse(JSON.stringify(this.globalList))
  }
}
</script>
