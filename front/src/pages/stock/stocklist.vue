<template>
  <div class="q-pt-sm">
    <transition appear enter-active-class="animated fadeIn">
      <CommonTable
        ref="goodsTable"
        :table_list="table_list"
        :rowKey="rowKey"
        :columns="columns"
        :numRows="numRows"
        :loading="loading"
        :topButtons="topButtons"
        :filterFn="filteredRows"
        :getNextPage="getListNext"
        :searchFn="getSearchList"
        multiple-select="true"
        @refresh="refresh"
      />
    </transition>
  </div>
</template>

<script>
import { LocalStorage } from 'quasar'
import { getauth, putauth, postauth, deleteauth } from 'boot/axios_request'
import { STOCK_STATUS } from 'src/store/stock/types'
import CommonTable from '../../components/Share/commontable.vue'
import FilePicker from 'components/Share/filepicker'
import NewForm from 'components/Share/newForm'
import GoodsDeleteDialog from 'pages/goods/components/goodsDeleteDialog'
import NewFormDialog from 'components/Share/newFormDialog'

const UNMATCH_EXTERNAL_GOODS_CODE = '未匹配'

export default {
  name: 'Pagestocklist',
  data () {
    var _this = this
    return {
      pathname: 'stock/list/',
      listPath: 'goods/?tags=details&stockBin=1&goods=1&goods_stocks=aggregation&order=stock__shortage__desc',
      pathname_previous: '',
      pathname_next: '',
      numRows: -1,
      editColName: '',
      editGoodsCode: '',
      editValue: '',
      defaultImage: 'http://127.0.0.1:8008/media/uploads/009.webp',
      openid: '',
      login_name: '',
      authin: '',
      table_list: [],
      table_list_copy: [],
      search_task: undefined,
      separator: 'cell',
      loading: false,
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      editid: 0,
      goodsSelectedList: [], // Array of goods_code
      editMode: false,
      tags_list: [],
      rowKey: 'goods_code',
      selectUnmatch: false,
      externalStocks: [],
      externalStocksOptions: [],
      updateGodosGoods: {
        update_summay: '',
        update_with_external: false,
        update_goods_code: false
      },
      dupplicate_goods_form: {
        dupplicate_goods: '',
        merge: true
      },
      topButtons: [
        {
          name: 'new',
          label: '新增',
          tip: '新增库存记录',
          icon: 'add',
          click: () => {
            _this.$q.notify({
              message: '新增库存功能未实现',
              icon: 'close',
              color: 'negative'
            })
          }
        },
        {
          name: 'confirm',
          label: '表格导入',
          tip: '从表格中导入库存',
          click: selectedList => {
            _this.$q.dialog({
              component: FilePicker
            }).onOk(stocks => {
              _this.onExternalStockImport(stocks)
            })
          }
        }
      ],
      columns: [
        {
          name: 'goods_image',
          required: true,
          label: '图片',
          align: 'center',
          type: 'image',
          field: 'goods_image',
          style: 'width:100px'
        },
        {
          name: 'goods_code',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          type: 'text',
          field: 'goods_code',
          style: {
            width: '300px',
            maxWidth: '300px',
            whiteSpace: 'normal'
          },
          onUpdate: _this.updateGoodsCode
        },
        {
          name: 'stock_onhand',
          label: '现有库存',
          field: 'stocks',
          align: 'center',
          type: 'number',
          sortable: true,
          edit: true,
          fieldMap: stocks => {
            return stocks.stock_onhand
          },
          onUpdate: _this.updateStockOnHand,
          setter: (stocks, newStock) => {
            stocks.stock_onhand = newStock
          },
          style: { width: '100px', maxWidth: '120px' }
        },
        {
          name: 'stock_reserve',
          label: '预留库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          fieldMap: stocks => {
            return stocks.stock_reserve
          },
          sortable: true,
          style: { width: '80px', maxWidth: '100px' }
        },
        {
          name: 'stock_purchased',
          label: '采购中库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          fieldMap: stocks => {
            return stocks.stock_purchased
          },
          sortable: true,
          style: { width: '80px', maxWidth: '100px' }
        },
        {
          name: 'stock_ship',
          label: '出货库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          sortable: true,
          fieldMap: stocks => {
            return stocks.stock_ship
          },
          style: { width: '80px', maxWidth: '100px' }
        },
        {
          name: 'stock_damage',
          label: '损坏库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          sortable: true,
          edit: true,
          fieldMap: stocks => {
            return stocks.stock_damage
          },
          onUpdate: _this.updateStockDamage,
          setter: (stocks, newStock) => {
            stocks.stock_damage = newStock
          },
          style: { width: '100px', maxWidth: '120px' }
        },
        {
          name: 'stock_sorted',
          label: '已分拣库存',
          field: 'stocks',
          align: 'center',
          sortable: true,
          type: 'number',
          edit: false,
          fieldMap: stocks => {
            return stocks.stock_sorted
          },
          style: { width: '80px', maxWidth: '100px' }
        },
        {
          name: 'stock_adjust',
          label: '调整库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          sortable: true,
          edit: false,
          fieldMap: stocks => {
            return stocks.stock_sorted +
              stocks.stock_onhand -
              stocks.stock_ship -
              stocks.stock_damage
          },
          style: { width: '80px', maxWidth: '100px' }
        },
        {
          name: 'action',
          label: this.$t('action'),
          type: 'actions',
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          align: 'center',
          actions: [
            {
              name: 'delete',
              label: '删除',
              tip: '删除这条数据',
              click: goods => {
                console.log('delete goods, ', goods)
                _this.deleteGoods(goods.id)
              }
            }
          ]
        }
      ],
      selected: [],
      error: '请出入正整数'
    }
  },
  watch: {
    selected: function onSelect () {
      console.log('selected item ', this.selected)
    }
  },
  methods: {
    onExternalStockUpdate (goods, externalStock) {
      var _this = this
      return new Promise((resolve, reject) => {
        if (goods.goods_code !== externalStock.goods_code) {
          _this.updateGoodsCode(goods, externalStock.goods_code).then(goodeCode => {
            const goodsAfterUpdate = _this.table_list.find(goods => {
              return goods.goods_code === goodeCode
            })
            goods.goods_code = externalStock.goods_code
            _this.updateStockOnHand(goodsAfterUpdate, externalStock.stock_qty)
          })
        } else {
          if (goods.stock_onhand !== externalStock.stock_qty) {
            _this.updateStockOnHand(goods, externalStock.stock_qty)
          } else {
            console.log('on external stock update no need to update ')
          }
        }
      })
    },
    onUpdateStockBatch (selectStockList) {
      console.log('update stock of select ', selectStockList)
      var _this = this
      if (selectStockList.length <= 0) {
        _this.$q.notify({
          message: '你似乎没有选择任何库存记录',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      let formItems = [
        {
          name: 'update_summary',
          label: '待更新的库存',
          field: 'update_summay',
          edit: false
        }
      ]
      if (selectStockList[0].external_stock) {
        const replaceWithExternalCols = [
          {
            name: 'update_with_external',
            type: 'toggle',
            label: '更新为导入表格的库存',
            field: 'update_with_external'
          },
          {
            name: 'update_goods_code',
            type: 'toggle',
            label: '同时更新商品编码',
            field: 'update_goods_code'
          }
        ]
        formItems = formItems.concat(replaceWithExternalCols)
        _this.updateGodosGoods.update_with_external = true
      }
      _this.updateGodosGoods.update_summay = `你将更新 ${selectStockList.length} 个库存记录`
      _this.$q.dialog({
        component: NewFormDialog,
        newFormData: _this.updateGodosGoods,
        newFormItems: formItems
      }).onOk(() => {
        _this.updateStockBatch(selectStockList)
      })
    },
    onExternalStockImport (stocks) {
      var _this = this
      const filterStock = stocks.filter(stock => {
        return stock.qty >= 0 && stock.goods_code !== 0 && stock.goods_code !== ''
      })
      filterStock.forEach(stock => {
        stock.goods_code = stock.goods_code + ''
      })
      _this.externalStocks = filterStock
      _this.externalStocksOptions = filterStock
      _this.matchExternalGoods(_this.table_list)
      _this.topButtons.push(
        {
          name: 'update',
          label: '更新选中库存',
          tip: '从表格中更新选中库存',
          click: selectStockList => {
            _this.onUpdateStockBatch(selectStockList)
          }
        }
      )
      _this.topButtons.push(
        {
          name: 'selectUnmatch',
          label: '筛选未匹配库存',
          tip: '从表格中筛选匹配库存',
          click: selectStockList => {
            _this.selectUnmatch = !_this.selectUnmatch
            if (_this.selectUnmatch) {
              _this.table_list_copy = _this.table_list
              _this.table_list = _this.table_list.filter(goods => {
                return goods.external_stock.goods_code === UNMATCH_EXTERNAL_GOODS_CODE
              })
            } else {
              _this.table_list = _this.table_list_copy
            }
          }
        }
      )
      const externalGoodsCodeCol = {
        name: 'external_goods_code',
        label: '商品编码(导入)',
        align: 'center',
        type: 'select',
        field: 'external_stock',
        globalOptions: _this.externalStocksOptions,
        style: {
          width: '250px',
          whiteSpace: 'normal'
        },
        optionLabel: stock => {
          return stock ? stock.goods_code : UNMATCH_EXTERNAL_GOODS_CODE
        },
        filterFn (val, update) {
          _this.stockOptionFilter(val, update, externalGoodsCodeCol)
        },
        onInput (val) {
          console.log('on stock add', val)
        },
        onUpdate (goods, externalStock) {
          console.log('on external stock update ', goods, externalStock)
          return new Promise((resolve, reject) => {
            _this.onExternalStockUpdate(goods, externalStock)
            resolve(externalStock)
          })
        }
      }
      const externalGoodsStockCol = {
        name: 'external_stock_qty',
        label: '库存(导入)',
        field: 'external_stock',
        align: 'center',
        type: 'number',
        sortable: true,
        edit: true,
        fieldMap: stock => {
          return stock ? stock.qty : -1
        }
      }
      _this.columns.splice(4, 0, externalGoodsCodeCol)
      _this.columns.splice(5, 0, externalGoodsStockCol)
      // 自动更新匹配的库存
      const matchGoods = _this.table_list.filter(goods => {
        return goods.goods_code === goods.external_stock.goods_code
      })
      console.log('update match stock on import ', matchGoods)
      _this.updateStockBatch(matchGoods)
    },
    stockOptionFilter (val, update, col) {
      const _this = this
      if (val === '') {
        update(() => {
          col.globalOptions = _this.externalStocks
        })
        return
      }
      update(() => {
        col.globalOptions = _this.externalStocks.filter(stock => {
          return stock.goods_code.indexOf(val) >= 0
        })
      })
    },
    matchExternalGoods (goodsList) {
      if (!this.externalStocks && this.externalStocks.length <= 0) {
        return
      }
      goodsList.forEach(goods => {
        const matchStock = this.externalStocks.find(stock => {
          return stock.goods_code === goods.goods_code
        })
        if (matchStock) {
          goods.external_stock = matchStock
        } else {
          goods.external_stock = {
            goods_code: UNMATCH_EXTERNAL_GOODS_CODE,
            qty: -1
          }
        }
      })
    },
    updateGoodsTags (goods, newTags) {
      return new Promise((resolve, reject) => {
        console.log('update goods tag , ', newTags)
        const currentGoodsTags = goods.tags
        let tagToRemove = []
        let tagToAdd = []
        if (newTags == null || newTags.length <= 0) {
          tagToRemove = currentGoodsTags
          tagToAdd = []
        } else {
          tagToRemove = currentGoodsTags.filter(tag => {
            return (
              newTags.find(newTag => {
                return newTag.id === tag.id
              }) === undefined
            ) // 找不到的要删除
          }, [])
          // 需要增加的Tag
          tagToAdd = newTags.filter(tag => {
            return (
              currentGoodsTags.find(currentTag => currentTag.id === tag.id) ===
              undefined
            )
          }, [])
        }
        tagToRemove.forEach(tag => {
          const index = tag.goods.indexOf(goods.id)
          tag.partial = true
          if (index >= 0) {
            tag.goods.splice(index, 1)
          }
        })
        console.log(' tagToAdd  ', tagToAdd)
        tagToAdd.forEach(tag => {
          tag.partial = true
          tag.goods.push(goods.id)
        })

        const tagToUpdate = tagToRemove.concat(tagToAdd)
        console.log(' tagToUpdate ', tagToUpdate)
        putauth('goods/tag/', tagToUpdate).then(tagSaved => {
          console.log('update success', tagSaved)
          this.$q.notify({
            message: '商品标签保存成功',
            icon: 'check',
            color: 'green'
          })
          tagToRemove.forEach(tag => {
            for (var i = 0; i < goods.tags.length; i++) {
              if (tag.id == goods.tags[i].id) {
                goods.tags.splice(i, 1)
                goods.tagsOptions.push(tag)
              }
            }
          })
          tagToAdd.forEach(tag => {
            goods.tags.push(tag)
          })
          resolve(goods.tags)
        })
      })
    },
    deleteGoods (id) {
      console.log('delete goods of id ', id)
      var _this = this
      _this.loading = true
      deleteauth('goods/' + id + '/').then(res => {
        console.log('delete goods success ', res)
        for (var i = 0; i < _this.table_list.length; i++) {
          if (_this.table_list[i].id === id) {
            _this.table_list.splice(i, 1)
            break
          }
        }
        _this.loading = false
      }).catch(err => {
        console.log('delete goods fail ', err)
        if (err.response) {
          if (err.response.status === 403) {
            const details = err.response.data.details
            if (details.code === -1) {
              _this.deleteWithRelativeEntry(details)
            }
          } else {
            _this.$q.notify({
              message: '无法删除产品',
              icon: 'close',
              color: 'negative'
            })
          }
        } else {
          _this.$q.notify({
            message: '请求失败',
            icon: 'close',
            color: 'negative'
          })
        }
        _this.loading = false
      })
    },
    deleteWithRelativeEntry (data) {
      var _this = this
      _this.$q.dialog({
        component: GoodsDeleteDialog,
        data: data
      }).onOk(() => {
      })
    },
    newGoodsTag (goods) {
      console.log('newGoodsTag ', goods.goods_code)
      var _this = this
      _this.newFormItemData = {
        tag: '',
        goods_code: goods.goods_code
      }
      const onNewPurchaseCancel = () => {
        console.log('newPurchasePlan onNewDataCancel,')
        _this.newDataDialog = false
        _this.newFormItemData = undefined
        _this.onNewDataCancel = undefined
        _this.onNewDataSummit = undefined
      }
      _this.newFormItems = [
        {
          name: 'goods_code',
          field: 'goods_code',
          label: '商品编码',
          edit: false
        },
        {
          name: 'tag',
          field: 'tag',
          label: '商品标签',
          edit: true
        }
      ]
      return new Promise((resolve, reject) => {
        const onNewGoodsTagSummit = formData => {
          const tagToSave = {
            creater: _this.login_name,
            openid: _this.openid,
            goods: [goods.id],
            tag: formData.tag
          }
          console.log('tagToSave  ', tagToSave)
          postauth('goods/tag/', tagToSave)
            .then(tagSaved => {
              this.$q.notify({
                message: '商品标签保存成功',
                icon: 'check',
                color: 'green'
              })
              resolve(tagSaved)
              _this.table_list.forEach(goods => {
                goods.tagsOptions.puss(tagToSave)
              })
            })
            .catch(err => {
              this.$q.notify({
                message: '商品标签保存失败',
                icon: 'check',
                color: 'green'
              })
              reject(err)
            })
          _this.newDataDialog = false
          _this.newFormItemData = undefined
          _this.onNewDataCancel = undefined
          _this.onNewDataSummit = undefined
        }
        _this.onNewDataCancel = onNewPurchaseCancel
        _this.onNewDataSummit = onNewGoodsTagSummit
        _this.newDataDialog = true
      })
    },
    updateStockBatch (goodsList) {
      var _this = this
      const stock2Update = []
      goodsList.forEach(goods => {
        const stockObj = {
          creater: _this.login_name,
          openid: _this.openid,
          goods: goods.id,
          stock_status: STOCK_STATUS.on_hand,
          stock_qty: goods.external_stock.qty
        }
        if (goods.external_stock) {
          if (_this.updateGodosGoods.update_goods_code) {
            if (goods.goods_code !== goods.external_stock.goods_code) {
              stockObj.new_goods_code = goods.external_stock.goods_code
            }
          }
          stock2Update.push(stockObj)
        } else {
          _this.$q.notify({
            message: `商品库存有误， 编码 ${goods.goods_code}`,
            icon: 'close',
            color: 'negative'
          })
          throw new Error(`illegal stock of code ${goods.goods_code}`)
        }
      })
      return new Promise((resolve, reject) => {
        postauth('stock/list/', stock2Update).then(stockSaved => {
          console.log('save stock bactch success ', stockSaved, stock2Update)
          stock2Update.forEach(stockRecord => {
            const goodsOfStock = _this.table_list.find(goods => {
              return goods.id === stockRecord.goods
            })
            const stocksOfGoods = goodsOfStock.stocks
            _this.$set(stocksOfGoods, 'stock_onhand', stockRecord.stock_qty)
            // for (var i = 0; i < _this.table_list.length; i++) {
            //   if (_this.table_list[i].id === stockRecord.goods) {
            //     const stocks = _this.table_list[i].stocks
            //     _this.$set(stocks, 'stock_onhand', stockRecord.stock_qty)
            //     break
            //   }
            // }
          })
          resolve(stock2Update)
        })
      })
    },
    getGoodsOfCode (goodsCode) {
      var _this = this
      _this.loading = true
      return new Promise((resolve, reject) => {
        getauth('goods/?search=' + goodsCode).then(res => {
          _this.loading = false
          if (res !== undefined) {
            resolve(res.results)
          }
        }).catch(err => {
          _this.loading = false
          _this.$q.notify({
            message: `出错了  ${err}`,
            icon: 'close',
            color: 'negative'
          })
        })
      })
    },
    updateGoodsCode (goods, newGoodsCode) {
      var _this = this
      return new Promise((resolve, reject) => {
        if (goods.goods_code !== newGoodsCode) {
          const formDatga = {
            id: goods.id,
            goods_code: newGoodsCode,
            partial: true
          }
          _this.loading = true
          return new Promise((resolve, reject) => {
            _this.getGoodsOfCode(newGoodsCode).then(goodsList => {
              const exist = goodsList.find(goods => {
                return goods.goods_code === newGoodsCode
              })
              if (exist) {
                _this.loading = false
                _this.handleDupplicateGoodsCode(goods, exist).then(res => {
                  if (res.merge) {
                    for (var i = 0; i < _this.table_list.length; i++) {
                      if (_this.table_list[i].id === goods.id) {
                        _this.table_list.splice(i, 1)
                      }
                    }
                    for (var j = 0; j < _this.table_list_copy.length; j++) {
                      if (_this.table_list_copy[j].id === goods.id) {
                        _this.table_list_copy.splice(j, 1)
                      }
                    }
                  } else {
                    resolve(res.goods_code)
                  }
                })
              } else {
                console.log(' new goods code is ok', newGoodsCode)
                putauth('goods/' + goods.id + '/', formDatga).then(res => {
                  console.log('update goods code success ', res)
                  _this.loading = false
                  goods.goods_code = newGoodsCode
                  resolve(newGoodsCode)
                }).catch(err => {
                  _this.loading = false
                  _this.$q.notify({
                    message: `更新商品编码失败 ${err}`,
                    icon: 'close',
                    color: 'negative'
                  })
                })
              }
            })
          })
        } else {
          resolve(goods.goods_code)
        }
      })
    },
    handleDupplicateGoodsCode (goods, existGoods) {
      console.log('handle dupplicate goods code ', goods, existGoods)
      var _this = this
      _this.$q.notify({
        message: '产品已存在',
        icon: 'close',
        color: 'negative',
        timeout: 3000
      })
      const formItems = [
        {
          name: 'dupplicate_goods',
          label: '重复商品编码',
          field: 'dupplicate_goods',
          edit: false
        },
        {
          name: 'merge_goods',
          type: 'toggle',
          label: '合并到此商品',
          field: 'merge',
          edit: true
        }
      ]
      _this.dupplicate_goods_form.dupplicate_goods = existGoods.goods_code
      return new Promise((resolve, reject) => {
        _this.$q.dialog({
          component: NewFormDialog,
          title: '商品名称重复',
          newFormData: _this.dupplicate_goods_form,
          newFormItems: formItems
        }).onOk(() => {
          const merge = _this.dupplicate_goods_form.merge
          const formData = {
            merge_to: existGoods.id,
            merge: true
          }
          if (merge) {
            _this.loading = true
            putauth('goods/' + goods.id + '/', formData).then(res => {
              _this.loading = false
              console.log('update and merge goods code success ', res)
              resolve({
                merge: true,
                goods_code: existGoods.goods_code
              })
            }).catch(err => {
              _this.loading = false
              reject(err)
            })
          } else {
            resolve({
              merge: false,
              goods_code: goods.goods_code
            })
          }
        })
      })
    },
    updateStockOnHand (goods, num) {
      var _this = this
      console.log('updateStockOnHand ', goods.id, goods.goods_code, num)
      const stockObj = {
        creater: _this.login_name,
        openid: _this.openid,
        goods: goods.id,
        stock_status: STOCK_STATUS.on_hand,
        stock_qty: num
      }
      return new Promise((resolve, reject) => {
        postauth('stock/list/', stockObj).then(stockSaved => {
          console.log('create / update stock obj success ', stockSaved)
          goods.stocks.stock_onhand = num
          resolve(num)
        })
      })
    },
    updateStockDamage (goods, num) {
      var _this = this
      console.log('updateStockDamage ', goods, num)
      const stockObj = {
        creater: _this.login_name,
        openid: _this.openid,
        goods: goods.id,
        stock_status: STOCK_STATUS.damage,
        stock_qty: num
      }
      return new Promise((resolve, reject) => {
        postauth('stock/list/', stockObj).then(stockSaved => {
          console.log('create / update stock obj success ', stockSaved)
          const diff = num - goods.stocks.stock_damage
          if (diff > 0) {
            const stocks = goods.stocks
            const stockOnHand = stocks.stock_onhand - Math.min(diff, stocks.stock_onhand)
            _this.$set(stocks, 'stock_onhand', stockOnHand)
          }
          goods.stocks.stock_damage = num
          resolve(num)
        })
      })
    },
    filteredRows (goods, searchTerm) {
      if (goods.goods_code === undefined) {
        console.log('found illegal goods ', goods)
      }
      const codeMatch = goods.goods_code.indexOf(searchTerm) > -1
      let tagMatch = false
      for (var i = 0; i < goods.tags.length; i++) {
        if (goods.tags[i].tag.indexOf(searchTerm) > -1) {
          tagMatch = true
          break
        }
      }
      let externalStockMatch = false
      if (goods.external_stock) {
        externalStockMatch = goods.external_stock.goods_code.indexOf(searchTerm) > -1
      } else {
        console.log('erternal stock no found', goods)
      }
      const nameMatch = goods.goods_name.indexOf(searchTerm) > -1
      return codeMatch || tagMatch || nameMatch || externalStockMatch
    },
    getList () {
      var _this = this
      _this.loading = true
      getauth(_this.listPath, {})
        .then(res => {
          console.log('stock of goods ', res)
          _this.numRows = res.count
          _this.table_list = res.results
          _this.matchExternalGoods(_this.table_list)
          _this.pathname_previous = res.previous
          _this.pathname_next = res.next
          _this.loading = false
        })
        .catch(err => {
          console.error('get stock list fail ', err)
          _this.loading = false
          _this.$q.notify({
            message: err.detail,
            icon: 'close',
            color: 'negative'
          })
        })
    },
    getSearchList (searchTerm) {
      var _this = this
      return new Promise((resolve, reject) => {
        if (searchTerm.length <= 0) {
          console.log('must seachch something')
          reject('can no search empty string')
          return
        }
        if (_this.table_list.length >= _this.numRows) {
          console.log(' no need to get Search List ', searchTerm)
          reject('no need to search')
          return
        }
        if (_this.search_task) {
          console.log('clear time out')
          clearTimeout(_this.search_task)
          _this.search_task = undefined
        }
        _this.search_task = setTimeout(() => {
          console.log('start search task')
          _this.loading = true
          if (LocalStorage.has('auth')) {
            getauth(_this.listPath + '&search=' + searchTerm, {})
              .then(res => {
                clearTimeout(_this.search_task) // 防止重复搜索
                const data = res.results
                _this.matchExternalGoods(data)
                data.forEach(goods => {
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
                reject('get data fail')
                _this.loading = false
                clearTimeout(_this.search_task)
                _this.$q.notify({
                  message: err.detail,
                  icon: 'close',
                  color: 'negative'
                })
              })
          }
        }, 500)
      })
    },
    getListPrevious () {
      // TODO
      console.log('getListPrevious')
    },
    refresh () {
      this.getList()
      if (this.externalStocks) {
        this.matchExternalGoods(this.table_list)
      }
    },
    getListNext (size) {
      // TODO
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
          getauth(path, {})
            .then(res => {
              _this.loading = false
              const data = res.results
              console.log('get next page before, num rows', res)
              _this.matchExternalGoods(data)
              data.forEach(goods => {
                const exist = _this.table_list.find(exitGoods => {
                  return exitGoods.goode_code === goods.goods_code
                })
                if (exist !== undefined) {
                  console.warn('duplicate goods find ', goods.goods_code)
                } else {
                  _this.table_list.push(goods)
                }
              })
              _this.pathname_previous = res.previous
              _this.pathname_next = res.next
              resolve('success')
            })
            .catch(err => {
              _this.loading = false
              reject('get next page fail')
              _this.$q.notify({
                message: err.detail,
                icon: 'close',
                color: 'negative'
              })
            })
        }
      })
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
      _this.getList()
    } else {
      _this.authin = '0'
    }
  },
  props: ['height'],
  components: {
    CommonTable,
    FilePicker,
    NewForm,
    GoodsDeleteDialog
  }
}
</script>
