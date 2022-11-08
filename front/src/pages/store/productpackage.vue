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
              <q-btn :label="$t('new')" icon="add" @click="add">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('store.view_productlist.synctip') }}</q-tooltip>
              </q-btn>
              <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh">
                <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
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
              <template v-if="col.name === 'action'">
                <q-btn dense icon="edit" @click="edit(props.row)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('edit') }}</q-tooltip>
                </q-btn>
                <q-btn dense icon="delete" @click="deletePackage(props.row.id)">
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('delete') }}</q-tooltip>
                </q-btn>
              </template>
              <template v-else-if="col.name === 'image'">
                <q-img :src="props.row[col.name]" :ratio="1"></q-img>
              </template>
              <template v-else-if="col.name === 'package_item'">
                <div :key="package_item.id" v-for="package_item in props.row[col.name]">
                  {{package_item.sku}}
                </div>
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

<script>
import PackageEditDialog from 'pages/store/components/packageeditdialog'
import productPackageService from 'pages/store/services/productpackageservice'
import { LocalStorage } from 'quasar'

export default {
  name: 'ProductPackage',
  data () {
    return {
      search_form: {
        selected: []
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
      columns: [
        { name: 'name', required: true, label: this.$t('store.view_package.name'), align: 'left', field: 'name' },
        { name: 'sku', required: true, label: this.$t('store.view_package.package_sku'), align: 'left', field: 'package_sku' },
        { name: 'image', required: true, label: this.$t('store.view_package.image'), align: 'left', field: 'image' },
        { name: 'package_item', required: true, label: this.$t('store.view_package.package_item'), align: 'left', field: 'package_item' },
        { name: 'create_time', label: this.$t('createdtime'), align: 'left', field: 'create_time' },
        { name: 'update_time', label: this.$t('updatedtime'), align: 'left', field: 'update_time' },
        { name: 'action', label: this.$t('action'), align: 'center' }
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
    deletePackage (id) {
      const _this = this
      productPackageService.removePackage(id).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        });
        _this.reFresh()
      })
    },
    edit (pkg) {
      console.log(pkg)
    },
    add () {
      const _this = this
      _this.$q.dialog({
        component: PackageEditDialog
      }).onOk(res => {
        productPackageService.newPackage(res).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          });
          _this.reFresh()
        })
      })
    },
    getSearchList () {
      const _this = this
      productPackageService.getPackageList({}).then(_this.resetPageData)
    },
    getListPrevious () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        productPackageService.getListPrevOrNext(_this.pathname_previous).then(_this.resetPageData)
      }
    },
    getListNext () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        productPackageService.getListPrevOrNext(_this.pathname_next).then(_this.resetPageData)
      }
    },
    reFresh () {
      this.getSearchList()
    },
    resetPageData (res) {
      const _this = this
      _this.table_list = res.results;
      _this.pathname_previous = res.previous;
      _this.pathname_next = res.next;
      _this.count = res.count;
      _this.curPage = res.page;
    },
  },
  mounted () {
    const _this = this
    _this.getSearchList()
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

<style scoped>

</style>