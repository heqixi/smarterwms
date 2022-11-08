<template>
  <q-card class="q-pa-md">
    <q-card-section>
      <q-banner rounded dense class="bg-white">
        <template v-slot:avatar>
          商品属性
        </template>
      </q-banner>
      <q-separator/>
      <q-list separator>
        <q-item>
          <q-item-section>
            <q-select :label="$t('store.brand')" v-model="selected.brand"
                      :options="filterBrandOptions"
                      use-input
                      option-value="brand_id"
                      option-label="display_brand_name"
                      @filter="filterFn"
            />
          </q-item-section>
          <q-item-section>
            类目：{{options.categoryId ? options.categoryId : ''}}
          </q-item-section>
        </q-item>
      </q-list>
      <q-list separator>
        <q-item :key="`Group-${i}`" v-for="(group, i) in attributeGroups">
          <q-item-section :key="`attr-${attr.attribute_id}`" v-for="(attr) in group">
            <template v-if="attr.input_type === 'TEXT_FILED'">
              <q-input v-model="attributes[attr.attribute_id]" :label="attr.display_attribute_name"/>
            </template>
            <template v-else>
              <q-select :multiple="attr.input_type === 'MULTIPLE_SELECT_COMBO_BOX'"
                        v-model="attributes[attr.attribute_id]"
                        :options="attr.attribute_value_list"
                        option-value="attribute_id"
                        option-label="display_value_name"
                        :label="attr.display_attribute_name">
                <template v-slot:before>
                  <span v-if="attr.is_mandatory" class="text-red-4" style="font-size: 20px">*</span>
                </template>
                <template v-slot:option="scope">
                  <q-item v-bind="scope.itemProps"
                          v-on="scope.itemEvents">
                    <q-item-section>
                      <q-item-label caption>
                        {{scope.opt.display_value_name}}{{scope.opt.value_unit ? '(' + scope.opt.value_unit + ')': ''}}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </template>
              </q-select>
            </template>
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
  </q-card>
</template>
<script>
import { LocalStorage } from 'quasar'
import globalProductService from 'pages/store/services/globalproductservice'

export default {
  name: 'ProductProperties',
  MERCHANT: 1,
  SHOP: 2,
  data () {
    return {
      selected: {
        brand: null,
        category: null
      },
      attributes: {},
      attributeGroups: [],
      brandOptions: [],
      filterBrandOptions: []
    }
  },
  props: {
    /**
     * options: {
     *   merchantId: Number,
     *   shopId: Number,
     *   categoryId: Number,
     *   brand: Object,
     *   attributeList: Array
     * }
     */
    options: {
      type: Object,
      require: true
    }
  },
  watch: {
    'options.merchantId': {
      handler (n, o) {
        // TODO
      }
    },
    'options.categoryId': {
      handler (n, o) {
        this.refreshBrands()
        this.refreshAttributes()
      }
    },
    'options.attributeList': {
      handler (n, o) {
        if (n) {
          console.log('options.attributeList', n)
        }
      }
    }
  },
  methods: {
    filterFn (val, update) {
      if (val === '') {
        const _this = this
        update(() => {
          if (_this.brandOptions && _this.brandOptions.length > 0) {
            const needle = val.toLowerCase()
            console.log('needle', needle)
            // _this.filterBrandOptions = _this.brandOptions.filter(v => v.toLowerCase().indexOf(needle) > -1)
          }
        })
      }
    },
    refreshBrands () {
      const _this = this
      if (_this.options.merchantId && _this.options.categoryId) {
        globalProductService.getGlobalBrands(
          _this.options.merchantId, _this.options.categoryId, _this.options.language
        ).then(res => {
          _this.brandOptions = res
        })
      }
    },
    refreshAttributes () {
      const _this = this
      if (_this.options.merchantId && _this.options.categoryId) {
        globalProductService.getGlobalAttributeList(
          _this.options.merchantId, _this.options.categoryId, _this.options.language
        ).then(res => {
          const groupLimit = 3
          let index = -1
          res.sort((a, b) => { return a.attribute_id - b.attribute_id })
          for (let i = 0; i < res.length; i++) {
            if (res[i]) {
              if (i % groupLimit === 0) {
                _this.attributeGroups[++index] = []
              }
              _this.attributeGroups[index].push(res[i])
            }
          }
          console.log('_this.attributeGroups', _this.attributeGroups);
          _this.$forceUpdate()
        })
      }
    }
  },
  created () {
    if (LocalStorage.has('auth')) {
      const _this = this
      const lang = LocalStorage.getItem('lang')
      const language = (lang.toLowerCase() === 'zh-hant' || lang.toLowerCase() === 'zh-hans') ? lang : 'en'
      _this.options.language = _this.options.language ? _this.options.language : language
    }
  }
}
</script>
