<template>
  <q-card>
    <q-banner inline-actions class="text-white bg-blue-5">供应商信息 </q-banner>
    <q-card-section>
      <div class="row justify-start">
        <div class="col-9">
          <q-input
            dense
            v-model="supplierInfo.url.value"
            label="链接"
            :rules="[val => (val && val.length > 0) || error1]"
            @blur="save('url')">
            <template v-slot:before class="q-mb-sm">
              <span v-if="supplierInfo.url.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{supplierInfo.url.label}}
              </div>
            </template>
          </q-input>
        </div>
      </div>
      <div class="row justify-start">
        <div class="col-3">
          <q-input
            dense
            v-model="supplierInfo.logistics_costs.value"
            @blur="save('logistics_costs')">
            <template v-slot:before class="q-mb-sm">
              <span v-if="supplierInfo.logistics_costs.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{supplierInfo.logistics_costs.label}}
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-3 q-pl-lg">
          <q-input
            dense
            v-model="supplierInfo.min_purchase_num.value"
            @blur="save('min_purchase_num')">
            <template v-slot:before class="q-mb-sm">
              <span v-if="supplierInfo.min_purchase_num.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{supplierInfo.min_purchase_num.label}}
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-3 q-pl-lg">
          <q-input
            dense
            v-model="supplierInfo.delivery_days.value"
            @blur="save('delivery_days')">
            <template v-slot:before class="q-mb-sm">
              <span v-if="supplierInfo.min_purchase_num.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{supplierInfo.delivery_days.label}}
              </div>
            </template>
          </q-input>
        </div>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
export default {
  name: 'GoodsSupplierInfo',
  data () {
    return {
      supplierInfo: {
        url: {
          value: '',
          require: true,
          label: '商品源'
        },
        logistics_costs: {
          value: '',
          require: false,
          label: '物流费用'
        },
        min_purchase_num: {
          value: '',
          require: false,
          label: '起批量'
        },
        delivery_days: {
          value: '',
          require: false,
          label: '物流天数'
        }
      },
      error1: '请出入商品源链接'
    }
  },
  created () {
    if (this.supplier) {
      this.supplierInfo.url.value = this.supplier.url
      this.supplierInfo.logistics_costs.value = this.supplier.logistics_costs
      this.supplierInfo.min_purchase_num.value = this.supplier.min_purchase_num
      this.supplierInfo.delivery_days.value = this.supplier.delivery_days
    }
  },
  props: ['supplier'],
  methods: {
    save (field) {
      if (field === 'url') {
        this.$emit('onChange', this.supplierInfo.url.value, 'url')
      }
      if (field === 'logistics_costs') {
        this.$emit('onChange', this.supplierInfo.logistics_costs.value, 'logistics_costs')
      }
      if (field === 'min_purchase_num') {
        this.$emit('onChange', this.supplierInfo.min_purchase_num.value, 'min_purchase_num')
      }
      if (field === 'delivery_days') {
        this.$emit('onChange', this.supplierInfo.delivery_days.value, 'delivery_days')
      }
    }
  }
}
</script>
