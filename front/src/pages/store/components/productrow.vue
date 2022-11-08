<template>
  <q-tr :props="props">
    <q-td auto-width>
      <q-checkbox dense v-model="props.selected" color="grey-8" keep-color/>
    </q-td>
    <q-td :props="props" v-for="col in columns" :key="col.name">
      <template v-if="col.name === 'action'">
        <q-btn-group unelevated>
          <q-btn round flat push color="dark" icon="edit_note" @click="edit(props.row)">
            <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('edit') }}</q-tooltip>
          </q-btn>
          <q-btn round flat push color="dark" icon="sync_alt" @click="refreshProduct(props.row['product_id'])">
            <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('sync') }}</q-tooltip>
          </q-btn>
        </q-btn-group>
      </template>
      <template v-else-if="col.name === 'image_url'">
        <q-img :src="props.row[col.name]" :ratio="1"></q-img>
      </template>
      <template v-else-if="col.name === 'product_name'">
        <q-input borderless :value="props.row[col.name]" readonly>
          <q-tooltip :offset="[10, 10]" content-style="font-size: 12px">{{props.row[col.name]}}</q-tooltip>
        </q-input>
      </template>
      <template v-else-if="col.name === 'product_status'">
        {{formatStatus(props.row[col.name])}}
      </template>
      <template v-else>
        {{props.row[col.name]}}
      </template>
    </q-td>
  </q-tr>
</template>

<script>
import GlobalProductView from 'pages/store/components/globalproductview'
import globalProductService from 'pages/store/services/globalproductservice'
import productService from 'pages/store/services/productservice'

export default {
  name: 'ProductRow',
  props: {
    props: Object,
    merchant_id: String,
    shop_id: String
  },
  data () {
    const columns = []
    if (this.shop_id) {
      columns.push({ name: 'global_item_id', label: this.$t('store.view_global.global_item_id'), align: 'left', field: 'global_item_id' })
    }
    columns.push({ name: 'product_id', label: this.shop_id ? this.$t('store.view_productlist.item_id') : this.$t('store.view_global.global_item_id'), align: 'left', field: 'product_id' })
    columns.push({ name: 'product_name', label: this.shop_id ? this.$t('store.view_productlist.name') : this.$t('store.view_global.global_item_name'), align: 'left', field: 'product_name' })
    columns.push({ name: 'product_sku', label: this.shop_id ? this.$t('store.view_productlist.item_sku') : this.$t('store.view_global.global_item_sku'), align: 'left', field: 'product_sku' })
    columns.push({ name: 'image_url', label: this.$t('store.view_productlist.product_image'), align: 'left', field: 'image_url' })
    if (this.shop_id) {
      columns.push({ name: 'product_status', label: this.$t('store.view_productlist.item_status'), align: 'left', field: 'product_status' })
    }
    columns.push({ name: 'create_time', label: this.$t('createdtime'), align: 'left', field: 'create_time' })
    columns.push({ name: 'update_time', label: this.$t('updatedtime'), align: 'left', field: 'update_time' })
    columns.push({ name: 'action', label: this.$t('action'), align: 'center' })

    return {
      columns
    }
  },
  methods: {
    formatStatus (val) {
      return this.$t('store.product_status.' + val.toLowerCase())
    },
    edit (data) {
      const _this = this
      if (_this.shop_id) {
        // TODO
      } else {
        _this.$q.dialog({
          component: GlobalProductView,
          parent: _this,
          merchantId: _this.merchant_id,
          id: data.id
        })
      }
    },
    refreshProduct (itemId) {
      const _this = this
      if (_this.shop_id) {
        productService.sycnProduct({
          shop_id: _this.shop_id,
          item_id: itemId
        }).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          })
          _this.$emit('refresh')
        })
      } else {
        globalProductService.sycnGlobalProduct({
          merchant_id: _this.merchant_id,
          item_id: itemId
        }).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          })
          _this.$emit('refresh')
        })
      }
    }
  },
  created () {
    this.$emit('columns', this.columns)
  }
}
</script>
