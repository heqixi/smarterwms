<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <q-table
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
              <q-btn :label="$t('new')" icon="add" @click="newArea()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('new') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
            <q-btn-group push class="float-right q-px-xs">
              <q-input dense clearable clear-icon="close" color="dark"
                       v-model="search_form.area"
                       :label="$t('fetch.view_areasettings.area')" @keyup.enter="getSearchList()"/>
              <q-btn dense @click="resetForm" :label="$t('clear')"/>
              <q-btn icon="search" @click="getSearchList()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('search') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
          </div>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td :props="props" v-for="col in columns" :key="col.name">
              <template v-if="col.name === 'image'">
                <q-img :src="props.row[col.name]" ratio="1" style="width: 80px; height: 80px;"/>
              </template>
              <template v-else-if="col.name === 'action'">
                <q-btn flat push color="dark" icon="edit" @click="editArea(props.row)">
                  <q-tooltip>{{$t('edit')}}</q-tooltip>
                </q-btn>
                <q-btn flat push color="dark" icon="delete" @click="deleteArea(props.row.id)">
                  <q-tooltip>{{$t('delete')}}</q-tooltip>
                </q-btn>
              </template>
              <template v-else>
                {{props.row[col.name]}}
              </template>
            </q-td>
          </q-tr>
        </template>
      </q-table>
    </transition>
    <template>
      <div class="q-pa-lg flex flex-center">
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

<script>
import { LocalStorage } from 'quasar'
import AreaSettings from 'pages/fetchbox/components/areasettings'
import fetchService from 'pages/fetchbox/services/fetchservice'

export default {
  name: 'AreaSettings',
  data () {
    return {
      search_form: {
        area: null
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
        { name: 'area', required: true, label: this.$t('fetch.view_areasettings.area'), align: 'left', field: 'area' },
        { name: 'exchange_rate', required: true, label: this.$t('fetch.view_areasettings.exchange_rate'), align: 'left', field: 'exchange_rate' },
        { name: 'activity_rate', required: true, label: this.$t('fetch.view_areasettings.activity_rate'), align: 'left', field: 'activity_rate' },
        { name: 'commission_rate', required: true, label: this.$t('fetch.view_areasettings.commission_rate'), align: 'left', field: 'commission_rate' },
        { name: 'transaction_rate', required: true, label: this.$t('fetch.view_areasettings.transaction_rate'), align: 'left', field: 'transaction_rate' },
        { name: 'withdrawal_rate', required: true, label: this.$t('fetch.view_areasettings.withdrawal_rate'), align: 'left', field: 'withdrawal_rate' },
        { name: 'exchange_loss_rate', required: true, label: this.$t('fetch.view_areasettings.exchange_loss_rate'), align: 'left', field: 'exchange_loss_rate' },
        { name: 'buyer_shipping', required: true, label: this.$t('fetch.view_areasettings.buyer_shipping'), align: 'left', field: 'buyer_shipping' },
        { name: 'other_fee', required: true, label: this.$t('fetch.view_areasettings.other_fee'), align: 'left', field: 'other_fee' },
        { name: 'action', align: 'center', label: '操作' }
      ],
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
    newArea () {
      const _this = this
      _this.$q.dialog({
        component: AreaSettings
      }).onOk(res => {
        fetchService.saveArea(res).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          })
          _this.getSearchList()
        })
      })
    },
    editArea (data) {
      const _this = this
      _this.$q.dialog({
        component: AreaSettings,
        settings: data
      }).onOk(res => {
        console.log('editArea', res)
        fetchService.saveArea(res).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          })
          _this.getSearchList()
        })
      })
    },
    deleteArea (id) {
      const _this = this
      fetchService.deleteArea(id).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getSearchList()
      })
    },
    resetForm () {
      const _this = this
      _this.search_form.area = null
    },
    getSearchList () {
      const _this = this
      if (LocalStorage.has('auth')) {
        fetchService.getAreaList({
          area: _this.search_form.area,
          max_page: _this.pagination.rowsPerPage
        }).then(_this.resetPageData)
      }
    },
    getListPrevious () {
      const _this = this
      if (LocalStorage.has('auth')) {
        fetchService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this
      if (LocalStorage.has('auth')) {
        fetchService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
    },
    resetPageData (res) {
      const _this = this
      _this.table_list = res.results
      _this.pathname_previous = res.previous
      _this.pathname_next = res.next
      _this.count = res.count
      _this.curPage = res.page
    },
    reFresh () {
      const _this = this
      _this.getSearchList()
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
      _this.height = String(_this.$q.screen.height - 290) + 'px'
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px'
    }
  },
  updated () {},
  destroyed () {}
}
</script>
