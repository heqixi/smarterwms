<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <q-table
        row-key="id"
        selection="multiple"
        :selected.sync="search_form.selected"
        class="my-sticky-header-table shadow-24"
        :data="table_list"
        :separator="separator"
        :loading="loading"
        :filter="filter"
        :columns="columns"
        hide-bottom
        :pagination.sync="pagination"
        no-data-label="No data"
        no-results-label="No data you want"
        :table-style="{ height: height }"
        flat
        bordered
      >
        <template v-slot:top>
          <div style="width: 100%">
            <q-btn-group push class="float-left">
              <q-btn :label="$t('sync')" icon="sync_alt" @click="syncProduct">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('store.view_productlist.synctip') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
            <q-space />
            <q-btn-group push class="float-right">
              <q-select color="dark" transition-show="flip-up" transition-hide="flip-down"
                        v-model="search_form.cur_shop_id"
                        :options="shop_select.options"
                        :options-dense="shop_select.denseOpts"
                        :dense="shop_select.dense"
                        :label="$t('store.label')"
                        emit-value
                        map-options>
                <template v-slot:prepend>
                  <q-icon name="img:statics/store/store.svg"/>
                </template>
              </q-select>
              <q-select color="dark" transition-show="flip-up" transition-hide="flip-down"
                        v-model="search_form.product_type" :options="product_type_select.options"
                        :options-dense="product_type_select.denseOpts"
                        :dense="product_type_select.dense"
                        emit-value
                        map-options
              ></q-select>
              <q-input dense clearable clear-icon="close" color="dark"
                       v-model="search_form.item_sku"
                       :label="$t('store.view_productlist.item_sku')"
                       @keyup.enter="getSearchList()"/>
              <q-input dense clearable clear-icon="close" color="dark"
                       v-model="search_form.item_id"
                       :label="$t('store.view_productlist.item_id')"
                       @keyup.enter="getSearchList()"/>
              <q-btn v-if="search_form.product_type === 2" dense :label="$t('more')" @click="more = !more">
                <q-icon :name="more ? 'expand_less' : 'expand_more'"/>
              </q-btn>
              <q-btn icon="search" @click="getSearchList()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('search') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
          </div>
          <div v-show="more" style="width: 100%; margin-top: .5em">
            <q-card class="no-shadow float-right">
              <q-btn-group push unelevated>
                <q-input v-if="search_form.product_type === 2" dense clearable clear-icon="close" color="dark"
                         v-model="search_form.model_id"
                         :label="$t('store.view_variant.model_id')"
                         @keyup.enter="getSearchList()"/>
                <q-input v-if="search_form.product_type === 2" dense clearable clear-icon="close" color="dark"
                         v-model="search_form.model_sku"
                         :label="$t('store.view_variant.model_sku')"
                         @keyup.enter="getSearchList()"/>
              </q-btn-group>
            </q-card>
          </div>
        </template>
        <template v-slot:body="props">
          <template v-if="search_form.product_type === 1">
            <product-row :props=props
                         :shop_id="search_form.cur_shop_id"
                         v-on:columns="initColumns"
                         v-on:refresh="reFresh"/>
          </template>
          <template v-else>
            <variant-row :props=props
                         :shop_id="search_form.cur_shop_id"
                         v-on:columns="initColumns"/>
          </template>
        </template>
      </q-table>
    </transition>
    <template>
      <div class="q-pa-lg flex flex-center">
        <span class="text-black" style="padding-right: 10px">{{$t('selected')}}: {{search_form.selected.length}}</span>
        <span class="text-black" style="padding-right: 10px">{{$t('total')}}: {{count}}</span>
        <q-btn v-show="pathname_previous" flat push color="purple" :label="$t('previous')" icon="navigate_before" @click="getListPrevious()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('previous') }}</q-tooltip>
        </q-btn>
        <span v-show="pathname_previous && pathname_next" class="text-purple" style="font-size: 14px">{{curPage}}</span>
        <q-btn v-show="pathname_next" flat push color="purple" :label="$t('next')" icon-right="navigate_next" @click="getListNext()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('next') }}</q-tooltip>
        </q-btn>
        <q-btn v-show="!pathname_previous && !pathname_next" flat push color="dark" :label="$t('no_data')"></q-btn>
        <q-select style="margin-left: 10px" dense v-model="pagination.rowsPerPage" :value="pagination.rowsPerPage" outlined  :options="pageOptions" :label="$t('row_num')"/>
      </div>
    </template>
  </div>
</template>
<router-view />

<script>
import { LocalStorage } from 'quasar'
import SyncProduct from 'pages/store/components/syncproduct'
import settings from 'pages/store/components/settings'
import productService from 'pages/store/services/productservice'
import storeService from 'pages/store/services/storeservice'
import ProductRow from 'pages/store/components/productrow'
import VariantRow from 'pages/store/components/variantrow'

export default {
  name: 'Storeproductlist',
  components: { VariantRow, ProductRow },
  data () {
    return {
      more: false,
      openid: '',
      login_name: '',
      search_form: {
        selected: [],
        product_type: null,
        cur_shop_id: null,
        item_sku: null,
        item_id: null,
        status: null,
        model_id: null,
        model_sku: null
      },
      shop_select: {
        options: [],
        dense: true,
        denseOpts: false
      },
      product_type_select: {
        options: [
          {
            label: '主产品',
            value: 1
          },
          {
            label: '变体',
            value: 2
          }
        ],
        dense: true,
        denseOpts: false
      },
      authin: '0',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      table_list: [],
      bin_size_list: [],
      bin_property_list: [],
      warehouse_list: [],
      columns: [],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      pageOptions: [10, 20, 30, 50, 100, 500],
      count: 0,
      curPage: 1
    }
  },
  methods: {
    test () {
      const _this = this
      productService.getProductByStatus({ shop_id: _this.search_form.cur_shop_id, product_status: 'DELETED' })
    },
    initColumns (columns) {
      this.columns = columns
    },
    formatType (val) {
      if (val === 1) {
        return this.$t('store.view_global.main')
      } else if (val === 2) {
        return this.$t('store.view_global.variants')
      } else {
        return val
      }
    },
    formatStatus (val) {
      return this.$t('store.product_status.' + val.toLowerCase())
    },
    setting (item) {
      const _this = this
      _this.$q.dialog({
        component: settings,
        parent: _this,
        item: item
      })
    },
    refreshProduct (itemId) {
      const _this = this;
      productService.sycnProduct({
        shop_id: _this.search_form.cur_shop_id,
        item_id: itemId
      }).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        });
        _this.reFresh();
      })
    },
    syncProduct () {
      const _this = this
      _this.$q.dialog({
        component: SyncProduct,
        parent: _this
      }).onOk(data => {
        data.shop_id = _this.search_form.cur_shop_id
        productService.sycnProduct(data).then(() => {
          _this.reFresh()
        })
      });
    },
    getSearchList () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        productService.getProductPages(_this.search_form.cur_shop_id, {
          item_sku: _this.search_form.item_sku,
          item_id: _this.search_form.item_id,
          type: _this.search_form.product_type,
          max_page: _this.pagination.rowsPerPage,
          model_id: _this.search_form.model_id,
          model_sku: _this.search_form.model_sku
        }).then(_this.resetPageData)
      }
    },
    getListPrevious () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        productService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        productService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
    },
    resetPageData (res) {
      const _this = this
      _this.table_list = res.results;
      _this.pathname_previous = res.previous;
      _this.pathname_next = res.next;
      _this.count = res.count;
      _this.curPage = res.page;
    },
    reFresh () {
      this.getSearchList();
      this.search_form.selected = [];
    }
  },
  created () {
    const _this = this;
    if (LocalStorage.has('openid')) {
      _this.openid = LocalStorage.getItem('openid');
    } else {
      _this.openid = '';
      LocalStorage.set('openid', '');
    }
    if (LocalStorage.has('login_name')) {
      _this.login_name = LocalStorage.getItem('login_name');
    } else {
      _this.login_name = '';
      LocalStorage.set('login_name', '');
    }
    if (LocalStorage.has('auth')) {
      _this.authin = '1';
      _this.search_form.product_type = _this.product_type_select.options[0].value;
      storeService.getStoreList().then(stores => {
        const options = [stores.length];
        for (const i in stores) {
          const store = stores[i]
          options[i] = {
            label: store.name + '(' + store.area + ')',
            value: store.uid
          }
        }
        _this.search_form.cur_shop_id = options[0].value;
        _this.shop_select.options = options;
      }).finally(() => {
        _this.getSearchList()
      })
    } else {
      _this.authin = '0';
    }
  },
  watch: {
    'pagination.rowsPerPage': {
      handler (n, o) {
        this.getSearchList()
      }
    },
    'search_form.cur_shop_id': {
      handler (n, o) {
        if (n) {
          this.getSearchList()
        }
      }
    },
    'search_form.product_type': {
      handler (n, o) {
        if (this.search_form.cur_shop_id) {
          this.getSearchList()
        }
      }
    }
  },
  mounted () {
    const _this = this;
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + 'px';
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px';
    }
  },
  updated () {},
  destroyed () {}
};
</script>
