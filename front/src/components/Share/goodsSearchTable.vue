<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <CommonTable
        ref="table"
        :table_list="table_list"
        :rowKey="rowKey"
        :columns="columns"
        :numRows="numRows"
        :topButtons="topButtons"
        :loading="loading"
        :getNextPage="getListNext"
        :filterFn="filteredRows"
        :searchFn="getSearchList"
        :preSearch="preSearch"
        :sortFn="sortFn"
        :defaultSelected="defaultSelected"
        :multiple-select="multipleSelect"
        :rowsPerPage="rowsPerPage"
        :hideSearch="hideSearch"
        tableHeight="700px"
        @newForm="onNewGoods"
        @refresh="reFresh">
      </CommonTable>
    </transition>
    <slot name="newData"></slot>
  </div>
</template>
<router-view/>

<script>
import { getauth } from 'boot/axios_request'
import { LocalStorage } from 'quasar'
import CommonTable from './commontable.vue'
import NewForm from './newForm.vue'

export default {
  name: 'GoodsSearchTable',
  data () {
    return {
      openid: '',
      allPurchasePlan: [],
      login_name: '',
      authin: '0',
      pathname: 'goods/',
      pathname_previous: '',
      pathname_next: '',
      loading: false,
      height: '',
      numRows: 0,
      table_list: [],
      rowKey: 'id',
      search_task: undefined,
      supplier_list: [],
      filter: '',
      token: LocalStorage.getItem('openid')
    }
  },
  methods: {
    resort (sortFn, goods) {
      // 外部调用
      this.table_list.sort(sortFn)
      for (let i = this.table_list.length - 1; i >= 0; i--) {
        if (this.table_list[i].id === goods.id) {
          this.table_list.splice(i, 1)
        }
      }
      for (let i = this.table_list.length - 1; i >= 0; i--) {
        if (sortFn(this.table_list[i], goods) <= 0) {
          this.table_list.splice(i, 0, goods)
          break
        }
      }
    },
    clearSelect () {
      this.$refs.table.clearSelect()
    },
    clearGoods (goodsList) {
      for (let i = this.table_list.length - 1; i >= 0; i--) {
        if (goodsList.find(goods => { return goods.id === this.table_list[i].id })) {
          this.table_list.splice(i, 1)
        }
      }
    },
    setLoading () {
      this.loading = true
    },
    clearLoading () {
      this.loading = false
    },
    addSelect (goodsList) {
      console.log('goods search table add select ', goodsList)
      this.$refs.table.addSelected(goodsList.map(goods => { return goods.id }))
    },
    prependGoods (goods) {
      this.table_list.unshift(goods)
    },
    getAllLoadGoods () {
      return this.table_list
    },
    getList (searchTerm) {
      var _this = this
      _this.loading = true

      let path = _this.pathname +
        '?purchases=details&supplier=details&goods_stocks=aggregation&variants=details&order=stock__shortage__desc'
      if (_this.path) {
        path = _this.path
      }
      if (this.exclude && this.exclude.length > 0) {
        const excludeGoods = this.exclude.join('&exclude=')
        path = path + '&exclude=' + excludeGoods
      }
      if (searchTerm) {
        path += '&search=' + searchTerm
      }
      getauth(path, {})
        .then(res => {
          console.log('get goods with purchase info ', res)
          _this.numRows = res.count
          _this.table_list = res.results
          _this.table_list.sort(_this.sortFn)
          _this.table_list.forEach(goods => {
            goods.purchase_num = Math.max(goods.stocks.stock_reserve - goods.stocks.stock_onhand - goods.stocks.stock_purchased, 0)
          })
          _this.supplier_list = res.supplier_list
          _this.pathname_previous = res.previous
          _this.pathname_next = res.next
          _this.loading = false
          // setTimeout(() => {
          //   if (_this.defaultSelected) {
          //     console.log('add default select ', _this.defaultSelected)
          //     _this.$refs.table.addSelected(_this.defaultSelected)
          //   } else {
          //     console.log('no need add default select ')
          //   }
          // }, 100)
        })
        // .catch(err => {
        //   _this.loading = false
        //   _this.$q.notify({
        //     message: '出错了，请重试',
        //     icon: 'close',
        //     color: 'negative'
        //   })
        // })
    },
    getSearchList (searchTerm) {
      const _this = this
      return new Promise((resolve, reject) => {
        if (searchTerm === _this.preSearch) {
          console.log('no need to search again for pre Search')
          reject('no need to search again for pre Search')
          return
        }
        if (searchTerm.length <= 0) {
          console.log('must seachch something')
          reject('can no search empty string')
          return
        }
        if (_this.table_list.length >= _this.numRows && !_this.preSearch) {
          console.log(' no need to get Search List ', searchTerm)
          reject('no need to search')
          return
        }
        let delay = 100
        if (_this.search_task) {
          console.log('clear time out')
          clearTimeout(_this.search_task)
          _this.search_task = undefined
          delay = 500
        }
        _this.search_task = setTimeout(() => {
          console.log('start search for ', searchTerm)
          if (LocalStorage.has('auth')) {
            _this.loading = true
            getauth(_this.pathname + '?purchases=details&supplier=details&goods_stocks=aggregation&order=stock__shortage__desc&search=' + searchTerm, {})
              .then(res => {
                clearTimeout(_this.search_task) // 防止重复搜索
                console.log(`seach result for ${searchTerm} `, res.results)
                const data = res.results
                data.forEach(goods => {
                  goods.purchase_num = Math.max(goods.stocks.stock_reserve - goods.stocks.stock_onhand - goods.stocks.stock_purchased, 0)
                  console.log('purchase num ', goods.purchase_num)
                  const exist = _this.table_list.find(exitGoods => {
                    return exitGoods.id === goods.id
                  })
                  if (exist !== undefined) {
                    console.warn('duplicate goods find ', goods.goods_code)
                  } else {
                    _this.table_list.push(goods)
                  }
                })
                _this.loading = false
                resolve(data)
              })
              .catch(err => {
                clearTimeout(_this.search_task) // 防止重复搜索
                _this.loading = false
                _this.$q.notify({
                  message: err.detail,
                  icon: 'close',
                  color: 'negative'
                })
              })
          }
        }, delay)
      })
    },
    filteredRows (goods, searchTerm) {
      const codeMatch = goods.goods_code.indexOf(searchTerm) > -1
      const nameMatch = goods.goods_name.indexOf(searchTerm) > -1
      return codeMatch || nameMatch
    },
    getListPrevious () {
      var _this = this
      _this.loading = true
      if (LocalStorage.has('auth')) {
        getauth(_this.pathname_previous, {})
          .then(res => {
            _this.table_list = res.results
            _this.pathname_previous = res.previous
            _this.pathname_next = res.next
            _this.loading = false
          })
          .catch(err => {
            _this.loading = false
            _this.$q.notify({
              message: err.detail,
              icon: 'close',
              color: 'negative'
            })
          })
      } else {
      }
    },
    getListNext (size) {
      var _this = this
      this.loading = true
      let path = _this.pathname_next
      const url = new URL('http://' + path)
      const urlParams = new URLSearchParams(url.search)
      if (size > 0) {
        urlParams.set('limit', size)
        path = 'goods/?' + urlParams.toString()
      }
      console.log('get next list stock ', path)
      return new Promise((resolve, reject) => {
        if (LocalStorage.has('auth')) {
          _this.loading = true
          getauth(path, {})
            .then(res => {
              const data = res.results
              data.forEach(goods => {
                const exist = _this.table_list.find(exitGoods => {
                  return exitGoods.goode_code === goods.goods_code
                })
                if (exist !== undefined) {
                  console.warn('duplicate goods find ', goods.goods_code)
                } else {
                  goods.purchase_num = goods.stocks.stock_reserve - goods.stocks.stock_onhand
                  _this.table_list.push(goods)
                }
              })
              _this.pathname_previous = res.previous
              _this.pathname_next = res.next
              _this.loading = false
              resolve('next page')
            })
            .catch(err => {
              _this.loading = false
              _this.$q.notify({
                message: err.detail,
                icon: 'close',
                color: 'negative'
              })
            })
        } else {
          _this.$q.notify({
            message: '请重新登录',
            icon: 'close',
            color: 'negative'
          })
        }
      })
    },
    onNewGoods () {
      console.log('new goods ')
    },
    reFresh () {
      var _this = this
      _this.getList()
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
      if (_this.goods) {
        _this.table_list = _this.goods
      }
      if (!_this.emptyData && !_this.table_list.length > 0) {
        _this.getList(_this.preSearch)
      }
    } else {
      _this.authin = '0'
    }
    console.log('row perpage ', this.rowsPerPage, ', hide search ', this.hideSearch)
  },
  mounted () {
    var _this = this
    if (_this.$q.platform.is.electron) {
      _this.height = String(_this.$q.screen.height - 290) + 'px'
    } else {
      _this.height = _this.$q.screen.height - 290 + '' + 'px'
    }
  },
  updated () {
  },
  destroyed () {
  },
  props: [
    'topButtons',
    'columns',
    'preSearch',
    'path',
    'emptyData',
    'sortFn',
    'defaultSelected',
    'multipleSelect',
    'exclude',
    'goods',
    'rowsPerPage',
    'hideSearch'
  ],
  components: {
    CommonTable,
    NewForm
  }
}
</script>

<style>
.q-uploader {
  width: 100% !important;
}

.q-uploader__header {
  width: 100% !important;
}

.q-uploader__list {
  width: 100% !important;
}
</style>
