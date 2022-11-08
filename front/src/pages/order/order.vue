<style scoped>
.title {
  display: inline-table;
  width: 5em;
}

.title span {
  display: table-cell;
}

.condition-font-size {
  font-size: 0.7em;
}
</style>
<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <q-table
          dense
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
          <div ref="top" class="full-width">
            <div class="row q-my-xs">
              <span class="title">
                <span class="vertical-middle text-grey-6 condition-font-size">{{ $t('sync') }}:</span>
              </span>
              <q-btn class="q-mr-md condition-font-size" unelevated dense :label="$t('order.status.ready_to_ship')"
                     @click="syncShipmentOrder"/>
              <q-btn class="q-mr-md condition-font-size" unelevated dense :label="$t('order.view_orderlist.specified')"
                     @click="syncOrder"/>
              <q-space/>
              <span class="title">
                <span class="vertical-middle text-grey-6 condition-font-size">{{ $t('more') }}:</span>
              </span>
              <q-btn class="q-mr-md condition-font-size" unelevated dense icon="print"
                     :label="$t('order.view_orderlist.print')" @click="batchPrintLogistics"/>
              <q-btn class="q-mr-md condition-font-size" unelevated dense
                     :label="$t('order.view_orderavailable.stock_matching')" @click="stockMatching()"/>
              <q-btn class="q-mr-md condition-font-size" unelevated dense :label="$t('order.view_orderlist.expand')"
                     @click="expandBatch"/>
              <q-btn class="q-mr-md condition-font-size" unelevated dense :label="$t('order.view_orderlist.close')"
                     @click="close"/>
            </div>
            <q-separator/>
            <div class="row">
              <div class="col">
                <div class="row q-my-xs">
                  <span class="title col-2">
                    <span class="vertical-middle text-grey-6 condition-font-size">{{ $t('store.label') }}:</span>
                  </span>
                  <div class="col-10 nowrap">
                    <q-scroll-area
                        :thumb-style="{right: '4px', borderRadius: '5px', backgroundColor: '#027be3', height: '4px', opacity: 0.45}"
                        :content-style="{'white-space': 'nowrap'}"
                        :content-active-style="{'white-space': 'nowrap'}" class="full-width"
                        style="height: 25px">
                      <q-btn class="q-mr-md condition-font-size"
                             :class="search_form.cur_shop_id === option.value ? 'bg-primary text-white' : ''"
                             v-for="option in shop_select.options" unelevated dense
                             :key="option.value" :label="option.label"
                             @click="search_form.cur_shop_id = option.value"/>
                    </q-scroll-area>
                  </div>
                </div>
                <div class="row q-my-xs">
                  <span class="title col-2">
                    <span class="vertical-middle text-grey-6 condition-font-size">{{ $t('order.view_orderlist.order_status') }}:</span>
                  </span>
                  <div class="col-10 nowrap">
                    <q-scroll-area ref="store"
                        :thumb-style="{right: '4px', borderRadius: '5px', backgroundColor: '#027be3', height: '4px', opacity: 0.45}"
                        :content-style="{'white-space': 'nowrap'}"
                        :content-active-style="{'white-space': 'nowrap'}" class="full-width"
                        style="height: 25px">
                      <q-btn class="q-mr-md condition-font-size"
                             :class="search_form.status === option.value ? 'bg-primary text-white' : ''"
                             v-for="option in status_select.options" unelevated dense
                             :key="option.value" :label="option.label"
                             @click="search_form.status = option.value"/>
                    </q-scroll-area>
                  </div>
                </div>
                <div class="row q-my-xs">
                  <span class="title">
                    <span class="vertical-middle text-grey-6 condition-font-size">{{ $t('order.view_orderlist.order_handle_status') }}:</span>
                  </span>
                  <q-btn class="q-mr-md condition-font-size"
                         :class="search_form.handle_status === option.value ? 'bg-primary text-white' : ''"
                         v-for="option in handle_status_select.options" unelevated dense
                         :key="option.value" :label="option.label"
                         @click="search_form.handle_status = option.value"/>
                </div>
              </div>
              <q-separator vertical/>
              <div class="col q-px-md">
                <div class="row">
                  <span class="title">
                    <span class="col-2 vertical-middle text-grey-6 condition-font-size">{{ $t('search_condition') }}</span>
                  </span>
                  <q-btn-group class="col-10" unelevated push>
                    <q-btn class="q-ma-xs" dense @click="resetForm" icon="delete" :label="$t('clear')"/>
                    <q-btn class="q-ma-xs" dense icon="search" :label="$t('search')" @click="getSearchList(true)"/>
                  </q-btn-group>
                </div>
                <div class="row">
                  <q-input dense clearable clear-icon="close" color="dark" v-model="search_form.order_sn"
                           class="condition-font-size q-mr-md"
                           :label="$t('order.view_orderlist.order_sn')" @keyup.enter="getSearchList(true)"/>
                  <q-input input-class="cursor-pointer" dense readonly clearable clear-icon="close"
                           v-model="batch_display"
                           class="condition-font-size q-mr-md"
                           :label="$t('order.view_orderrecord.create_document')" @click="openRecord()"
                           @keyup.enter="getSearchList(true)">
                    <template v-slot:after>
                      <q-icon name="close" class="cursor-pointer" @click="clearBatchRecord()"/>
                    </template>
                  </q-input>
                  <q-input dense clearable clear-icon="close" color="dark" v-model="search_form.buyer"
                           class="condition-font-size q-mr-md"
                           :label="$t('order.view_orderlist.buyer')" @keyup.enter="getSearchList(true)"/>
                  <q-input dense clearable clear-icon="close" color="dark" v-model="search_form.model_sku"
                           class="condition-font-size q-mr-md"
                           :label="$t('store.view_variant.model_sku')" @keyup.enter="getSearchList(true)"/>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td auto-width>
              <q-checkbox dense v-model="props.selected" color="grey-8" keep-color/>
            </q-td>
            <q-td :props="props" v-for="col in columns" :key="initRow(props, col)">
              <template v-if="col.name === 'action'">
                <q-btn round flat push color="dark" v-if="props.row.handle_status === 0"
                       icon="local_shipping"
                       @click="shipment(props.row.id)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('order.view_orderavailable.send') }}
                  </q-tooltip>
                </q-btn>
                <q-fab round flat push class="z-inherit" v-if="[0,1,2,3].indexOf(props.row.handle_status) === -1"
                       icon="fast_forward" direction="left">
                  <q-fab-action color="warning" @click="partially_shipment(props.row.id)"
                                :label="$t('order.view_orderavailable.partially_shipment')"/>
                  <q-fab-action color="secondary" @click="forced_shipment(props.row.id)"
                                :label="$t('order.view_orderavailable.forced_shipment')"/>
                  <template v-slot:tooltip>
                    <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                               content-style="font-size: 12px">{{ $t('order.view_orderavailable.forced_shipment') }}
                    </q-tooltip>
                  </template>
                </q-fab>
                <q-btn round flat push color="dark"
                       icon="join_inner" @click="stockMatching(props.row.id)"
                       v-if="[0,1,2,3].indexOf(props.row.handle_status) === -1">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('order.view_orderavailable.stock_matching') }}
                  </q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark"
                       icon="remove_circle_outline"
                       @click="freedStock(props.row.id)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('order.view_orderavailable.freed_stock') }}
                  </q-tooltip>
                </q-btn>
                <q-btn v-if="canPrint(props.row.order_status)" round flat push color="dark" icon="print"
                       @click="printLogistics(props.row.order_sn)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('order.view_orderlist.print_logistics') }}
                  </q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark"
                       :icon="props.expand ? 'expand_less' : 'expand_more'"
                       @click="props.expand = !props.expand">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('details') }}
                  </q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark" icon="sync_alt" @click="refreshOrder(props.row['order_sn'])">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]"
                             content-style="font-size: 12px">{{ $t('sync') }}
                  </q-tooltip>
                </q-btn>
              </template>
              <template v-else-if="col.name === 'order_sn'">
                <div class="full-height full-width relative-position" style="display: table">
                  <span style="display: table-cell; vertical-align: middle">{{props.row[col.name]}}</span>
                  <q-chip dense class="absolute cursor-pointer" style="right: -15px; top: -5px" v-if="checkOverdue(props.row)" color="red-5" text-color="white">
                    <q-avatar color="deep-orange">
                      <q-icon name="notification_important" color="lime-12"/>
                    </q-avatar>
                    {{checkOverdue(props.row)}}
                  </q-chip>
                </div>
              </template>
              <template v-else-if="col.name === 'order_status'">
                {{ formatStatus(props.row[col.name]) }}
              </template>
              <template v-else-if="col.name === 'days_to_ship'">
                {{ formatDate(props.row['ship_by_date'], props.row[col.name]) }}
              </template>
              <template v-else-if="col.name === 'handle_status'">
                {{ formatHandleStatus(props.row[col.name]) }}
              </template>
              <template v-else-if="col.name === 'store'">
                <q-input borderless dense readonly :value="formatStore(props.row[col.name])">
                  <q-tooltip>{{ formatStore(props.row[col.name]) }}</q-tooltip>
                </q-input>
              </template>
              <template v-else>
                {{ props.row[col.name] }}
              </template>
            </q-td>
          </q-tr>
          <q-tr v-show="props.expand" :props="props">
            <q-td colspan="100%">
              <order-details :order=props.row :show="props.expand" :order-id="props.row.id"
                             @freedStock="props.row.handle_status = -1"></order-details>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </transition>
    <template>
      <div ref="footer" class="q-pa-none flex flex-center">
        <span class="text-black"
              style="padding-right: 10px">{{ $t('selected') }}: {{ search_form.selected.length }}</span>
        <span class="text-black" style="padding-right: 10px">{{ $t('total') }}: {{ count }}</span>
        <q-btn v-show="pathname_previous" flat push color="purple" :label="$t('previous')" icon="navigate_before"
               @click="getListPrevious()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">
            {{ $t('previous') }}
          </q-tooltip>
        </q-btn>
        <span v-show="pathname_previous && pathname_next" class="text-purple"
              style="font-size: 14px">{{ curPage }}</span>
        <q-btn v-show="pathname_next" flat push color="purple" :label="$t('next')" icon-right="navigate_next"
               @click="getListNext()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">
            {{ $t('next') }}
          </q-tooltip>
        </q-btn>
        <q-btn v-show="!pathname_previous && !pathname_next" flat push color="dark" :label="$t('no_data')"></q-btn>
        <q-select borderless dense v-model="pagination.rowsPerPage" :value="pagination.rowsPerPage"
                  :options="pageOptions">
          <template v-slot:prepend><span style="font-size: 14px">{{ $t('row_num') }}</span></template>
        </q-select>
      </div>
    </template>
  </div>
</template>
<router-view/>

<script>
import { LocalStorage } from 'quasar'
import SyncOrder from 'pages/order/components/syncorder'
import OrderDetails from 'pages/order/components/orderdetails'
import OrderRecordList from 'pages/order/components/orderrecordlist'
import storeService from 'pages/store/services/storeservice'
import orderService from 'pages/order/services/orderservice'
import LogisticsView from 'pages/order/components/logisticsview'
import moment from 'moment'

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
        handle_status: '',
        cur_shop_id: null,
        order_sn: '',
        buyer: '',
        model_sku: ''
      },
      status_select: {
        options: [],
        dense: false,
        denseOpts: false
      },
      handle_status_select: {
        options: [
          {
            label: this.$t('all'),
            value: ''
          },
          {
            label: this.$t('order.handle_status.lack'),
            value: '-1,-2'
          },
          {
            label: this.$t('order.handle_status.unprocessed'),
            value: '0'
          },
          {
            label: this.$t('order.handle_status.shipped'),
            value: '1,2,3'
          }
        ],
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
        { name: 'handle_status', required: true, label: this.$t('order.view_orderavailable.handle_status'), align: 'left', field: 'handle_status' },
        { name: 'ship_by_date', required: true, label: this.$t('order.view_details.ship_by_date'), align: 'left', field: 'ship_by_date' },
        { name: 'days_to_ship', required: true, label: this.$t('order.view_details.cancel_time'), align: 'left', field: 'days_to_ship' },
        // { name: 'buyer_username', required: true, label: this.$t('order.view_orderlist.buyer'), align: 'left', field: 'buyer_username' },
        // { name: 'pay_time', required: true, label: this.$t('order.view_orderlist.pay_time'), align: 'left', field: 'pay_time' },
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
        this.getSearchList()
      }
    },
    'search_form.handle_status': {
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
    checkOverdue (order) {
      if (order.handle_status <= 0) {
        const curDate = moment(new Date())
        const shipByDate = moment(order.ship_by_date)
        if (order.order_status === 'READY_TO_SHIP') {
          const diffDate = shipByDate.diff(curDate, 'hour')
          if (diffDate <= 0) {
            return this.$t('order.tip.out_of_time')
          } else if (diffDate < 24) {
            return this.$t('order.tip.ship_by_date_overdue')
          }
        } else if (order.order_status === 'PROCESSED' || order.order_status === 'SHIPPED') {
          let messageTip = ''
          if (order.order_status === 'PROCESSED') {
            const diffDate = shipByDate.diff(curDate, 'hour')
            if (diffDate < 48) {
              messageTip += this.$t('order.tip.forecast_alerts')
            }
          }
          const diffDate = shipByDate.add(3, 'day').diff(curDate, 'hour')
          if (diffDate <= 0) {
            if (messageTip.length > 0) {
              messageTip += '/'
            }
            messageTip += this.$t('order.tip.out_of_time')
            return messageTip
          } else if (diffDate < 72) {
            if (messageTip.length > 0) {
              messageTip += '/'
            }
            messageTip += this.$t('order.tip.delivery_date_overdue')
            return messageTip
          }
          return messageTip
        }
      }
      return ''
    },
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
      const _this = this
      const orderSnList = []
      for (const i in _this.search_form.selected) {
        orderSnList.push(_this.search_form.selected[i].order_sn)
      }
      orderService.applyLogistics({
        shopId: _this.search_form.cur_shop_id,
        snList: orderSnList
      }).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.openPrint(orderSnList)
      }).finally(() => {
        _this.search_form.selected = []
      })
    },
    printLogistics (orderSn) {
      const _this = this
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
        })
        _this.openPrint([orderSn], () => dialog.hide())
      }).catch(() => {
        dialog.hide()
      })
    },
    openPrint (orderSn, callback) {
      const _this = this
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
    partially_shipment (orderId) {
      const _this = this
      const orderIdList = []
      if (orderId) {
        orderIdList.push(orderId)
      } else {
        for (const i in _this.search_form.selected) {
          orderIdList.push(_this.search_form.selected[i].id)
        }
      }
      orderService.partiallyShipment(orderIdList).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.reFresh()
      })
    },
    forced_shipment (orderId) {
      const _this = this
      const orderIdList = []
      if (orderId) {
        orderIdList.push(orderId)
      } else {
        for (const i in _this.search_form.selected) {
          orderIdList.push(_this.search_form.selected[i].id)
        }
      }
      orderService.forcedShipment(orderIdList).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.reFresh()
      })
    },
    shipment (orderId) {
      const _this = this
      const orderIdList = []
      if (orderId) {
        orderIdList.push(orderId)
      } else {
        for (const i in _this.search_form.selected) {
          orderIdList.push(_this.search_form.selected[i].id)
        }
      }
      orderService.shipment(orderIdList).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.reFresh()
      })
    },
    formatStatus (val) {
      return `${this.$t('order.status.' + val.toLowerCase())}`
    },
    formatHandleStatus (val) {
      if (val === 3) {
        return this.$t('order.handle_status.partially_shipment')
      } else if (val === 2) {
        return this.$t('order.handle_status.forced_shipment')
      } else if (val === 1) {
        return this.$t('order.handle_status.shipped')
      } else if (val === 0) {
        return this.$t('order.handle_status.unprocessed')
      } else {
        return this.$t('order.handle_status.lack')
      }
    },
    formatDate (date, days) {
      if (days) {
        return moment(date).add(days, 'day').format('YYYY-MM-DD HH:mm:ss')
      } else {
        return moment(date).format('YYYY-MM-DD HH:mm:ss')
      }
    },
    formatStore (val) {
      const _this = this
      for (const i in _this.stores) {
        const store = _this.stores[i]
        if (store.id === val) {
          return '[' + store.area + '] ' + store.name
        }
      }
      return val
    },
    getStore () {
      const _this = this
      for (const i in _this.stores) {
        if (_this.stores[i].uid === _this.search_form.cur_shop_id) {
          return _this.stores[i]
        }
      }
      return null
    },
    refreshOrder (orderSn) {
      const _this = this
      orderService.syncOrder({
        shop_id: _this.search_form.cur_shop_id,
        order_sn: orderSn
      }).then(res => {
        _this.reFresh()
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
      })
    },
    syncShipmentOrder () {
      const _this = this
      orderService.syncShipmentOrder().then(() => {
        _this.reFresh()
      })
    },
    syncOrder () {
      const _this = this
      _this.$q.dialog({
        component: SyncOrder,
        parent: _this,
        shop_id: _this.search_form.cur_shop_id
      })
    },
    freedStock (orderId) {
      const _this = this
      const orderIdList = []
      if (orderId) {
        orderIdList.push(orderId)
      } else {
        _this.search_form.selected.forEach(order => {
          orderIdList.push(order.id)
        })
      }
      orderService.freedStock(orderIdList).then((res) => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getSearchList()
      })
    },
    stockMatching (id) {
      const _this = this
      orderService.stockMatching({ order_id: id }).then((res) => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        if (!id) {
          _this.search_form.handle_status = '0'
        }
        _this.getSearchList()
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
        const params = {
          shop_id: _this.search_form.cur_shop_id,
          order_status: _this.search_form.status,
          handle_status: _this.search_form.handle_status,
          order_sn: _this.search_form.order_sn,
          buyer_username: _this.search_form.buyer,
          max_page: _this.pagination.rowsPerPage,
          model_sku: _this.search_form.model_sku ? _this.search_form.model_sku.trim() : null,
          record: batchList
        }
        if (_this.search_form.handle_status) {
          params.ordering = 'ship_by_date'
          params.is_handle = 1
        }
        orderService.getOrderList(params).then(res => {
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
      const _this = this
      if (LocalStorage.has('auth')) {
        orderService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this
      if (LocalStorage.has('auth')) {
        orderService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
    },
    resetPageData (res) {
      const _this = this
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
      var ratio = 0, screen = window.screen, ua = navigator.userAgent.toLowerCase()
      if (window.devicePixelRatio !== undefined) {
        ratio = window.devicePixelRatio
      } else if (~ua.indexOf('msie')) {
        if (screen.deviceXDPI && screen.logicalXDPI) {
          ratio = screen.deviceXDPI / screen.logicalXDPI
        }
      } else if (window.outerWidth !== undefined && window.innerWidth !== undefined) {
        ratio = window.outerWidth / window.innerWidth
      }
      if (ratio) {
        ratio = Math.round(ratio * 100)
      }
      // ratio 就是获取到的百分比
      console.log(ratio)
      this.onresize_height = ratio
      return ratio
    },
    resize () {
      const _this = this
      let ratio = 0
      if (_this.curWindowRatio) {
        ratio = _this.detectZoom() - _this.curWindowRatio
      }
      _this.curWindowRatio = _this.detectZoom()
      const height = (_this.$q.screen.height - (_this.$refs.footer.clientHeight + _this.$refs.top.clientHeight + 65)) * ((100 - ratio) / 100)
      if (_this.$q.platform.is.electron) {
        _this.height = String(height) + 'px'
      } else {
        _this.height = height + '' + 'px'
      }
    }
  },
  created () {
    var _this = this
    if (LocalStorage.has('openid')) {
      _this.openid = LocalStorage.getItem('openid')
    } else {
      _this.openid = ''
      LocalStorage.set('openid', '')
    }
    if (LocalStorage.has('login_name')) {
      _this.login_name = LocalStorage.getItem('login_name')
    } else {
      _this.login_name = ''
      LocalStorage.set('login_name', '')
    }
    if (LocalStorage.has('auth')) {
      _this.authin = '1'
      const status = orderService.getStatusList(_this)
      _this.status_select.options = status
      _this.search_form.status = status[0].value
      storeService.getStoreList().then(stores => {
        _this.stores = stores
        const options = []
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
        _this.search_form.cur_shop_id = options[0].value
        _this.shop_select.options = options
      }).finally(() => {
        _this.getSearchList()
      })
    } else {
      _this.authin = '0'
    }
  },
  mounted () {
    const _this = this
    _this.resize()
    // const storeArea = _this.$refs.store
    // storeArea.addEventListener('wheel', (event) => {
    //   event.preventDefault()
    //   storeArea.scrollLeft += event.deltaY
    // })
  },
  updated () {
  },
  destroyed () {
  }
}
</script>
