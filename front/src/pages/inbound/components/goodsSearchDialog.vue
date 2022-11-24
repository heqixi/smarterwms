<template>
  <div>
    <transition appear enter-active-class="animated fadeIn">
      <GoodsSearchTable
        ref="table"
        :columns="columns"
        :topButtons="topButtons"
        :exclude="exclude"
        :sort-fn="sortGoodsByDefaultPurchasePlan"
        multiple-select="true">
        <template v-slot:newData>
          <q-dialog v-model="newDataDialog">
            <NewForm
              :items="newFormItems"
              :newFormData="newFormData"
              @newDataSummit="onNewDataSummit"
              @newDataCancel="onNewDataCancel"
            />
          </q-dialog>
        </template>
      </GoodsSearchTable>
    </transition>
  </div>
</template>
<router-view/>

<script>
import { STOCK_STATUS } from 'src/store/stock/types'
import { getauth, postauth, putauth } from 'boot/axios_request'
import { LocalStorage } from 'quasar'
import GoodsSearchTable from 'src/components/Share/goodsSearchTable.vue'
import NewForm from 'src/components/Share/newForm'
import PurchaseSelectedDialog from 'pages/inbound/components/purchaseSearchForGoods'
import GoodsSearchForSupplier from 'pages/inbound/components/goodsSearchForSupplier'

export default {
  name: 'goodsSearchDialog',
  data () {
    var _this = this
    return {
      openid: '',
      login_name: '',
      authin: '0',
      pathname: 'goods/',
      pathname_previous: '',
      pathname_next: '',
      loading: false,
      height: '',
      numRows: 0,
      table_list: [],
      purchases: undefined,
      search_task: undefined,
      supplier_list: [],
      newDataDialog: false,
      newFormItems: [],
      onNewDataSummit: undefined,
      onNewDataCancel: undefined,
      newFormData: {},
      allPurchasePlan: [],
      noPurchaseGoods: [],
      topButtons: [
        {
          name: 'confirm',
          label: '一键采购',
          tip: '一键采购短缺库存',
          click: selectedList => {
            console.log('purchase selectedList, ', selectedList.length)
            if (selectedList.length <= 0) {
              _this.purchaseShortageGoods()
            } else {
              _this.getGoodsPurchases(selectedList)
            }
          }
        },
        {
          name: 'cancel',
          label: '取消',
          tip: '下次再选',
          click: selectedList => {
            console.log('cancel selectedList, ', selectedList.length)
            _this.$emit('onCancel')
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
          style: {
            maxWidth: '150px',
            width: '150px'
          }
        },
        {
          name: 'goods_code',
          required: true,
          label: this.$t('goods.view_goodslist.goods_code'),
          align: 'center',
          type: 'text',
          field: 'goods_code',
          edit: false,
          style: {
            maxWidth: '200px',
            width: '200px',
            whiteSpace: 'normal'
          }
        },
        {
          name: 'stock_on_hand',
          label: '现有库存',
          field: 'stocks',
          align: 'center',
          type: 'number',
          sortable: true,
          style: {
            maxWidth: '100px',
            width: '100px'
          },
          fieldMap: stocks => {
            return stocks.stock_onhand
          },
          onUpdate: _this.updateStockOnHand,
          setter: (stocks, newStock) => {
            stocks.stock_onhand = newStock
          }
        },
        {
          name: 'stock_reserve',
          label: '短缺',
          field: 'stocks',
          type: 'number',
          align: 'center',
          style: {
            maxWidth: '100px',
            width: '100px'
          },
          fieldMap: stocks => {
            return Math.max(stocks.stock_reserve - stocks.stock_onhand - stocks.stock_purchased, 0)
          },
          sortable: true
        },
        {
          name: 'stock_purchased',
          label: '采购中库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          style: {
            maxWidth: '100px',
            width: '100px'
          },
          fieldMap: stocks => {
            return stocks.stock_purchased
          },
          sortable: true
        },
        {
          name: 'stock_ship',
          label: '出货库存',
          field: 'stocks',
          type: 'number',
          align: 'center',
          style: {
            maxWidth: '100px',
            width: '100px'
          },
          sortable: true,
          fieldMap: stocks => {
            return stocks.stock_ship
          }
        }
      ],
      filter: '',
      token: LocalStorage.getItem('openid')
    }
  },
  methods: {
    async purchaseShortageGoods () {
      const _this = this
      const shortageGoods = await _this.getAndFilterShortageGoods(_this.$refs.table.getAllLoadGoods())
      if (shortageGoods.length <= 0) {
        this.$q.notify({
          message: '暂无库存短缺的货物',
          icon: 'check',
          color: 'green'
        })
        return
      }
      await _this.getGoodsPurchases(shortageGoods)
    },
    async getAndFilterShortageGoods (loadedGoods) {
      loadedGoods.forEach(goods => {
        goods.stocks.shortage = goods.stocks.stock_reserve - (goods.stocks.stock_onhand + goods.stocks.stock_purchased)
      })
      loadedGoods.sort((x, y) => { return y.stocks.shortage - x.stocks.shortage })
      var allShortageGoods
      if (loadedGoods[loadedGoods.length - 1].shortage > 0) {
        // Load all shortage stock
        allShortageGoods = await getauth('goods/?&goods_stocks=aggregation&order=stock__shortage__desc&filter=stock__shortage').results
        console.log('get all shortage goods ', allShortageGoods)
      } else {
        allShortageGoods = loadedGoods.filter(goods => { return goods.stocks.shortage > 0 })
      }
      return allShortageGoods
    },
    async getGoodsPurchases (goodsList) {
      console.log('get shortage goods purchase ', goodsList)
      const goodsFilter = goodsList.map(goods => { return goods.id }).join('&goods=')
      const purchases = await getauth('supplier/purchase?goods_settings=true&goods=' + goodsFilter)
      console.log('shortage goods purchase purchase ', purchases)
      goodsList.forEach(goods => {
        purchases.forEach(purchase => {
          const matchPurchaseSettings = purchase.goods_settings.find(s => { return s.goods === goods.id })
          if (matchPurchaseSettings) {
            if (!goods.purchase) {
              goods.purchase = purchase
              goods.purchase_settings = matchPurchaseSettings
            } else if (goods.purchase_settings.level > matchPurchaseSettings.level) {
              goods.purchase = purchase
              goods.purchase_settings = matchPurchaseSettings
            }
          }
        })
      })
      const noPurchaseGoods = goodsList.filter(goods => { return !goods.purchase })
      const purchaseReadyGoods = goodsList.filter(goods => { return goods.purchase })
      console.log('all goods ', goodsList.length, ',purchase ready ', purchaseReadyGoods.length)
      if (noPurchaseGoods.length > 0) {
        this.$q.notify({
          message: '请先完善采购链接',
          icon: 'check',
          color: 'green'
        })
        await this.selectPurchaseForGoods(noPurchaseGoods, () => {
          const purchaseReadyGoods = goodsList.filter(goods => {
            return goods.purchase
          })
          console.log('after select purchase, ready ', purchaseReadyGoods.length)
          this.onGoodsSelect(purchaseReadyGoods)
        })
      } else {
        this.onGoodsSelect(purchaseReadyGoods)
      }
    },
    sortGoodsByDefaultPurchasePlan (goodsLeft, goodsRight) {
      if (goodsLeft.stocks && goodsLeft.stocks.stock_reserve <= 0) {
        return 1
      }
      let purchaseNameLeft = ''
      if (goodsLeft.purchases && goodsLeft.purchases.length > 0) {
        purchaseNameLeft = goodsLeft.purchases[0].supplier.supplier_name
      }
      let purchaseNameRight = ''
      if (goodsRight.purchases && goodsRight.purchases.length > 0) {
        purchaseNameRight = goodsRight.purchases[0].supplier.supplier_name
      }
      if (purchaseNameLeft === purchaseNameRight) {
        return 0
      }
      // if (!purchaseNameLeft || !purchaseNameRight) {
      //   console.log('something go wrong, ', goodsLeft, purchaseNameLeft, goodsRight, purchaseNameRight)
      // }
      if (!purchaseNameLeft || purchaseNameLeft.length === 0) {
        return 1
      }
      return purchaseNameLeft < purchaseNameRight ? -1 : 1
    },
    addGoodsToPurchasePlan (purchasePlan, goodsIds) {
      console.log('addGoodsToPurchasePlan', purchasePlan, goodsIds)
      const formData = {
        id: purchasePlan.id,
        goods: goodsIds,
        add: true
      }
      return new Promise((resolve, reject) => {
        putauth('supplier/purchase/' + purchasePlan.id + '/', formData).then(res => {
          console.log('add goods to purchase success ', res)
          resolve(purchasePlan)
        }).catch(err => {
          this.$q.notify({
            message: '采购方案保存失败',
            icon: 'check',
            color: 'green'
          })
        })
      })
    },
    getPurchasePlan () {
      var _this = this
      getauth('supplier/purchase/?supplier=details', {}).then(purchaseList => {
        console.log('get purchase list ', purchaseList)
        _this.allPurchasePlan = purchaseList
      })
    },
    setLoading () {
      this.$refs.table.setLoading()
    },
    clearLoading () {
      this.$refs.table.clearLoading()
    },
    resortGoods (goods) {
      this.$refs.table.resort(this.sortGoodsByDefaultPurchasePlan, goods)
    },
    purchaseOptionFilter (val, update, col) {
      const _this = this
      if (val === '') {
        update(() => {
          col.globalOptions = _this.allPurchasePlan
        })
        return
      }
      update(() => {
        col.globalOptions = _this.allPurchasePlan.filter(purchase => {
          const nameMatch = purchase.supplier.supplier_name.indexOf(val) > -1
          const tagMatch = purchase.tag.indexOf(val) > -1
          return nameMatch || tagMatch
        })
      })
    },
    updateStockOnHand (goods, num) {
      var _this = this
      console.log('updateStockOnHand ', goods, num)
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
    async selectPurchaseForGoods (noPurchaseGoods, callBack) {
      var _this = this
      console.log(' select purchase for goods ', noPurchaseGoods)
      let getProduct = true
      for (let i = 0; i < noPurchaseGoods.length; i++) {
        if (noPurchaseGoods[i].products === undefined) {
          getProduct = false
          break
        }
      }
      if (!getProduct) {
        _this.setLoading()
        const goodsIds = noPurchaseGoods.map(goods => { return goods.id }).join('&id_in=')
        const path = `goods/?products=true&id_in=${goodsIds}&offset=0&limit=${noPurchaseGoods.length}`
        const response = await getauth(path, {})
        _this.clearLoading()
        console.log(' get product of for goods res', response)
        const productOfGoods = response.results
        noPurchaseGoods.forEach(goods => {
          const matchGoods = productOfGoods.find(g => { return g.id === goods.id })
          if (matchGoods) {
            goods.products = matchGoods.products
          } else {
            goods.products = []
          }
        })
      }
      _this.$q.dialog({
        component: GoodsSearchForSupplier,
        refName: 'viewDataDialog',
        searchPath: 'goods/?purchases=details',
        goods: noPurchaseGoods,
        additionalTopButtons: [
          {
            name: 'add_purchase',
            label: '添加供应商',
            tip: '添加供应商',
            selectAutoClear: true,
            click: selectedGoods => {
              console.log('selectedList, ', selectedGoods.length)
              if (selectedGoods.length <= 0) {
                this.$q.notify({
                  message: '请先选择货物',
                  icon: 'check',
                  color: 'green'
                })
                return
              }
              _this.selectPurchasePlan(selectedGoods, noPurchaseGoods)
            }
          }
        ]
      }).onOk(operation => {
        if (operation.action === 'addPurchase') {
          const goodsList = operation.goods
          _this.selectPurchasePlan(goodsList, noPurchaseGoods)
        }
        console.log('on goods search for supplier ok')
        if (callBack) {
          callBack()
        }
      })
    },
    async selectPurchasePlan (goodsList, noPurchaseGoods) {
      var _this = this
      if (!_this.purchases) {
        _this.loading = true
        _this.purchases = await getauth('supplier/purchase/?supplier=true&goods_settings=true', {})
        _this.loading = false
      }
      _this.$q.dialog({
        component: PurchaseSelectedDialog,
        refName: 'purchaseSelectDialog',
        purchases: _this.purchases
      }).onOk((purchase) => {
        console.log('on select purchase ', purchase)
        const goods2Add = []
        goodsList.forEach(goods => {
          _this.$set(goods, 'purchase', purchase)
          if (!goods.purchases) {
            goods.purchases = []
          }
          goods.purchases.push(purchase)
          for (let i = noPurchaseGoods.length - 1; i >= 0; i--) {
            if (noPurchaseGoods[i].id === goods.id) {
              noPurchaseGoods.splice(i, 1)
              break
            }
          }
          const goodsExist = purchase.goods_settings.find(settings => {
            return goods.id === settings.goods
          })
          if (goodsExist) {
            console.error('goods already has this purchase plan ', goods, purchase)
          } else {
            goods2Add.push(goods.id)
          }
        })
        console.log('after select purchase plan ', noPurchaseGoods.length)
        if (goods2Add.length > 0) {
          _this.addGoodsToPurchasePlan(purchase, goods2Add).then(res => {
            // goods2Add.forEach(goods => {
            //   purchase.goods.push(goods)
            // })
          })
        } else {
          console.log('no thing to add')
        }
      })
    },
    // newPurchasePlan (goods) {
    //   console.log('newPurchasePlan ', goods)
    //   var _this = this
    //   const supplierOptions = _this.supplier_list
    //   const newFormData = {
    //     tag: '',
    //     url: '',
    //     supplier: undefined,
    //     price: 0,
    //     default: false
    //   }
    //   const onNewPurchaseCancel = () => {
    //     console.log('newPurchasePlan onNewDataCancel,')
    //     _this.newDataDialog = false
    //   }
    //   return new Promise((resolve, reject) => {
    //     const onNewPurchaseSummit = formData => {
    //       const newPurchasePlan = {
    //         tag: formData.tag,
    //         creater: _this.login_name,
    //         openid: _this.openid,
    //         goods: [goods.id],
    //         supplier: formData.supplier.id,
    //         price: formData.price,
    //         url: formData.url,
    //         default: formData.default
    //       }
    //       _this.newDataDialog = false
    //       postauth('supplier/purchase/', newPurchasePlan)
    //         .then(savePurchasePlan => {
    //           console.log('newPurchasePlan save,', savePurchasePlan)
    //           this.$q.notify({
    //             message: '采购方案保存成功',
    //             icon: 'check',
    //             color: 'green'
    //           })
    //           savePurchasePlan.supplier = formData.supplier
    //           resolve(savePurchasePlan)
    //         })
    //         .catch(err => {
    //           this.$q.notify({
    //             message: '供应商保存失败',
    //             icon: 'close',
    //             color: 'negative'
    //           })
    //         })
    //     }
    //     const purchaseFormItems = [
    //       {
    //         name: 'supplier',
    //         label: '选择或输入供应商名称,回车保存',
    //         type: 'select',
    //         field: 'supplier',
    //         options: supplierOptions,
    //         optionLabel: supplier => {
    //           return supplier.supplier_name
    //         }
    //       },
    //       {
    //         name: 'tag',
    //         label: '标签',
    //         field: 'tag',
    //         edit: true
    //       },
    //       {
    //         name: 'url',
    //         label: '采购链接',
    //         field: 'url',
    //         edit: true
    //       },
    //       {
    //         name: 'price',
    //         label: '价格',
    //         field: 'price',
    //         edit: true
    //       },
    //       {
    //         name: 'default',
    //         type: 'toggle',
    //         label: '设为默认',
    //         field: 'default'
    //       }
    //     ]
    //     var handlerNewSupplier = () => {
    //       _this
    //         .newSupplier()
    //         .then(supplier => {
    //           console.log(
    //             'new supplier success ,now let complete purchase plan '
    //           )
    //           newFormData.supplier = supplier
    //           purchaseFormItems[0] = {
    //             name: 'supplier',
    //             field: 'supplier',
    //             label: '供应商',
    //             edit: false,
    //             fieldMap: supplier => {
    //               return supplier.supplier_name
    //             }
    //           }
    //           _this.newFormData = newFormData
    //           console.log('purchaseFormItems ', purchaseFormItems, newFormData)
    //           _this.newFormItems = purchaseFormItems
    //           _this.onNewDataCancel = onNewPurchaseCancel
    //           _this.onNewDataSummit = onNewPurchaseSummit
    //           _this.newDataDialog = true
    //         })
    //         .catch(err => {
    //           console.log('handlerNewSupplier new supplier fail', err)
    //         })
    //     }
    //     purchaseFormItems[0].newValue = handlerNewSupplier
    //     _this.newFormItems = purchaseFormItems
    //     _this.onNewDataCancel = onNewPurchaseCancel
    //     _this.onNewDataSummit = onNewPurchaseSummit
    //     _this.newDataDialog = true
    //   })
    // },
    newSupplier () {
      console.log('item new value ')
      var _this = this
      _this.newFormData = {
        supplier_name: '',
        supplier_city: '',
        supplier_address: '',
        supplier_contact: '',
        supplier_manager: '',
        supplier_level: 1
      }
      _this.newFormItems = [
        {
          name: 'supplier_name',
          label: '供应商名称',
          field: 'supplier_name',
          edit: true
        },
        {
          name: 'supplier_city',
          label: '所在城市',
          field: 'supplier_city',
          edit: true
        },
        {
          name: 'supplier_address',
          label: '详细地址',
          field: 'supplier_address',
          edit: true
        },
        {
          name: 'supplier_contact',
          label: '联系方式',
          field: 'supplier_contact',
          edit: true
        },
        {
          name: 'supplier_manager',
          label: '负责人',
          field: 'supplier_manager',
          edit: true
        }
      ]
      _this.onNewDataCancel = () => {
        console.log('on new supplier  cancel ')
        _this.newDataDialog = false
      }
      return new Promise((resolve, reject) => {
        _this.onNewDataSummit = supplier => {
          console.log('on new supplier summit ', supplier)
          supplier.creater = _this.login_name
          supplier.openid = _this.openid
          postauth('supplier/', supplier)
            .then(res => {
              console.log('save new supplier success response ', res)
              _this.newDataDialog = false
              const supplierSave = res
              this.$q.notify({
                message: '供应商保存成功',
                icon: 'check',
                color: 'green'
              })
              resolve(supplierSave)
            })
            .catch(err => {
              console.log('save new supplier fail ', err)
              _this.newDataDialog = false
              this.$q.notify({
                message: '供应商保存失败',
                icon: 'close',
                color: 'negative'
              })
              reject('供应商保存失败')
            })
        }
        _this.newDataDialog = true
      })
    },
    onGoodsSelect (selectGoods) {
      if (selectGoods.length <= 0) {
        this.$q.notify({
          message: '你似乎还没选择任何项目',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      this.$emit('onGoodsSelect', selectGoods)
    },
    onCancel () {
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
      _this.getPurchasePlan()
    } else {
      _this.authin = '0'
    }
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
  components: {
    GoodsSearchTable,
    NewForm
  },
  props: {
    exclude: Array
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
