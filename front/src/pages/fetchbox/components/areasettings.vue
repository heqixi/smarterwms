<style>
.after-font-size {
  font-size: 0.6em;
}
</style>
<template>
  <q-dialog ref="dialog" no-backdrop-dismiss>
    <q-card>
      <q-card-section>
        <q-banner rounded dense class="bg-white">
          <template v-slot:default>
            <span>{{$t('fetch.view_areasettings.base_info')}}</span>
            <a class="after-font-size" style="float: right" href="https://shopee.cn/edu/article/5091" target="_blank">跨境物流成本（藏价）与物流运费一览</a>
          </template>
        </q-banner>
        <q-separator/>
        <div class="row">
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.area')" v-model="form_data.area">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.short_area')" v-model="form_data.short_area">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.currency')" v-model.number="form_data.currency">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
        </div>
        <div class="row">
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.exchange_rate')"
                   v-model="form_data.exchange_rate"
                   @change="checkNumber('exchange_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="`${$t('fetch.view_areasettings.activity_rate')}(${(form_data.activity_rate*100).toFixed(2)}%)`"
                   v-model="form_data.activity_rate"
                   @change="checkNumber('activity_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
        </div>
        <div class="row">
          <q-input dense class="col q-px-xs" :label="`${$t('fetch.view_areasettings.commission_rate')}(${(form_data.commission_rate*100).toFixed(2)}%)`"
                   v-model.number="form_data.commission_rate"
                   @change="checkNumber('commission_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="`${$t('fetch.view_areasettings.transaction_rate')}(${(form_data.transaction_rate*100).toFixed(2)}%)`"
                   v-model.number="form_data.transaction_rate"
                   @change="checkNumber('transaction_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
        </div>
        <div class="row">
          <q-input dense class="col q-px-xs" :label="`${$t('fetch.view_areasettings.withdrawal_rate')}(${(form_data.withdrawal_rate*100).toFixed(2)}%)`"
                   v-model.number="form_data.withdrawal_rate"
                   @change="checkNumber('withdrawal_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="`${$t('fetch.view_areasettings.exchange_loss_rate')}(${(form_data.exchange_loss_rate*100).toFixed(2)}%)`"
                   v-model.number="form_data.exchange_loss_rate"
                   @change="checkNumber('exchange_loss_rate')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
          </q-input>
        </div>
        <div class="row">
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.buyer_shipping')"
                   v-model.number="form_data.buyer_shipping"
                   @change="checkNumber('buyer_shipping')">
            <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
            <template v-slot:append><span class="after-font-size">{{form_data.currency}}</span></template>
          </q-input>
          <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.other_fee')"
                   v-model.number="form_data.other_fee"
                   @change="checkNumber('other_fee')">
            <template v-slot:append><span class="after-font-size">￥</span></template>
          </q-input>
        </div>
      </q-card-section>
      <q-separator/>
      <q-card-section>
        <q-banner rounded dense class="bg-white">
          <template v-slot:default>
            <div class="full-width" style="display: table">
              <span style="display: table-cell; vertical-align: middle;">{{$t('fetch.view_areasettings.logistics_range')}}</span>
              <q-btn class="float-right" dense icon="add" :label="$t('new')" @click="newArea"/>
            </div>
          </template>
        </q-banner>
        <q-separator/>
        <div class="row q-my-sm" :key="i" v-for="(calc, i) in form_data.logistics_calc_list">
          <div class="col-11 row">
            <q-input dense class="col q-px-xs" readonly :label="$t('fetch.view_areasettings.min_weight')" v-model.number="calc.min_weight">
              <template v-slot:append><span class="after-font-size">KG</span></template>
            </q-input>
            <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.max_weight')" v-model.number="calc.max_weight" @change="checkMaxWeight(calc, i)">
              <template v-slot:append><span class="after-font-size">KG</span></template>
            </q-input>
            <q-input v-if="calc.calc_type === 2" dense class="col q-px-xs" :label="`${calc.logistics_fee?calc.logistics_fee:0}${form_data.currency}/${calc.interval?calc.interval:0}KG`"
                     v-model.number="calc.interval" @change="checkIntervalWeight(calc)">
              <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
              <template v-slot:append><span class="after-font-size">KG</span></template>
            </q-input>
            <q-input dense class="col q-px-xs" :label="$t('fetch.view_areasettings.logistics_fee')" v-model.number="calc.logistics_fee" @change="checkLogisticsFee(calc, i)">
              <template v-slot:before><span class="text-red-9 text-weight-bold">*</span></template>
              <template v-slot:append><span class="after-font-size">{{form_data.currency}}</span></template>
            </q-input>
            <q-select dense map-options color="dark" transition-show="flip-up" transition-hide="flip-down"
                      :label="$t('fetch.view_areasettings.calc_type')"
                      v-model="calc.calc_type" emit-value
                      :options="calc_options"/>
          </div>
          <div class="col-1 q-px-xs text-center">
            <q-btn class="float-right" dense icon="delete" @click="removeArea(calc, i)"/>
          </div>
        </div>
      </q-card-section>
      <q-separator/>
      <q-card-section>
        <q-banner rounded dense class="bg-white">
          <template v-slot:default>
            <div class="full-width" style="display: table">
              <span style="display: table-cell; vertical-align: middle;">适用店铺</span>
            </div>
          </template>
        </q-banner>
        <q-option-group
          name="accepted_genres"
          v-model="form_data.stores"
          :options="allStoresWithoutSettings"
          type="checkbox"
          inline/>
      </q-card-section>
      <q-card-actions align="right">
        <span class="after-font-size">
          如何验证？
          <q-tooltip>
            前往 Shopee企业微信 / 工作台 / 定价模拟器
          </q-tooltip>
        </span>
        <q-btn :label="$t('index.cancel')" @click="hide"></q-btn>
        <q-btn :label="$t('index.submit')" color="primary" text-color="white" @click="submit"></q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script>

import { getauth } from 'boot/axios_request'

export default {
  name: 'AreaSettings',
  data () {
    return {
      form_data: {
        id: null,
        area: null,
        short_area: null,
        currency: null,
        exchange_rate: null,
        activity_rate: null,
        commission_rate: null,
        transaction_rate: null,
        withdrawal_rate: null,
        exchange_loss_rate: null,
        buyer_shipping: null,
        other_fee: 0,
        logistics_calc_list: [],
        stores: []
      },
      allStoresWithoutSettings: [],
      calc_options: [
        {
          label: this.$t('fetch.view_areasettings.fixed'),
          value: 1
        }, {
          label: this.$t('fetch.view_areasettings.stage'),
          value: 2
        }
      ]
    }
  },
  props: {
    settings: Object
  },
  methods: {
    getAllStore () {
      var _this = this
      getauth('store/all?type=2&profit_settings=true', {}).then(stores => {
        console.log('get all store ', stores)
        stores.forEach((store) => {
          if ((_this.settings && store.profit_setting && store.profit_setting.id === _this.settings.id) ||
              !store.profit_setting) {
            _this.allStoresWithoutSettings.push({
              label: store.name,
              value: store.uid
            })
          }
        })
      })
    },
    checkIntervalWeight (calc) {
      if (isNaN(Number(calc.interval)) || Number(calc.interval) <= 0) {
        this.$q.notify({
          message: 'Please fill in the numbers and must be > 0',
          icon: 'close',
          color: 'negative'
        })
        calc.interval = 0.01
        return false
      }
      return true
    },
    checkFormData () {
      const _this = this
      if (_this.form_data.area &&
          _this.form_data.short_area &&
          _this.form_data.currency &&
          _this.checkNumber('exchange_rate') &&
          _this.checkNumber('activity_rate') &&
          _this.checkNumber('commission_rate') &&
          _this.checkNumber('transaction_rate') &&
          _this.checkNumber('withdrawal_rate') &&
          _this.checkNumber('exchange_loss_rate') &&
          _this.checkNumber('buyer_shipping') &&
          _this.checkNumber('other_fee')
      ) {
        return true
      }
      this.$q.notify({
        message: 'Params Error',
        icon: 'close',
        color: 'negative'
      })
      return false
    },
    checkNumber (key) {
      if (isNaN(Number(this.form_data[key]))) {
        this.$q.notify({
          message: 'Please fill in the numbers',
          icon: 'close',
          color: 'negative'
        })
        this.form_data[key] = 0
        return false
      }
      return true
    },
    checkLogisticsFee (calc, i) {
      const _this = this
      if (calc.logistics_fee <= 0) {
        _this.$q.notify({
          message: 'Logistics Fee must be > 0',
          icon: 'close',
          color: 'negative'
        })
      }
    },
    checkMaxWeight (calc, i) {
      const _this = this
      const nextCalc = _this.form_data.logistics_calc_list[i + 1]
      if (nextCalc && nextCalc.min_weight !== calc.max_weight) {
        nextCalc.min_weight = calc.max_weight
      }
      if (calc.max_weight && calc.max_weight < calc.min_weight) {
        _this.$q.notify({
          message: 'Max Weight must be > Min Weight',
          icon: 'close',
          color: 'negative'
        })
        calc.max_weight = calc.min_weight
      }
    },
    removeArea (calc, i) {
      this.form_data.logistics_calc_list.splice(i, 1)
    },
    newArea () {
      let minWeight = 0
      const _this = this
      const len = _this.form_data.logistics_calc_list.length
      if (len > 0) {
        minWeight = _this.form_data.logistics_calc_list[len - 1].max_weight
        const logisticsFee = _this.form_data.logistics_calc_list[len - 1].logistics_fee
        if (!minWeight || !logisticsFee) {
          _this.$q.notify({
            message: 'Please enter max weight and logistics fee',
            icon: 'close',
            color: 'negative'
          })
          return
        }
      }
      _this.form_data.logistics_calc_list.push({
        min_weight: minWeight,
        max_weight: null,
        calc_type: len ? _this.calc_options[1].value : _this.calc_options[0].value,
        logistics_fee: null
      })
    },
    submit () {
      const _this = this
      if (_this.checkFormData()) {
        console.log('summit data ', _this.form_data.stores.map(store => { return store.uid }))
        _this.$emit('ok', {
          id: _this.form_data.id,
          area: _this.form_data.area,
          short_area: _this.form_data.short_area,
          currency: _this.form_data.currency,
          exchange_rate: _this.form_data.exchange_rate,
          activity_rate: _this.form_data.activity_rate,
          commission_rate: _this.form_data.commission_rate,
          transaction_rate: _this.form_data.transaction_rate,
          withdrawal_rate: _this.form_data.withdrawal_rate,
          exchange_loss_rate: _this.form_data.exchange_loss_rate,
          buyer_shipping: _this.form_data.buyer_shipping,
          other_fee: _this.form_data.other_fee,
          logistics_calc_list: _this.form_data.logistics_calc_list,
          stores: _this.form_data.stores
        })
        this.hide()
      }
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  },
  created () {
    const _this = this
    if (_this.settings) {
      console.log('this. setting ', _this.settings)
      _this.form_data = JSON.parse(JSON.stringify(_this.settings))
    }
    this.getAllStore()
  }
}
</script>
