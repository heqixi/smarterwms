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
          <q-btn-group push>
            <q-btn :label="$t('new')" icon="add" @click="openAddStoreDialog()">
              <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('newtip') }}</q-tooltip>
            </q-btn>
            <q-btn :label="$t('refresh')" icon="refresh" @click="reFresh()">
              <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
            </q-btn>
          </q-btn-group>
          <q-space />
          <q-input outlined rounded dense debounce="300" color="primary" v-model="filter" :placeholder="$t('search')" @blur="getSearchList()" @keyup.enter="getSearchList()">
            <template v-slot:append>
              <q-icon name="search" @click="getSearchList()" />
            </template>
          </q-input>
        </template>
        <template v-slot:body="props">
          <q-tr :props="props">
            <q-td :props="props" v-for="col in columns" :key="col.name">
              <template v-if="col.name === 'action'">
                <q-btn round flat push color="dark" icon="token"
                       @click="refresh(props.row.id)"
                >
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('store.view_storemanagement.refresh_token') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark" icon="autorenew"
                       @click="reauthorize(props.row.id)"
                >
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('store.view_storemanagement.reauthorize') }}</q-tooltip>
                </q-btn>
                <q-btn round flat push color="dark" icon="delete"
                       @click="deleteData(props.row.id)"
                >
                  <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('delete') }}</q-tooltip>
                </q-btn>
              </template>
              <template v-else-if="col.name === 'type'">
                {{storeTypeFormat(props.row[col.name])}}
              </template>
              <template v-else-if="col.name === 'platform'">
                {{platformFormat(props.row[col.name])}}
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
        <q-btn v-show="pathname_previous" flat push color="purple" :label="$t('previous')" icon="navigate_before" @click="getListPrevious()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('previous') }}</q-tooltip>
        </q-btn>
        <q-btn v-show="pathname_next" flat push color="purple" :label="$t('next')" icon-right="navigate_next" @click="getListNext()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('next') }}</q-tooltip>
        </q-btn>
        <q-btn v-show="!pathname_previous && !pathname_next" flat push color="dark" :label="$t('no_data')"></q-btn>
      </div>
      <q-dialog v-model="addStoreDialog" persistent>
        <q-card>
          <q-bar>
            <q-icon name="add_box" />
            <div>{{$t('new')}}</div>
            <q-space />
            <q-btn dense flat icon="close" v-close-popup>
              <q-tooltip>{{$t('index.close')}}</q-tooltip>
            </q-btn>
          </q-bar>
          <q-card-section>
            <q-input v-model="partnerId" label="PartnerID"/>
            <q-input v-model="partnerKey" label="PartnerKey"/>
          </q-card-section>
          <q-card-actions align="right" class="text-primary">
            <q-btn flat :label="$t('index.cancel')" v-close-popup />
            <q-btn flat :label="$t('index.submit')" v-close-popup @click="addStore()" />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </template>
    <q-dialog v-model="deleteForm">
      <q-card class="shadow-24">
        <q-bar class="bg-light-blue-10 text-white rounded-borders" style="height: 50px">
          <div>{{ $t('delete') }}</div>
          <q-space />
          <q-btn dense flat icon="close" v-close-popup>
            <q-tooltip content-class="bg-amber text-black shadow-4">{{ $t('index.close') }}</q-tooltip>
          </q-btn>
        </q-bar>
        <q-card-section style="max-height: 325px; width: 400px" class="scroll">{{ $t('deletetip') }}</q-card-section>
        <div style="float: right; padding: 15px 15px 15px 0">
          <q-btn color="white" text-color="black" style="margin-right: 25px" @click="deleteDataCancel()">{{ $t('cancel') }}</q-btn>
          <q-btn color="primary" @click="deleteDataSubmit()">{{ $t('submit') }}</q-btn>
        </div>
      </q-card>
    </q-dialog>
  </div>
</template>
<router-view />

<script>
import { LocalStorage } from 'quasar';
import storeService from 'pages/store/services/storeservice'

export default {
  name: 'Pagestoremanagement',
  data () {
    return {
      deleteid: '',
      deleteForm: false,
      partnerId: null,
      partnerKey: null,
      addStoreDialog: false,
      openid: '',
      login_name: '',
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
        { name: 'name', required: true, label: this.$t('store.view_storemanagement.name'), align: 'left', field: 'name' },
        { name: 'platform', required: true, label: this.$t('store.view_storemanagement.platform'), align: 'left', field: 'platform'},
        { name: 'uid', required: true, label: this.$t('store.view_storemanagement.uid'), align: 'left', field: 'uid' },
        { name: 'type', required: true, label: this.$t('store.view_storemanagement.type'), align: 'left', field: 'type' },
        { name: 'area', required: true, label: this.$t('store.view_storemanagement.area'), align: 'left', field: 'area' },
        { name: 'creater', required: true, label: this.$t('creater'), align: 'left', field: 'creater' },
        { name: 'create_time', required: true, label: this.$t('createdtime'), align: 'left', field: 'create_time' },
        { name: 'update_time', required: true, label: this.$t('updatedtime'), align: 'left', field: 'update_time' },
        { name: 'action', label: this.$t('action'), align: 'center' }
      ],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      }
    }
  },
  methods: {
    refresh (storeId) {
      const _this = this;
      storeService.refreshToken(storeId).then(res => {
        _this.$q.notify({
          message: 'Refresh Token Success',
          icon: 'check',
          color: 'green'
        });
      })
    },
    reauthorize (storeId) {
      storeService.getShopeeAuthUrl({
        storeId: storeId
      }).then(url => {
        window.open(url, '_self');
      }).finally(() => {
        this.partnerId = '';
        this.partnerKey = '';
      })
    },
    deleteDataCancel() {
      const _this = this;
      _this.deleteForm = false;
      _this.deleteid = 0;
    },
    deleteDataSubmit () {
      const _this = this;
      storeService.deleteStore(_this.deleteid).then(res => {
        _this.deleteDataCancel();
        _this.getList();
        _this.$q.notify({
          message: 'Success Edit Data',
          icon: 'check',
          color: 'green'
        });
      })
    },
    deleteData (id) {
      const _this = this;
      console.log('delete', id);
      _this.deleteForm = true;
      _this.deleteid = id;
    },
    addStore () {
      const _this = this;
      storeService.getShopeeAuthUrl({
        partnerId: _this.partnerId,
        partnerKey: _this.partnerKey
      }).then(url => {
        window.open(url, '_self');
      }).finally(() => {
        this.partnerId = '';
        this.partnerKey = '';
      });
    },
    openAddStoreDialog () {
      this.addStoreDialog = true;
    },
    storeTypeFormat (type) {
      if (type === 1) {
        return 'Merchant';
      } else if (type === 2) {
        return 'Shop';
      } else {
        return '';
      }
    },
    platformFormat (platform) {
      if (platform === 1) {
        return 'SHOPEE';
      } else {
        return ''
      }
    },
    getList () {
      const _this = this;
      storeService.getStorePages().then(res => {
        _this.table_list = res.results;
        _this.pathname_previous = res.previous;
        _this.pathname_next = res.next;
      })
    },
    getSearchList () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        storeService.getStorePages().then(res => {
          _this.table_list = res.results;
          _this.pathname_previous = res.previous;
          _this.pathname_next = res.next;
        })
      }
    },
    getListPrevious () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        storeService.getListPrevOrNext(_this.pathname_previous).then(res => {
          _this.table_list = res.results;
          _this.pathname_previous = res.previous;
          _this.pathname_next = res.next;
        })
      }
    },
    getListNext () {
      const _this = this;
      if (LocalStorage.has('auth')) {
        storeService.getListPrevOrNext(_this.pathname_next).then(res => {
          _this.table_list = res.results;
          _this.pathname_previous = res.previous;
          _this.pathname_next = res.next;
        })
      }
    },
    reFresh () {
      this.getList();
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
      _this.getList();
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
};
</script>
