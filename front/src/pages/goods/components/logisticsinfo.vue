<template>
  <q-card>
    <q-banner inline-actions class="text-white bg-blue-5">物流信息</q-banner>
    <q-card-section>
      <div class="row justify-start">
        <div class="col-2">
          <q-input
            dense
            square
            v-model.number="logistic.weight"
            type="number"
            :rules="[val => (val && val > 0) || error5]">
            <template v-slot:before class="q-mb-sm">
              <span v-if="goodsLogisticsInfo.weight.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{goodsLogisticsInfo.weight.label}}
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-2 q-ml-md">
          <q-input
            dense
            square
            v-model.number="logistic.product_d"
            type="number"
            :rules="[val => (val && val > 0) || error6]"
            @blur="saveProductD">
            <template v-slot:before class="q-mb-sm">
              <span v-if="goodsLogisticsInfo.dimension.require" :style="{color:'red', fontSize:'8px'}"> * </span>
              <div class="text-body2">
                {{goodsLogisticsInfo.dimension.label}}
              </div>
            </template>
            <template v-slot:append class="q-mb-sm">
              <div class="text-body2">
                长
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-2 q-ml-lg">
          <q-input
            dense
            square
            v-model.number="logistic.product_w"
            type="number"
            :rules="[val => (val && val > 0) || error7]"
            @blur="saveProductW()">
            <template v-slot:append class="q-mb-sm">
              <div class="text-body2">
                宽
              </div>
            </template>
          </q-input>
        </div>
        <div class="col-2 q-ml-lg">
          <q-input
            dense
            square
            v-model.number="logistic.product_h"
            type="number"
            :rules="[val => (val && val > 0) || error7]"
            @blur="saveProductH()">
            <template v-slot:append class="q-mb-sm">
              <div class="text-body2">
                高
              </div>
            </template>
          </q-input>
        </div>
      </div>
      <div class="row justify-start" >
        <q-input
          dense
          square
          v-model.number="logistic.days_deliver"
          type="number"
          :rules="[val => (val && val > 0) || error5]"
          @blur="saveDayDeliver()">
          <template v-slot:before class="q-mb-sm">
            <span v-if="goodsLogisticsInfo.daysDeliver.require" :style="{color:'red', fontSize:'8px'}"> * </span>
            <div class="text-body2">
              {{goodsLogisticsInfo.daysDeliver.label}}
            </div>
          </template>
          <template v-slot:after class="q-mb-sm">
            <div class="text-body2">
              {{goodsLogisticsInfo.daysDeliver.tip}}
            </div>
          </template>
        </q-input>
      </div>
    </q-card-section>
  </q-card>
</template>

<script>
export default {
  name: 'LogisticsInfo',
  data () {
    return {
      goodsLogisticsInfo: {
        dimension: {
          product_w: 0,
          product_h: 0,
          product_d: 0,
          require: true,
          label: '商品尺寸(cm)'
        },
        weight: {
          value: 0,
          unit: 'KG',
          require: true,
          label: '商品重量'
        },
        daysDeliver: {
          value: 3,
          require: true,
          label: '发货时间',
          tip: '默认发货时长3天。自定义发货时长5~10天(跨境店铺) / 7~30天(本地店铺)'
        }
      },
      error4: this.$t('goods.view_goodslist.error4'),
      error8: this.$t('goods.view_unit.error1'),
      error12: this.$t('goods.view_shape.error1'),
      error11: this.$t('goods.view_color.error1'),
      error7: this.$t('goods.view_goodslist.error7'),
      error6: this.$t('goods.view_goodslist.error6'),
      error5: this.$t('goods.view_goodslist.error5')
    }
  },
  props: ['logistic'],
  methods: {
    // saveWeight () {
    //   this.onChange(this.goodsLogisticsInfo.weight.value, 'weight')
    // },
    saveProductW () {
      this.onChange(this.goodsLogisticsInfo.dimension.product_w, 'product_w')
    },
    saveProductD () {
      this.onChange(this.goodsLogisticsInfo.dimension.product_d, 'product_d')
    },
    saveProductH () {
      this.onChange(this.goodsLogisticsInfo.dimension.product_h, 'product_h')
    },
    saveDayDeliver () {
      this.onChange(this.goodsLogisticsInfo.daysDeliver.value, 'days_deliver')
    },
    onChange (value, field) {
      this.$emit('onChange', value, field)
    }
  },
  created () {
    this.goodsLogisticsInfo.dimension.product_w = this.logistic.product_w || ''
    this.goodsLogisticsInfo.dimension.product_h = this.logistic.product_h || ''
    this.goodsLogisticsInfo.dimension.product_d = this.logistic.product_d || ''
    this.goodsLogisticsInfo.weight.value = this.logistic.weight || ''
    this.goodsLogisticsInfo.daysDeliver.value = this.logistic.days_deliver || ''
  }
}
</script>
