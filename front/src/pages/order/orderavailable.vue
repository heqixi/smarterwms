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
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('order.view_orderavailable.send')" icon="local_shipping" @click="shipment()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.send') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('order.view_orderavailable.stock_matching')" @click="stockMatching()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.stock_matching') }}</q-tooltip>
              </q-btn>
              <q-btn-dropdown :label="$t('order.view_orderlist.expand')+'/'+$t('order.view_orderlist.close')">
                <q-list>
                  <q-item clickable v-close-popup @click="expand">
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
                        v-model="search_form.handle_status"
                        :options="status_select.options"
                        :label="$t('order.view_orderlist.order_status')"
                        emit-value
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
                <q-btn round flat push color="dark" v-if="props.row.handle_status === 0"
                       icon="local_shipping"
                       @click="shipment(props.row.id)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.send') }}</q-tooltip>
                </q-btn>
                <q-fab round flat push class="z-inherit" v-if="[0,1,2,3].indexOf(props.row.handle_status) === -1" icon="fast_forward" direction="left">
                  <q-fab-action color="warning" @click="partially_shipment(props.row.id)" :label="$t('order.view_orderavailable.partially_shipment')" />
                  <q-fab-action color="secondary" @click="forced_shipment(props.row.id)" :label="$t('order.view_orderavailable.forced_shipment')" />
                  <template v-slot:tooltip>
                    <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.forced_shipment') }}</q-tooltip>
                  </template>
                </q-fab>
                <q-btn round flat push color="dark"
                       icon="join_inner" @click="stockMatching(props.row.id)"
                       v-if="[0,1,2,3].indexOf(props.row.handle_status) === -1">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.stock_matching') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark"
                       icon="remove_circle_outline"
                       @click="freedStock(props.row.id)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderavailable.freed_stock') }}</q-tooltip>
                </q-btn>
                <q-btn v-if="canPrint(props.row.order_status)" round flat push color="dark" icon="print"
                       @click="printLogistics(props.row.store, props.row.order_sn)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('order.view_orderlist.print_logistics') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark"
                       :icon="props.expand ? 'expand_less' : 'expand_more'"
                       @click="props.expand = !props.expand">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('details') }}</q-tooltip>
                </q-btn>
              </template>
              <template v-else-if="col.name === 'ship_by_date'">
                {{formatDate(props.row[col.name])}}
              </template>
              <template v-else-if="col.name === 'days_to_ship'">
                {{formatDate(props.row['ship_by_date'], props.row[col.name])}}
              </template>
              <template v-else-if="col.name === 'handle_status'">
                {{formatStatus(props.row[col.name])}}
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
<script>
import { LocalStorage } from 'quasar'
import moment from 'moment'
import orderService from 'pages/order/services/orderservice'
import LogisticsView from 'pages/order/components/logisticsview'
import OrderDetails from 'pages/order/components/orderdetails'
import OrderRecordList from 'pages/order/components/orderrecordlist'

export default {
  name: 'OrderAvailable',
  components: { OrderDetails },
  data () {
    return {
      more: false,
      batch_display: null,
      expandObj: {},
      search_form: {
        batch_number_selected: null,
        handle_status: '',
        selected: [],
        order_sn: ''
      },
      status_select: {
        options: [
          {
            label: this.$t('all'),
            value: ''
          },
          {
            label: this.$t('order.handle_status.unprocessed'),
            value: '0'
          },
          {
            label: this.$t('order.handle_status.lack'),
            value: '-1,-2'
          },
          {
            label: this.$t('order.handle_status.shipped'),
            value: '1,2,3'
          }
        ],
        dense: false,
        denseOpts: false
      },
      openid: '',
      login_name: '',
      authin: '0',
      pathname_previous: '',
      pathname_next: '',
      separator: 'cell',
      loading: false,
      height: '',
      table_list: [],
      columns: [
        { name: 'order_sn', required: true, label: this.$t('order.view_orderlist.order_sn'), align: 'left', field: 'order_sn' },
        { name: 'handle_status', required: true, label: this.$t('order.view_orderavailable.handle_status'), align: 'left', field: 'handle_status' },
        { name: 'ship_by_date', required: true, label: this.$t('order.view_details.ship_by_date'), align: 'left', field: 'ship_by_date' },
        { name: 'days_to_ship', required: true, label: this.$t('order.view_details.cancel_time'), align: 'left', field: 'days_to_ship' },
        { name: 'create_time', required: true, label: this.$t('createdtime'), align: 'left', field: 'create_time' },
        { name: 'action', label: this.$t('action'), align: 'center' }
      ],
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      pageOptions: [10, 20, 30, 50, 100, 500],
      count: 0,
      curPage: 1
    }
  },
  watch: {
    'pagination.rowsPerPage': {
      handler (n, o) {
        this.getSearchList()
      }
    },
    'search_form.handle_status': {
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
    expand () {
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
    printLogistics (storeId, orderSn) {
      const _this = this
      const dialog = _this.$q.dialog({
        message: _this.$t('order.view_orderlist.apply_print_tip') + ' ......',
        progress: true,
        persistent: true,
        ok: false
      })
      orderService.applyLogistics({
        storeId: storeId,
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
    formatStatus (val) {
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
    reFresh () {
      this.getSearchList()
    },
    getSearchList (expand) {
      const _this = this
      orderService.getOrderList({
        is_handle: 1,
        order_sn: _this.search_form.order_sn,
        handle_status: _this.search_form.handle_status,
        max_page: _this.pagination.rowsPerPage,
        ordering: 'ship_by_date'
      }).then((res) => {
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
    }
  },
  created () {
    const _this = this
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
      _this.getSearchList()
    } else {
      _this.authin = '0'
    }
  },
  mounted () {
    const _this = this
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 250) + 'px'
    } else {
      _this.height = _this.$q.screen.height - 250 + '' + 'px'
    }
  }
}
</script>
