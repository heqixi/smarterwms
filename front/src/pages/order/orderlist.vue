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
              <q-btn-dropdown :label="$t('sync')">
                <q-list>
                  <q-item clickable v-close-popup @click="syncShipmentOrder">
                    <q-item-section>
                      <q-item-label>{{$t('order.status.ready_to_ship')}}</q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup @click="syncOrder">
                    <q-item-section>
                      <q-item-label>{{$t('order.view_orderlist.specified')}}</q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('order.view_orderlist.print')" icon="print" @click="batchPrintLogistics()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderlist.batch_print_logistics') }}</q-tooltip>
              </q-btn>
              <q-btn-dropdown :label="$t('order.view_orderlist.expand')+'/'+$t('order.view_orderlist.close')">
                <q-list>
                  <q-item clickable v-close-popup @click="expandBatch">
                    <q-item-section>
                      <q-item-label>
                        {{$t('order.view_orderlist.expand')}}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                  <q-item clickable v-close-popup @click="close">
                    <q-item-section>
                      <q-item-label>
                        {{$t('order.view_orderlist.close')}}
                      </q-item-label>
                    </q-item-section>
                  </q-item>
                </q-list>
              </q-btn-dropdown>
            </q-btn-group>
            <q-btn-group push class="float-right">
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
              <q-select dense color="dark" transition-show="flip-up" transition-hide="flip-down"
                        v-model="search_form.status"
                        :options="status_select.options"
                        :label="$t('order.view_orderlist.order_status')"
                        emit-value
                        input-style="{min-width: 500px}"
                        map-options>
                <template v-slot:prepend>
                  <q-icon name="drag_handle"/>
                </template>
              </q-select>
              <q-input dense clearable clear-icon="close" color="dark"
                       v-model="search_form.order_sn"
                       :label="$t('order.view_orderlist.order_sn')" @keyup.enter="getSearchList(true)"/>
              <q-btn dense :label="$t('more')" @click="more = !more">
                <q-icon :name="more ? 'expand_less' : 'expand_more'"/>
              </q-btn>
              <q-btn dense @click="resetForm" :label="$t('clear')"/>
              <q-btn icon="search" @click="getSearchList(true)">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('search') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
          </div>
          <div v-show="more" style="width: 100%; margin-top: .5em">
            <q-card class="no-shadow float-right">
              <q-btn-group push unelevated>
                <q-input class="q-ma-sm" dense clearable clear-icon="close" color="dark"
                         v-model="search_form.buyer"
                         :label="$t('order.view_orderlist.buyer')" @keyup.enter="getSearchList(true)"/>
                <q-input class="q-ma-sm" dense readonly
                         clearable clear-icon="close"
                         v-model="batch_display"
                         :label="$t('order.view_orderrecord.create_document')" @keyup.enter="getSearchList(true)" @click="openRecord()">
                  <template v-slot:append>
                    <q-icon name="menu_open" class="cursor-pointer" @click="openRecord()"/>
                  </template>
                  <template v-slot:after>
                    <q-icon name="close" class="cursor-pointer" @click="clearBatchRecord()"/>
                  </template>
                </q-input>
              </q-btn-group>
            </q-card>
          </div>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td auto-width>
              <q-checkbox v-model="props.selected" color="grey-8" keep-color/>
            </q-td>
            <q-td :props="props" v-for="col in columns" :key="initRow(props, col)">
              <template v-if="col.name === 'action'">
                <q-btn v-if="canPrint(props.row.order_status)" round flat push color="dark" icon="print"
                       @click="printLogistics(props.row.order_sn)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderlist.print_logistics') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark"
                       :icon="props.expand ? 'expand_less' : 'expand_more'"
                       @click="props.expand = !props.expand">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('details') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark" icon="sync_alt" @click="refreshOrder(props.row['order_sn'])">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('sync') }}</q-tooltip>
                </q-btn>
              </template>
              <template v-else-if="col.name === 'order_status'">
                {{formatStatus(props.row[col.name])}}
              </template>
              <template v-else-if="col.name === 'store'">
                {{formatStore(props.row[col.name])}}
              </template>
              <template v-else>
                {{props.row[col.name]}}
              </template>
            </q-td>
          </q-tr>
          <q-tr v-show="props.expand" :props="props">
            <q-td colspan="100%">
              <order-details :order=props.row :show="props.expand" :order-id="props.row.id" @freedStock="props.row.handle_status = -1"></order-details>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </transition>
    <template>
      <div class="q-pa-none flex flex-center">
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
        <q-select borderless dense v-model="pagination.rowsPerPage" :value="pagination.rowsPerPage" :options="pageOptions">
          <template v-slot:prepend><span style="font-size: 14px">{{$t('row_num')}}</span></template>
        </q-select>
      </div>
    </template>
  </div>
</template>
<router-view />

<script>
import { LocalStorage } from 'quasar'
import SyncOrder from 'pages/order/components/syncorder'
import OrderDetails from 'pages/order/components/orderdetails'
import OrderRecordList from 'pages/order/components/orderrecordlist'
import storeService from 'pages/store/services/storeservice'
import orderService from 'pages/order/services/orderservice'
import LogisticsView from 'pages/order/components/logisticsview'

export default {
  name: 'Pageorderlist',
  components: { OrderDetails },
  data () {
    return {
      more: false,
      stores: [],
      expandObj: {},
      batch_display: null,
      search_form: {
        batch_number_selected: null,
        selected: [],
        status: null,
        cur_shop_id: null,
        order_sn: '',
        buyer: ''
      },
      status_select: {
        options: [],
        dense: false,
        denseOpts: false
      },
      shop_select: {
        options: [],
        dense: false,
        denseOpts: false
      },
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
      bin_size_list: [],
      bin_property_list: [],
      warehouse_list: [],
      columns: [
        { name: 'order_sn', required: true, label: this.$t('order.view_orderlist.order_sn'), align: 'left', field: 'order_sn' },
        { name: 'store', required: true, label: this.$t('store.label'), align: 'left', field: 'store' },
        { name: 'order_status', required: true, label: this.$t('order.view_orderlist.order_status'), align: 'left', field: 'order_status' },
        { name: 'buyer_username', required: true, label: this.$t('order.view_orderlist.buyer'), align: 'left', field: 'buyer_username' },
        { name: 'pay_time', required: true, label: this.$t('order.view_orderlist.pay_time'), align: 'left', field: 'pay_time' },
        { name: 'action', label: this.$t('action'), align: 'center' }
      ],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      pageOptions: [10, 20, 30, 50, 100, 500],
      count: 0,
      curPage: 1,
      curWindowRatio: null
    };
  },
  watch: {
    'pagination.rowsPerPage': {
      handler (n, o) {
        this.getSearchList()
      }
    },
    'search_form.cur_shop_id': {
      handler (n, o) {
        this.getSearchList()
      }
    },
    'search_form.status': {
      handler (n, o) {
        this.getSearchList()
      }
    }
  },
  methods: {
    resetForm () {
      this.clearBatchRecord()
      this.search_form.buyer = null
      this.search_form.order_sn = null
    },
    clearBatchRecord () {
      const _this = this
      _this.batch_display = null
      _this.search_form.batch_number_selected = []
    },
    openRecord () {
      const _this = this
      _this.$q.dialog({
        component: OrderRecordList,
        type: 1
      }).onOk(res => {
        _this.search_form.batch_number_selected = res
        let display = ''
        for (const i in _this.search_form.batch_number_selected) {
          display += ',' + _this.search_form.batch_number_selected[i].batch_number
        }
        if (display) {
          display = display.substr(1)
        }
        _this.batch_display = display
      })
    },
    initRow (props, col) {
      this.expandObj[props.row.id] = props
      return col.name
    },
    close () {
      const _this = this
      _this.search_form.selected.forEach(order => {
        _this.expandObj[order.id].expand = false
      })
      _this.search_form.selected = []
    },
    expandBatch () {
      const _this = this
      _this.search_form.selected.forEach(order => {
        _this.expandObj[order.id].expand = true
      })
      _this.search_form.selected = []
    },
    closeAndCleanExpandObj () {
      const _this = this
      const keys = Object.keys(_this.expandObj)
      for (const i in keys) {
        _this.expandObj[keys[i]].expand = false
      }
      _this.expandObj = {}
    },
    batchPrintLogistics () {
      const _this = this;
      const orderSnList = []
      for (const i in _this.search_form.selected) {
        orderSnList.push(_this.search_form.selected[i].order_sn)
      }
      orderService.applyLogistics({
        shopId: _this.search_form.cur_shop_id,
        snList: orderSnList
      })
        .then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          });
          _this.openPrint(orderSnList)
        }).finally(() => {
          _this.search_form.selected = []
        })
    },
    printLogistics (orderSn) {
      const _this = this;
      const dialog = _this.$q.dialog({
        message: _this.$t('order.view_orderlist.apply_print_tip') + ' ......',
        progress: true,
        persistent: true,
        ok: false
      })
      orderService.applyLogistics({
        shopId: _this.search_form.cur_shop_id,
        snList: [orderSn]
      }).then((res) => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        });
        _this.openPrint([orderSn], () => dialog.hide())
      }).catch(() => {
        dialog.hide()
      })
    },
    openPrint (orderSn, callback) {
      const _this = this;
      _this.$q.dialog({
        component: LogisticsView,
        parent: _this,
        orderList: orderSn,
        openid: _this.openid
      })
      if (callback) {
        callback()
      }
    },
    canPrint (orderStatus) {
      return orderStatus.toLowerCase() !== 'unpaid' || orderStatus.toLowerCase() === 'cancelled'
    },
    formatStatus (val) {
      return `${this.$t('order.status.' + val.toLowerCase())}`
    },
    formatStore (val) {
      const _this = this
      for (const i in _this.stores) {
        const store = _this.stores[i]
        if (store.id === val) {
          return store.name + '(' + store.area + ')'
        }
      }
      return val
    },
    getStore () {
      const _this = this;
      for (const i in _this.stores) {
        if (_this.stores[i].uid === _this.search_form.cur_shop_id) {
          return _this.stores[i]
        }
      }
      return null
    },
    refreshOrder (orderSn) {
      const _this = this;
      orderService.syncOrder({
        shop_id: _this.search_form.cur_shop_id, order_sn: orderSn
      }).then(res => {
        _this.reFresh()
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        });
      })
    },
    syncShipmentOrder () {
      const _this = this
      orderService.syncShipmentOrder().then(() => {
        _this.reFresh()
      })
    },
    syncOrder () {
      const _this = this;
      _this.$q.dialog({
        component: SyncOrder,
        parent: _this,
        shop_id: _this.search_form.cur_shop_id
      })
    },
    getSearchList (expand) {
      const _this = this
      if (LocalStorage.has('auth')) {
        const batchList = []
        if (_this.search_form.batch_number_selected && _this.search_form.batch_number_selected.length > 0) {
          _this.search_form.batch_number_selected.forEach(batch => {
            batchList.push(batch.batch_number)
          })
        }
        orderService.getOrderList({
          shop_id: _this.search_form.cur_shop_id,
          order_status: _this.search_form.status,
          order_sn: _this.search_form.order_sn,
          buyer_username: _this.search_form.buyer,
          max_page: _this.pagination.rowsPerPage,
          record: batchList
        }).then(res => {
          _this.resetPageData(res)
          if (expand) {
            setTimeout(() => {
              const keys = Object.keys(_this.expandObj)
              console.log('keys', keys)
              for (const i in keys) {
                _this.expandObj[keys[i]].expand = true
              }
            }, 50)
          }
        })
      }
    },
    getListPrevious () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        orderService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        orderService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
    },
    resetPageData (res) {
      const _this = this;
      _this.table_list = res.results
      _this.pathname_previous = res.previous
      _this.pathname_next = res.next
      _this.count = res.count
      _this.curPage = res.page
      _this.closeAndCleanExpandObj()
      _this.search_form.selected = []
      _this.more = false
    },
    reFresh () {
      const _this = this
      _this.getSearchList()
    },
    detectZoom () {
      var ratio = 0, screen = window.screen, ua = navigator.userAgent.toLowerCase();
      if (window.devicePixelRatio !== undefined) {
        ratio = window.devicePixelRatio;
      } else if (~ua.indexOf('msie')) {
        if (screen.deviceXDPI && screen.logicalXDPI) {
          ratio = screen.deviceXDPI / screen.logicalXDPI;
        }
      } else if (window.outerWidth !== undefined && window.innerWidth !== undefined) {
        ratio = window.outerWidth / window.innerWidth;
      }
      if (ratio) {
        ratio = Math.round(ratio * 100);
      }
      // ratio 就是获取到的百分比
      console.log(ratio)
      this.onresize_height = ratio
      return ratio;
    },
    resize () {
      const _this = this
      let ratio = 0
      if (_this.curWindowRatio) {
        ratio = _this.detectZoom() - _this.curWindowRatio
      }
      _this.curWindowRatio = _this.detectZoom()
      const height = (_this.$q.screen.height - 250) * ((100 - ratio) / 100)
      if (_this.$q.platform.is.electron) {
        _this.height = String(height) + 'px'
      } else {
        _this.height = height + '' + 'px'
      }
    }
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
      const status = orderService.getStatusList(_this);
      _this.status_select.options = status;
      _this.search_form.status = status[0].value;
      storeService.getStoreList().then(stores => {
        _this.stores = stores;
        const options = [];
        options.push({
          label: _this.$t('all'),
          value: ''
        })
        for (const i in stores) {
          const store = stores[i]
          options.push({
            label: store.name + '(' + store.area + ')',
            value: store.uid
          })
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
    const _this = this
    window.addEventListener('resize', _this.resize, true)
    _this.resize()
  },
  updated () {},
  destroyed () {}
};
</script>
