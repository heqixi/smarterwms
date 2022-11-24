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
          bordered>
        <template v-slot:top>
          <div style="width: 100%">
            <q-btn-group push class="float-left">
              <q-btn :label='$t("fetch.view_fetchlist.receive")' icon="outbox" @click="receive()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('fetch.view_fetchlist.batch_receive_tip') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
            <q-btn-group push class="float-right q-px-xs">
              <q-input dense clearable clear-icon="close" color="dark"
                       v-model="search_form.name"
                       :label="$t('fetch.view_fetchlist.name')" @keyup.enter="getSearchList()"/>
              <q-btn dense @click="resetForm" :label="$t('clear')"/>
              <q-btn icon="search" @click="getSearchList()">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('search') }}</q-tooltip>
              </q-btn>
            </q-btn-group>
          </div>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td auto-width>
              <q-checkbox v-model="props.selected" color="grey-8" keep-color/>
            </q-td>
            <q-td :props="props" v-for="col in columns" :key="col.name">
              <template v-if="col.name === 'name'">
                <q-input :value="props.row[col.name]" borderless>
                  <q-tooltip>{{props.row[col.name]}}</q-tooltip>
                </q-input>
              </template>
              <template v-else-if="col.name === 'image'">
                <q-img :src="props.row[col.name]" ratio="1" style="width: 80px; height: 80px;"/>
              </template>
              <template v-else-if="col.name === 'status'">
                {{formatStatus(props.row[col.name])}}
              </template>
              <template v-else-if="col.name === 'action'">
                <q-btn-group push>
                  <q-btn flat color="dark"
                         :label='$t("fetch.view_fetchlist.open_link")' @click="openUrl(props.row.url)"/>
                  <q-btn flat color="dark"
                         :label='$t("fetch.view_fetchlist.profit_calc")' @click="profitCalc(props.row)"/>
                  <q-btn flat color="dark"
                         :label='$t("fetch.view_fetchlist.receive")' @click="receive(props.row)"/>
                  <q-btn flat color="dark"
                         :label='$t("fetch.view_fetchlist.download_medias")' @click="downloadMedias(props.row.id)"/>
                </q-btn-group>
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
import fetchService from 'pages/fetchbox/services/fetchservice'
import ProfitCalculatorDialog from 'pages/fetchbox/components/profitcalculatordialog.vue'
import Receive from 'pages/fetchbox/components/receive.vue'
import mediaService from 'pages/fetchbox/services/mediaservice'
import JSZip from 'jszip'
import FileSaver from 'file-saver'
import NewFormDialog from 'components/Share/newFormDialog'
import {getauth, postauth} from 'boot/axios_request';

export default {
  name: 'FetchList',
  data () {
    return {
      search_form: {
        status: null,
        name: null,
        selected: []
      },
      allStore: [],
      selectedStore: {
        store: undefined
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
        { name: 'company', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.company'), field: 'company' },
        { name: 'name', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.name'), field: 'name' },
        { name: 'image', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.image'), field: 'image' },
        { name: 'price', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.price'), field: 'price' },
        { name: 'weight', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.weight'), field: 'weight' },
        { name: 'size', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.size'), field: 'size' },
        { name: 'logistics_costs', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.logistics_costs'), field: 'logistics_costs' },
        { name: 'mix_purchase_qty', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.mix_purchase_qty'), field: 'mix_purchase_qty' },
        { name: 'status', required: true, align: 'center', label: this.$t('fetch.view_fetchlist.status'), field: 'status' },
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
  watch: {
    'pagination.rowsPerPage': {
      handler (n, o) {
        this.getSearchList()
      }
    }
  },
  methods: {
    downloadMedias (id) {
      fetchService.getFetchMedias(id).then(medias => {
        const zip = new JSZip()
        const promises = []
        // const medias = res.result
        for (const i in medias) {
          if (medias[i].type !== 1) {
            promises.push(mediaService.imgUrlToFile(medias[i].url).then(({ blob }) => {
              const filename = mediaService.getFileName(medias[i].url)
              zip.file(filename, blob, { binary: true })
            }))
          }
        }
        Promise.all(promises).then(() => {
          zip.generateAsync({ type: 'blob' }).then(content => {
            FileSaver.saveAs(content, '素材包.zip')
          })
        })
      })
    },
    formatStatus (status) {
      if (status > 0) {
        return this.$t('fetch.view_fetchlist.received')
      } else {
        return ''
      }
    },
    profitCalc (row) {
      const _this = this
      _this.$q.dialog({
        component: ProfitCalculatorDialog,
        data: row
      })
    },
    resetForm () {
      const _this = this
      _this.search_form.name = null
    },
    async selectStore () {
      var _this = this
      if (!_this.allStore || _this.allStore.length <= 0) {
        _this.allStore = await getauth('store/all?type=1', {})
      }
      return new Promise(resolve => {
        const formItems = [
          {
            name: 'store',
            label: '店铺',
            type: 'select',
            field: 'store',
            options: _this.allStore,
            optionLabel: store => {
              return store.name
            }
          }
        ]
        this.$q.dialog({
          component: NewFormDialog,
          title: '请选择店铺',
          newFormData: _this.selectedStore,
          newFormItems: formItems
        }).onOk(() => {
          resolve(_this.selectedStore.store)
        })
      })
    },
    receive (row) {
      const _this = this
      const fetchList = []
      const received = []
      if (row) {
        if (row.status === 1) {
          received.push(row.id)
        } else {
          fetchList.push(row.id)
        }
      } else {
        _this.search_form.selected.forEach(row => {
          if (row.status === 1) {
            received.push(row.id)
          } else {
            fetchList.push(row.id)
          }
        })
      }
      if (received.length > 0) {
        let message = ''
        const btn = []
        if (row) {
          message = _this.$t('fetch.view_fetchlist.received_tip')
          btn.push(_this.$t('submit'))
        } else {
          message = _this.$t('fetch.view_fetchlist.batch_received_tip')
          btn.push(_this.$t('submit'))
          btn.push(`${_this.$t('fetch.view_fetchlist.receive')}${_this.$t('all')}`)
        }
        _this.$q.dialog({
          component: Receive,
          title: _this.$t('fetch.view_fetchlist.receive'),
          message: message,
          btn: btn
        }).onOk((btnIndex) => {
          if (btnIndex === 1 || (row && btnIndex === 0)) {
            received.forEach(product => {
              fetchList.push(product)
            })
          }
          _this._receive(fetchList)
        })
      } else {
        _this._receive(fetchList)
      }
    },
    async _receive (fetchList) {
      const _this = this
      _this.selectStore().then(store => {
        if (store) {
          if (fetchList && fetchList.length > 0) {
            fetchService.receiveProduct(fetchList).then(globalProductIds => {
              console.log('receive product ids ', globalProductIds)
              if (store.platform === 1) {
                postauth('shopee/publish/claim', { global_product_ids: globalProductIds, store_id: store.id }).then(res => {
                  const successCount = res.success_list.length
                  const failCount = res.fail_list.length
                  _this.$q.notify({
                    message: `认领成功 ${successCount} 个产品，失败 ${failCount}`,
                    icon: 'check',
                    color: 'green'
                  })
                }).catch(err => {
                  console.error('claim product fail ', err)
                  _this.$q.notify({
                    message: '认领成功失败',
                    icon: 'check',
                    color: 'green'
                  })
                })
              }
              _this.getSearchList(_this.curPage)
            })
          }
        } else {
          console.log('no store selected')
        }
      })
    },
    openUrl (url) {
      window.open(url, '_blank')
    },
    getSearchList (page) {
      const _this = this
      if (LocalStorage.has('auth')) {
        fetchService.getFetchList({
          name: _this.search_form.name,
          max_page: _this.pagination.rowsPerPage,
          page: page
        }).then(_this.resetPageData)
      }
    },
    getListPrevious () {
      const _this = this;
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
      _this.getSearchList()
    } else {
      _this.authin = '0';
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
}
</script>
