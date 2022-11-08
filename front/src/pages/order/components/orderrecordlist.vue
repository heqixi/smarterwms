<template>
  <q-dialog ref="dialog">
    <q-layout view="hHh lpr fFf" container class="full-width bg-white" style="min-width: 700px">
      <q-header elevated class="bg-white text-black">
        <q-toolbar>
          <q-toolbar-title>
            {{ $t('order.view_orderrecord.order_record') }}
          </q-toolbar-title>
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page padding class="q-pa-md full-width">
          <q-table
              selection="multiple"
              :selected.sync="search_form.selected"
              class="my-sticky-header-table shadow-24"
              :data="table_list"
              row-key="batch_number"
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
            <template v-slot:body="props">
              <q-tr :props="props">
                <q-td auto-width>
                  <q-checkbox v-model="props.selected" color="grey-8" keep-color/>
                </q-td>
                <q-td :props="props" v-for="col in columns" :key="col.name">
                  <template v-if="col.name === 'type'">
                    {{formatType(props.row[col.name])}}
                  </template>
                  <template v-else>
                    {{props.row[col.name]}}
                  </template>
                </q-td>
              </q-tr>
            </template>
          </q-table>
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
        </q-page>
      </q-page-container>
      <q-footer elevated class="bg-white text-black text-right" style="padding: 5px">
        <q-btn :label="$t('cancel')" @click="hide()"/>
        <q-btn :label="$t('submit')" @click="submit()" color="primary" text-color="white"/>
      </q-footer>
    </q-layout>
  </q-dialog>
</template>
<script>
import { LocalStorage } from 'quasar'
import orderRecordService from 'pages/order/services/orderrecordservice'

export default {
  name: 'OrderRecordList',
  data () {
    return {
      search_form: {
        selected: []
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
      columns: [
        { name: 'batch_number', required: true, label: this.$t('order.view_orderrecord.batch_number'), align: 'left', field: 'batch_number' },
        { name: 'type', required: true, label: this.$t('order.view_orderrecord.type'), align: 'left', field: 'type' },
        { name: 'create_time', required: true, label: this.$t('createdtime'), align: 'left', field: 'create_time' }
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
  props: {
    type: Number
  },
  methods: {
    submit () {
      const _this = this
      _this.$emit('ok', _this.search_form.selected)
      _this.hide()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    formatType (val) {
      return this.$t('order.view_orderrecord.type_options.' + val)
    },
    getSearchList () {
      const _this = this
      orderRecordService.getBatchList(_this.type).then(_this.resetPageData)
    },
    resetPageData (res) {
      const _this = this
      _this.table_list = res.results
      _this.pathname_previous = res.previous
      _this.pathname_next = res.next
      _this.count = res.count
      _this.curPage = res.page
      _this.search_form.selected = []
    },
    getListPrevious () {
      const _this = this
      if (LocalStorage.has('auth')) {
        orderRecordService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this
      if (LocalStorage.has('auth')) {
        orderRecordService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
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
    }
  }
}
</script>
