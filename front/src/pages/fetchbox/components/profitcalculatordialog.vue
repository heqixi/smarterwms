<template>
  <q-dialog ref="calcDialog">
    <profit-calculator
      :fetch-data="coverFetchData"
      :store="store"
      @ok="onOk"
    />
  </q-dialog>
</template>

<script>
import ProfitCalculator from './profitcalculator.vue'
export default {
  name: 'ProfitCalculatorDialog',
  components: { ProfitCalculator },
  props: {
    fetchData: Object,
    data: Object,
    store: undefined
  },
  data () {
    return {
      coverFetchData: null
    }
  },
  methods: {
    show () {
      this.$refs.calcDialog.show()
    },
    hide () {
      this.$refs.calcDialog.hide()
    },
    onOk (price, profit) {
      console.log('on dialog inner ok ', price, profit)
      this.$emit('ok', { price: price, profit: profit })
      this.hide()
    }
  },
  created () {
    const _this = this
    if (_this.fetchData) {
      _this.coverFetchData = JSON.parse(JSON.stringify(_this.fetchData))
    } else if (_this.data) {
      _this.coverFetchData = {
        logisticsCosts: _this.data.logistics_costs,
        price: _this.data.price,
        pack: { weight: _this.data.weight }
      }
    }
  }
}
</script>

