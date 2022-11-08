<template>
  <q-card square style="min-width: 950px" :bordered=false flat>
    <q-banner dense class="q-pa-sm text-center bg-red-7 text-white">
      <strong>SHOPEE利润计算器</strong>
    </q-banner>
    <q-separator/>
    <q-card-section class="full-width">
      <div class="row">
        <q-input dense class="col q-pa-sm" label="成本(￥)" v-model.number="calculator.price"/>
        <q-input dense class="col q-pa-sm" label="重量(KG)" v-model.number="calculator.weight"/>
        <q-input dense class="col q-pa-sm" label="数量(件)" v-model.number="calculator.number"/>
        <q-input dense class="col-3 q-pa-sm"
                 :label="`${logisticsCostsTotal ? '总境内物流(￥)' : '境内物流(￥)/每'}`"
                 v-model.number="calculator.logisticsCosts">
          <template v-slot:after>
            <q-icon class="cursor-pointer" :name="logisticsCostsTotal ? 'switch_left' : 'switch_right'" @click="logisticsCostsTotal = !logisticsCostsTotal">
              <q-tooltip>切换境内物流计算方式</q-tooltip>
            </q-icon>
          </template>
        </q-input>
        <q-input dense label="利润(￥)" class="col-2 q-pa-sm" v-model.number="netProfit" @keyup.enter="calculatePrice()">
          <template v-slot:after>
            <q-icon class="cursor-pointer" name="calculate" @click="calculatePrice()">
              <q-tooltip>根据指定利润计算价格</q-tooltip>
            </q-icon>
          </template>
        </q-input>
      </div>
      <div :key="calculate.area" v-for="calculate in calculates" class="row full-width"
           style="border-bottom: 1px solid rgba(0,0,0,0.2); background-color: rgb(247,247,247)">
        <q-input readonly dense label="地区" class="col q-pa-sm"
                 borderless v-model="calculate.area"/>
        <q-input dense :label="`售价(${calculate.currency})`" class="col q-pa-sm"
                 v-model.number="calculate.price"/>
        <q-input dense :label="`活动费率(${calculate.activity_rate*100}%)`" class="col q-pa-sm"
                 v-model.number="calculate.activity_rate"/>
        <q-input dense :label="`佣金费率(${calculate.commission_rate*100}%)`" class="col q-pa-sm"
                 v-model.number="calculate.commission_rate"/>
        <q-input dense :label="`交易费率(${calculate.transaction_rate*100}%)`" class="col q-pa-sm"
                 v-model.number="calculate.transaction_rate"/>
        <q-input dense :label="`提现费率(${calculate.withdrawal_rate*100}%)`" class="col q-pa-sm"
                 v-model.number="calculate.withdrawal_rate"/>
        <q-input dense :label="`汇损(${calculate.exchange_loss_rate*100}%)`" class="col q-pa-sm"
                 v-model.number="calculate.exchange_loss_rate"/>
        <q-input readonly dense :label="`跨境物流费(${calculate.currency})`" class="col q-pa-sm"
                 borderless :value="getLogisticsFee(calculate, calculator)"/>
        <q-input readonly dense :label="`收入(${calculate.currency})`" class="col q-pa-sm"
                 borderless :value="getIncome(calculate, calculator)"/>
        <q-input readonly dense :label="`净利润(￥)`" class="col q-pa-sm"
                 borderless :value="getNetProfit(calculate, calculator)"/>
      </div>
      <div v-if="!areaInfos" class="text-center">
        <span>未设置地区信息，请前往设置...</span>
      </div>
    </q-card-section>
    <div style="float: right; padding: 15px 15px 15px 0">
      <q-btn color="white" text-color="black" @click="submit()">{{ $t('submit') }}</q-btn>
    </div>
  </q-card>
</template>

<script>
import fetchService from 'pages/fetchbox/services/fetchservice'
import profitService from 'pages/fetchbox/services/profitservice'

export default {
  name: 'profitcalculator',
  props: {
    fetchData: Object,
    store: undefined
  },
  data () {
    return {
      areaInfos: null,
      calculates: [],
      netProfit: 0,
      logisticsCostsTotal: true,
      calculator: {
        number: 1,
        price: null,
        weight: null,
        logisticsCosts: null,
        fetchData: null
      }
    }
  },
  methods: {
    submit () {
      console.log('submit', this.calculates[0].price, this.getNetProfit(this.calculates[0], this.calculator))
      const profit = this.getNetProfit(this.calculates[0], this.calculator)
      this.$emit('ok', this.calculates[0].price, profit)
    },
    cancel () {
      console.log('cancel')
      this.$emit('cancel')
    },
    resetData (fetchData) {
      const _this = this
      _this.calculator.number = 1
      _this.calculator.fetchData = fetchData
      _this.calculator.price = fetchData.price
      _this.calculator.weight = fetchData.pack ? fetchData.pack.packWeight ? fetchData.pack.packWeight : fetchData.pack.weight ? fetchData.pack.weight : 0 : 0
      _this.calculator.logisticsCosts = fetchData.logisticsCosts
    },
    getLogisticsFee (calculateObj, calculator) {
      return profitService.getLogisticsFee(
        calculateObj, calculator.weight, calculator.number).toFixed(2)
    },
    getIncome (calculateObj, calculator) {
      return profitService.getIncome(
        calculateObj, calculateObj.price, calculator.number, calculator.weight).toFixed(2)
    },
    getNetProfit (calculateObj, calculator) {
      return profitService.getNetProfit(
        calculateObj, calculateObj.price, calculator.number,
        calculator.weight, calculator.price, this.getLogisticsCosts()).toFixed(2)
    },
    getLogisticsCosts () {
      const _this = this
      if (_this.calculator) {
        if (_this.logisticsCostsTotal) {
          return _this.calculator.logisticsCosts
        } else {
          return _this.calculator.logisticsCosts * _this.calculator.number
        }
      } else {
        return 0
      }
    },
    calculatePrice (index) {
      const _this = this
      if (index >= 0) {
        const price = profitService.getPriceByNetProfit(
          _this.calculates[index], _this.netProfit, _this.calculator.number,
          _this.calculator.price, _this.getLogisticsCosts(), _this.calculator.weight)
        if (price) {
          _this.calculates[index].price = price.toFixed(2)
        }
      } else {
        _this.calculates.forEach(calculate => {
          const price = profitService.getPriceByNetProfit(
            calculate, _this.netProfit, _this.calculator.number,
            _this.calculator.price, _this.getLogisticsCosts(), _this.calculator.weight)
          if (price) {
            calculate.price = price.toFixed(2)
          }
        })
      }
    }
  },
  created () {
    const _this = this
    fetchService.getAreaList({ store: _this.store }).then(res => {
      _this.areaInfos = res.results
      _this.resetData(_this.fetchData)
      if (_this.areaInfos) {
        _this.areaInfos.forEach(areaInfo => {
          const calculate = JSON.parse(JSON.stringify(areaInfo))
          calculate.price = 1
          _this.calculates.push(calculate)
          _this.calculatePrice(_this.calculates.length - 1)
        })
      }
    })
  }
}
</script>
