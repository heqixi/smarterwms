<template>
  <q-tr :props="props">
    <q-td auto-width>
      <q-checkbox v-model="props.selected" color="grey-8" keep-color/>
    </q-td>
    <q-td :props="props" v-for="col in columns" :key="col.name">
      <template v-if="col.name === 'action'">
        <q-btn-group unelevated>
          <q-btn round flat push color="dark" icon="edit_note" @click="updateSku(props.row)">
            <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('edit') }}</q-tooltip>
          </q-btn>
        </q-btn-group>
      </template>
      <template v-else-if="col.name === 'product_name'">
        <q-input borderless :value="props.row[col.name]" readonly>
          <q-tooltip :offset="[10, 10]" content-style="font-size: 12px">{{props.row[col.name]}}</q-tooltip>
        </q-input>
      </template>
      <template v-else-if="col.name === 'image'">
        <q-img :src="props.row[col.name]" :ratio="1"></q-img>
      </template>
      <template v-else>
        {{props.row[col.name]}}
      </template>
    </q-td>
  </q-tr>
</template>

<script>
export default {
  name: 'VariantRow',
  props: {
    props: Object,
    merchant_id: String,
    shop_id: String
  },
  data () {
    const columns = [
      { name: 'product_id', required: true, label: this.shop_id ? this.$t('store.view_productlist.item_id') : this.$t('store.view_global.global_item_id'), align: 'left', field: 'product_id' },
      { name: 'product_name', required: true, label: this.shop_id ? this.$t('store.view_productlist.name') : this.$t('store.view_global.global_item_name'), align: 'left', field: 'product_name' },
      { name: 'product_sku', required: true, label: this.shop_id ? this.$t('store.view_productlist.item_sku') : this.$t('store.view_global.global_item_sku'), align: 'left', field: 'product_sku' },
      { name: 'image', required: true, label: this.$t('store.view_productlist.product_image'), align: 'left', field: 'image' },
      { name: 'model_id', required: true, label: this.$t('store.view_variant.model_id'), align: 'left', field: 'model_id' },
      { name: 'model_sku', required: true, label: this.$t('store.view_variant.model_sku'), align: 'left', field: 'model_sku' },
      { name: 'action', label: this.$t('action'), align: 'center' }
    ]
    return {
      columns
    }
  },
  methods: {
    updateSku (row) {
      // TODO 编辑SKU
    }
  },
  created () {
    this.$emit('columns', this.columns)
  }
}
</script>
