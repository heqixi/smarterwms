<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <q-table
          selection="multiple"
          :selected.sync="search_form.selected"
          class="my-sticky-header-table shadow-24"
          :data="table_list"
          row-key="id"
          :separator="separator"
          :loading="loading"
          :filter="search_form.orderSn"
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
          <q-btn-group push>
            <q-btn :label="$t('order.view_message.readed')" icon="done" @click="readed()">
              <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('newtip') }}</q-tooltip>
            </q-btn>
            <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
              <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
            </q-btn>
          </q-btn-group>
          <q-space />
          <q-btn-group push>
            <q-select dense color="dark" transition-show="flip-up" transition-hide="flip-down"
                      v-model="search_form.cur_shop_id"
                      :options="shop_select.options"
                      :label="$t('store.label')"
                      emit-value
                      map-options>
              <template v-slot:prepend>
                <q-icon name="img:statics/store/store.svg"/>
              </template>
            </q-select>
            <q-input outlined rounded dense debounce="300" color="primary" v-model="search_form.orderSn" :placeholder="$t('search')" @blur="getSearchList()" @keyup.enter="getSearchList()">
              <template v-slot:append>
                <q-icon name="search" @click="getSearchList()" />
              </template>
            </q-input>
          </q-btn-group>
        </template>
      </q-table>
    </transition>
  </div>
</template>
<script>
import { LocalStorage } from 'quasar'
import orderMessageService from 'pages/order/services/ordermessageservice'
import storeService from 'pages/store/services/storeservice'

export default {
  name: 'OrderMessage',
  data () {
    return {
      search_form: {
        selected: [],
        orderSn: ''
      },
      shop_select: [],
      openid: '',
      login_name: '',
      authin: '0',
      pathname: 'order',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      table_list: [],
      columns: [
        { name: 'order_sn', required: true, label: this.$t('order.view_orderlist.order_sn'), align: 'left', field: 'order_sn' },
        { name: 'order_status', required: true, label: this.$t('order.view_orderlist.order_status'), align: 'left', field: 'order_status' },
        { name: 'message', required: true, label: this.$t('order.view_orderlist.buyer'), align: 'left', field: 'message' },
        { name: 'type', required: true, label: this.$t('order.view_orderlist.pay_time'), align: 'left', field: 'type' },
        { name: 'create_time', required: true, label: this.$t('createdtime'), align: 'left', field: 'create_time' },
        { name: 'action', label: this.$t('action'), align: 'center' }
      ],
      pagination: {
        page: 1,
        rowsPerPage: '30'
      }
    }
  },
  methods: {
    readed () {},
    reFresh () {},
    getSearchList () {}
  },
  created () {
    var _this = this;
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
      storeService.getStoreList().then(stores => {
        _this.stores = stores;
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
  mounted () {
    var _this = this;
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + 'px';
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px';
    }
  }
}
</script>
