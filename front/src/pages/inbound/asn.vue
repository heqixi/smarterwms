<template>
  <div>
    <transition>
      <CommonTable
        ref="asnListTable"
        :table_list="asnGroupList"
        :columns="columns"
        :topButtons="topButtons"
        :loading="loading"
        :num-rows="numRows"
        :getNextPage="getListNext"
        :filterFn="filteredRows"
        multipleSelect="true"
        row-key="id"
        @getSearchList="getSearchList"
        @fieldUpdate="updateField"
        @refresh="reFresh"
      />
    </transition>

    <q-dialog v-model="newForm" full-width>
      <GoodsSearchDialog
        :exclude="goodsToPurchase"
        @onGoodsSelect="onGoodsSelected"
        @onCancel="cancelDialog"
      />
    </q-dialog>
    <q-dialog v-model='asnOrderShow'>
      <NewForm
        :items="newFormItems"
        :newFormData="newFormData"
        @newDataSummit="onNewDataSummit"
        @newDataCancel="onNewDataCancel"
      />
    </q-dialog>
  </div>
</template>
<router-view/>

<script>
import { getauth, postauth, putauth } from 'boot/axios_request'
import { LocalStorage, SessionStorage } from 'quasar'
import GoodsSearchDialog from 'src/pages/inbound/components/goodsSearchDialog.vue'
import { mapActions, mapGetters, mapMutations } from 'vuex'

import {
  ACTION_ADD_ANS_ORDER,
  ACTION_ASYNC_GET_ANS_LIST,
  ACTION_DELETE_ASN_OBJ,
  ACTION_SAVE_PURCHASE_LIST,
  ACTION_UPDATE_ASN_LIST,
  ADD_GOODS_TO_PURCHASE,
  GET_GOODS_BY_ID,
  GET_GOODS_TO_PURCHASE,
  MOVE_TO_NEXT_PHASE,
  PHASE_TYPE,
  UPDATE_FIELD,
  UPDATE_PRUCHASE_QTY,
} from 'src/store/inbound/types'

import CommonTable from '../../components/Share/commontable.vue'
import NewForm from 'src/components/Share/newForm'
import PurchaseSelectedDialog from 'pages/inbound/components/purchaseSearchForGoods'

export default {
  name: 'Pageasnlist',
  data () {
    var _this = this
    return {
      loading: false,
      allPurchasePlan: [],
      phase: PHASE_TYPE.purchase,
      editting_asn_id: -1,
      numRows: 0,
      asnOrderShow: false,
      nextPhase: false,
      newFormItems: undefined,
      newFormData: undefined,
      onNewDataSummit: undefined,
      onNewDataCancel: undefined,
      orderUrl: '',
      asnOrder: {
        url: '',
        delivery_date: '',
        trans_name: '',
        trans_url: '',
        trans_phone: '',
        item_cost: '',
        trans_fee: '',
        discount: ''
      },
      openid: '',
      login_name: '',
      authin: '0',
      pathname: 'asn/',
      pathname_previous: '',
      pathname_next: '',
      height: '',
      table_list: [],
      supplier_list: [],
      filter: '',
      pagination: {
        page: 1,
        rowsPerPage: '30'
      },
      newForm: false,
      goodsData1: {
        code: '',
        qty: ''
      },

      devi: window.device,
      error1: this.$t('baseinfo.view_supplier.error1'),
      goodsListData: [],
      topButtons: [
        {
          name: 'new',
          label: '新增',
          tip: '新增库存记录',
          icon: 'add',
          click: () => {
            _this.newForm = true
          }
        }
      ],
      columns: [
        {
          name: 'asn_code',
          required: true,
          label: this.$t('inbound.view_asn.asn_code'),
          align: 'left',
          type: 'text',
          field: 'asn_code',
          style: {
            width: '120px',
            whiteSpace: 'normal',
            fontSize: '6px'
          }
        },
        {
          name: 'summary',
          label: '小计',
          field: 'self',
          type: 'text',
          align: 'center',
          fieldMap: asn => {
            const supplierName = asn.supplier ? asn.supplier.supplier_name : ''
            const cost = '金额:' + asn.total_cost.toFixed(1) || ''
            const totalQty = '数量:' + asn.total_qty || ''
            return supplierName + '\n' + totalQty + ' ' + cost
          },
          style: {
            width: '100px',
            maxWidth: '100px',
            textAlign: 'center',
            whiteSpace: 'pre-line',
            fontSize: '8px'
          }
        },
        {
          name: 'purchase_url',
          label: '采购链接',
          field: 'purchases',
          type: 'table',
          keepExpand: true,
          rowHeight: 50,
          edit: false,
          style: {
            width: '600px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          subColumns: [
            {
              name: 'tag',
              label: '标签',
              field: 'tag',
              align: 'center',
              style: {
                width: '80px',
                maxWidth: '80px',
                whiteSpace: 'normal',
                fontSize: '4px'
              },
              class: 'col-1 text-center'
            },
            {
              name: 'url',
              label: '链接',
              field: 'url',
              type: 'url',
              style: {
                width: '50px',
                maxWidth: '50px',
                fontSize: '6px'
              },
              class: 'col-1 text-center',
              edit: false
            },
            {
              name: 'details',
              label: '明细',
              field: 'details',
              type: 'table',
              style: {
                width: '400px',
                maxWidth: '400px',
                fontSize: '6px'
              },
              class: 'col-10',
              subColumns: [
                {
                  name: 'goods_image',
                  label: '图片',
                  field: 'goods',
                  type: 'image',
                  style: { width: '50px', maxWidth: '50px', padding: '0', margin: '0 auto' },
                  imageStyle: { width: '50px', maxWidth: '50px', height: '50px', minHeight: '50px' },
                  edit: false,
                  class: 'col-2 text-center',
                  fieldMap: goods => {
                    return goods.goods_image
                  }
                },
                {
                  name: 'goods_code',
                  label: 'sku',
                  field: 'goods',
                  align: 'center',
                  style: {
                    width: '100px',
                    maxWidth: '100px',
                    whiteSpace: 'normal',
                    fontSize: '6px'
                  },
                  class: 'col-2 text-center',
                  fieldMap: goods => {
                    return goods.goods_code
                  }
                },
                {
                  name: 'price',
                  label: '单价',
                  field: 'purchase',
                  type: 'number',
                  edit: false,
                  style: {
                    width: '80px',
                    maxWidth: '80px',
                    fontSize: '6px'
                  },
                  class: 'col-1 text-center',
                  fieldMap: purchase => {
                    return purchase.price
                  }
                },
                {
                  name: 'stock_onhand',
                  label: '现有',
                  field: 'goods',
                  align: 'center',
                  type: 'number',
                  class: 'col-1 text-center',
                  style: { width: '80px', maxWidth: '80px' },
                  fieldMap: goods => {
                    return goods.stocks.stock_onhand
                  }
                },
                {
                  name: 'stock_ship',
                  label: '已出',
                  field: 'goods',
                  type: 'number',
                  align: 'center',
                  style: {
                    maxWidth: '100px',
                    width: '100px'
                  },
                  class: 'col-1 text-center',
                  sortable: true,
                  fieldMap: goods => {
                    return goods.stocks.stock_ship
                  }
                },
                {
                  name: 'stock_reserved',
                  label: '短缺',
                  field: 'goods',
                  type: 'number',
                  style: {
                    width: '80px',
                    maxWidth: '80px',
                    fontSize: '6px'
                  },
                  class: 'col-1 text-center',
                  edit: false,
                  fieldMap: goods => {
                    return Math.max(goods.stocks.stock_reserve - goods.stocks.stock_onhand - goods.stocks.stock_purchased, 0)
                  }
                },
                {
                  name: 'goods_qty',
                  label: '购买数量',
                  field: 'goods_qty',
                  type: 'number',
                  style: {
                    width: '80px',
                    fontSize: '6px'
                  },
                  class: 'col-2 text-center',
                  edit: true,
                  onUpdate: (asn, purchase, detail, qty) => {
                    console.log('on goods_qty update ', detail, qty)
                    return _this.updatePurchaseNum(asn, detail, qty)
                  }
                },
                {
                  name: 'action',
                  label: this.$t('action'),
                  type: 'actions',
                  style: {
                    textAlign: 'center',
                    width: 'cal',

                    whiteSpace: 'normal'
                  },
                  class: 'col-2 text-center',
                  align: 'center',
                  actions: [
                    {
                      name: 'change',
                      label: '更换',
                      tip: '更换供应商',
                      click: (asn, purchase, asnDetail) => {
                        console.log('delete asn detail ', asn, asnDetail)
                        _this.changePurchase(asn, purchase, asnDetail)
                        // _this.selectPurchasePlan(asn, asnDetail)
                        // return _this.updatePurchaseNum(asn, asnDetail, 0)
                      }
                    },
                    {
                      name: 'delete',
                      label: '删除',
                      tip: '删除',
                      click: (asn, purchase, asnDetail) => {
                        console.log('delete asn detail ', asn, asnDetail)
                        _this.deleteAsnDetail(asn, purchase, asnDetail)
                        return new Promise((resolve, reject) => { resolve(0) })
                      }
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          name: 'creater',
          label: this.$t('creater'),
          style: {
            width: '50px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          field: 'creater',
          align: 'center'
        },
        {
          name: 'action',
          type: 'actions',
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          label: this.$t('action'),
          align: 'right',
          actions: [
            {
              name: 'next',
              label: '采购',
              tip: '去采购',
              click: asn => {
                console.log('to purchase, ', asn)
                _this.moveToWaitingList(asn.id)
              }
            },
            {
              name: 'delete',
              label: '删除',
              tip: '删除这条数据',

              click: asn => {
                console.log('delete asn, ', asn)
                _this.removeItem(asn.id)
              }
            }
          ]
        }
      ]
    }
  },
  computed: {
    ...mapGetters('inbound', {
      goodsToPurchaseList: GET_GOODS_TO_PURCHASE
    }),
    // loading () {
    //   return this.goodsToPurchaseList !== undefined
    // },
    asnGroupList () {
      this.goodsToPurchaseList.forEach(asn => {
        asn.purchases = []
        const details = asn.details
        for (let i = 0; i < details.length; i++) {
          const purchase = asn.purchases.find(purchase => { return purchase.id === details[i].purchase.id })
          if (!purchase) {
            const purchase = details[i].purchase
            purchase.details = [details[i]]
            asn.purchases.push(purchase)
          } else {
            purchase.details.push(details[i])
          }
        }
      })
      console.log('compute asnGroupList ', this.goodsToPurchaseList)
      return this.goodsToPurchaseList
    },
    goodsToPurchase () {
      const goodsToPurchases = []
      this.goodsToPurchaseList.forEach(asn => {
        asn.details.forEach(detail => {
          goodsToPurchases.push(detail.goods.id)
        })
      })
      return goodsToPurchases
    }
  },
  methods: {
    ...mapMutations('inbound', {
      addGoodsToPurchase: ADD_GOODS_TO_PURCHASE,
      onNextPhase: MOVE_TO_NEXT_PHASE,
      updateField: UPDATE_FIELD,
      updateQty: UPDATE_PRUCHASE_QTY
    }),
    ...mapGetters('inbound', {
      asnByPhaseId: GET_GOODS_BY_ID
    }),
    ...mapActions('inbound', {
      asyncGetList: ACTION_ASYNC_GET_ANS_LIST,
      savePurchaseList: ACTION_SAVE_PURCHASE_LIST,
      asyncUpdateList: ACTION_UPDATE_ASN_LIST,
      asyncAddOrderUrl: ACTION_ADD_ANS_ORDER,
      removeItem: ACTION_DELETE_ASN_OBJ
    }),
    async changePurchase (asn, purchase, asnDetail) {
      var _this = this
      const goods = asnDetail.goods
      if (!goods.purchases) {
        goods.purchases = await getauth(`supplier/purchase/?supplier=true&goods=${goods.id}`, {})
      }
      console.log('purchase of goods ', asn, purchase, asnDetail)
      const purchaseList = goods.purchases
      const dialog = _this.$q.dialog({
        component: PurchaseSelectedDialog,
        refName: 'purchaseSelectDialog',
        purchases: purchaseList,
        additionalTopButtons: [
          {
            name: 'add_to_other_purchase',
            label: '其他供应商',
            tip: '选择其他供应商',
            click: selectedPurchase => {
              console.log('select other purchase plan ')
              if (_this.allPurchasePlan.length <= 0) {
                _this.getPurchasePlan().then(allPurchases => {
                  console.log('append other purchase ', allPurchases)
                  allPurchases.forEach(p => {
                    if (!purchaseList.find(pExist => { return pExist.id === p.id })) {
                      purchaseList.push(p)
                    }
                  })
                })
              } else {
                _this.allPurchasePlan.forEach(p => {
                  if (!purchaseList.find(pExist => { return pExist.id === p.id })) {
                    purchaseList.push(p)
                  }
                })
              }
            }
          }
        ]
      }).onOk((purchaseSelected) => {
        console.log('on select purchase ', purchaseSelected)
        if (purchaseSelected.action === 'set_default') {
          postauth('supplier/purchase/set_default', {
            goods: goods.id,
            purchase: purchaseSelected.purchase.id
          })
          this.$q.notify({
            message: '设置成功',
            icon: 'check',
            color: 'green'
          })
          return
        }
        if (purchaseSelected.id === goods.purchase.id) {
          this.$q.notify({
            message: '采购链接相同',
            icon: 'check',
            color: 'green'
          })
          return
        }
        const goodsExist = purchaseSelected.goods.find(goodsId => {
          return goods.id === goodsId
        })
        if (!goodsExist) {
          _this.addGoodsToPurchasePlan(purchaseSelected, [goods.id]).then(res => {
            _this.realChangePurchase(goods, purchase, purchaseSelected, asn, asnDetail)
          })
        } else {
          _this.realChangePurchase(goods, purchase, purchaseSelected, asn, asnDetail)
        }
      })
    },
    realChangePurchase (goods, prePurchase, purchase, asn, asnDetail) {
      console.log('real change purchase ', prePurchase, purchase, asnDetail)
      var _this = this
      goods.purchase = purchase
      goods.purchase_num = asnDetail.goods_qty
      _this.addGoodsToPurchase([goods])
      _this.updatePurchaseNum(asn, asnDetail, 0)
      for (let k = 0; k < _this.asnGroupList.length; k++) {
        const asnAt = _this.asnGroupList[k]
        if (asnAt.id === asn.id) {
          for (let i = 0; i < asnAt.purchases.length; i++) {
            const purchaseAt = asnAt.purchases[i]
            if (purchaseAt.id === prePurchase.id) {
              for (let j = 0; j < purchaseAt.details.length; j++) {
                if (purchaseAt.details[j].id === asnDetail.id) {
                  purchaseAt.details.splice(j, 1)
                  break
                }
              }
              if (purchaseAt.details.length === 0) {
                asnAt.purchases.splice(i, 1)
              }
              break
            }
          }
          if (asnAt.purchases.length === 0) {
            _this.removeItem(asnAt.id)
          }
          break
        }
      }
    },
    selectPurchasePlan (asn, asnDetail) {
      var _this = this
      const selectPurchasePlanForm = {
        purchase: undefined
      }
      const selectPurchasePlanItems = [
        {
          name: 'purchase',
          label: '选择采购链接',
          type: 'select',
          field: 'purchase',
          options: _this.allPurchasePlan,
          optionLabel: purchase => {
            return purchase.supplier.supplier_name + '-' + purchase.tag + ' 价格 ' + purchase.price
          }
        }
      ]
      _this.newFormData = selectPurchasePlanForm
      _this.newFormItems = selectPurchasePlanItems
      _this.onNewDataSummit = formData => {
        console.log('on purchase plan select ', formData.purchase, asnDetail)
        const goods = asnDetail.goods
        const purchaseSelected = formData.purchase
        if (purchaseSelected.id === asnDetail.purchase.id) {
          this.$q.notify({
            message: '购买链接一样',
            icon: 'close',
            color: 'negative'
          })
          return
        }
        const goodsExist = purchaseSelected.goods.find(goodsId => {
          return goods.id === goodsId
        })
        goods.purchase = formData.purchase
        goods.purchase_num = asnDetail.goods_qty
        if (goodsExist) {
          console.info('goods already has this purchase plan ', goods, purchaseSelected)
          _this.addGoodsToPurchase([goods])
          _this.updatePurchaseNum(asn, asnDetail, 0)
        } else {
          _this.addGoodsToPurchasePlan(purchaseSelected, [goods.id]).then(res => {
            console.log('add goods to purchase plan succes ')
            purchaseSelected.goods.push(goods.id)
            goods.purchases.push(purchaseSelected)
            _this.addGoodsToPurchase([goods])
          })
          _this.updatePurchaseNum(asn, asnDetail, 0)
        }
        _this.asnOrderShow = false
      }
      _this.asnOrderShow = true
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
      return new Promise((resolve, reject) => {
        getauth('supplier/purchase/?supplier=details', {}).then(purchaseList => {
          console.log('get all purchase list ', purchaseList)
          _this.allPurchasePlan = purchaseList
          resolve(purchaseList)
        })
      })
    },
    deleteAsnDetail (asn, purchase, asndetail) {
      var _this = this
      _this.updatePurchaseNum(asn, asndetail, 0)
      for (let k = 0; k < _this.asnGroupList.length; k++) {
        const asnAt = _this.asnGroupList[k]
        if (asnAt.id === asn.id) {
          for (let i = 0; i < asnAt.purchases.length; i++) {
            const purchaseAt = asnAt.purchases[i]
            if (purchaseAt.id === purchase.id) {
              for (let j = 0; j < purchaseAt.details.length; j++) {
                if (purchaseAt.details[j].id === asndetail.id) {
                  purchaseAt.details.splice(j, 1)
                  break
                }
              }
              if (purchaseAt.details.length === 0) {
                asnAt.purchases.splice(i, 1)
              }
              break
            }
          }
          if (asnAt.purchases.length === 0) {
            _this.removeItem(asnAt.id)
          }
          break
        }
      }
    },
    updatePurchaseNum (asnObj, detailObj, newQty) {
      console.log('updateField asnObj ', asnObj)
      try {
        newQty = parseInt(newQty)
      } catch (err) {
        this.$q.notify({
          message: '请输入合法数量',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      this.updateQty({ asnId: asnObj.id, detailsId: detailObj.id, newQty: newQty })
      return new Promise((resolve, reject) => {
        resolve(newQty)
      })
    },
    moveToWaitingList (asnId) {
      console.log('updateOrderUrl ', asnId)
      const asnObj = this.goodsToPurchaseList.find(item => {
        return item.id === asnId
      })
      console.log('updateOrderUrl ansObj ', asnObj)
      console.log('updateOrderUrl ', asnObj)
      if (
        asnObj === undefined ||
        asnObj.order === undefined ||
        asnObj.order.url === undefined
      ) {
        // 需要填写进货单的采购链接
        this.editting_asn_id = asnId // 临时保存asn index
        this.asnOrderDetailPopup(asnObj)
      } else {
        this.onNextPhase(this.phase, asnId)
      }
    },
    asnOrderDetailPopup (asnObj) {
      var _this = this
      _this.asnOrder.url = ''
      _this.asnOrder.delivery_date = 3
      _this.asnOrder.item_cost = asnObj.total_cost
      _this.asnOrder.trans_fee = 5
      _this.asnOrder.discount = 0
      _this.newFormData = _this.asnOrder
      _this.newFormItems = [
        {
          name: 'url',
          label: '订单链接',
          field: 'url',
          edit: true
        },
        {
          name: 'delivery_date',
          label: '预计到货天数',
          field: 'delivery_date',
          edit: true
        },
        {
          name: 'item_cost',
          label: '货物金额',
          field: 'item_cost',
          edit: true
        },
        {
          name: 'trans_fee',
          label: '物流费用',
          field: 'trans_fee',
          edit: true
        },
        {
          name: 'discount',
          label: '优惠金额',
          field: 'discount',
          edit: true
        }
      ]
      _this.onNewDataSummit = formData => {
        console.log('order detail receive ', formData)
        formData.asn = asnObj.id
        _this.onAsnOrderSubmit(formData)
        _this.asnOrderShow = false
      }
      _this.onNewDataCancel = () => {
        console.log('on new supplier  cancel ')
        _this.asnOrderShow = false
      }
      _this.asnOrderShow = true
    },
    async onAsnOrderSubmit (formData) {
      console.log('onAsnOrderSubmit ', this.editting_asn_id, formData)
      this.nextPhase = false
      let deliveryDateStr = ''
      if (formData.delivery_date) {
        try {
          const days = parseInt(formData.delivery_date)
          const deliveryDate = new Date()
          deliveryDate.setDate(deliveryDate.getDate() + days)
          deliveryDateStr = deliveryDate.getFullYear() + '-' + deliveryDate.getMonth() + '-' + deliveryDate.getDate()
        } catch (error) {
          console.warn('fail to parse deliveryDate ')
        }
      }
      const data = {
        creater: LocalStorage.getItem('login_name'),
        asn: formData.asn,
        url: formData.url,
        status: 0, // 未发货
        item_cost: formData.item_cost,
        trans_fee: formData.trans_fee,
        discount: formData.discount,
        delivery_date: deliveryDateStr
        // delivery_date: '2022-06-28',
      }
      console.log('onAsnOrderSubmit post', data)
      await this.asyncAddOrderUrl(data)
      this.onNextPhase({
        currentPhase: this.phase,
        asn_id: formData.asn
      })
    },
    getList () {
      var _this = this
      if (LocalStorage.has('auth')) {
        getauth(
          _this.pathname + 'list/?details=1&purchases=1&goods=1&stock=1',
          {}
        )
          .then(res => {
            _this.table_list = []
            res.results.forEach(item => {
              if (item.asn_status === 1) {
                item.asn_status = _this.$t('inbound.predeliverystock')
              } else if (item.asn_status === 2) {
                item.asn_status = _this.$t('inbound.preloadstock')
              } else if (item.asn_status === 3) {
                item.asn_status = _this.$t('inbound.presortstock')
              } else if (item.asn_status === 4) {
                item.asn_status = _this.$t('inbound.sortstock')
              } else if (item.asn_status === 5) {
                item.asn_status = _this.$t('inbound.asndone')
              } else {
                item.asn_status = 'N/A'
              }
              _this.table_list.push(item)
            })
            _this.supplier_list = res.supplier_list
            _this.pathname_previous = res.previous
            _this.pathname_next = res.next
            _this.goodsListData = res.results
            console.log(this.goodsListData, 777)
          })
          .catch(err => {
            _this.$q.notify({
              message: err.detail,
              icon: 'close',
              color: 'negative'
            })
          })
      } else {
      }
    },
    getSearchList () {
    },
    getListNext () {
      this.getAsnList(this.pathname_next)
    },
    filteredRows (asn, searchTerm) {
      const codeMatch = asn.asn_code.indexOf(searchTerm) > -1
      let goodsMatch = false
      asn.details.forEach(detail => {
        if (detail.goods.goods_code.indexOf(searchTerm) > -1) {
          goodsMatch = true
        }
      })
      return codeMatch || goodsMatch
    },
    reFresh () {
      this.getAsnList()
    },
    onGoodsSelected (goods) {
      console.log('onGoodsSelected ', goods)
      this.newForm = false
      this.addGoodsToPurchase(goods)
      this.savePurchaseList()
    },
    cancelDialog () {
      this.newForm = false
    },
    async getAsnList (path) {
      this.loading = true
      const response = await this.asyncGetList({ status: 0, path: path })
      this.numRows = response.count
      this.pathname_next = response.next
      this.loading = false
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
      _this.table_list = []
      console.log('on create get list')
      if (!this.goodsToPurchaseList || this.goodsToPurchaseList.length <= 0) {
        _this.getAsnList()
      }
      // _this.getPurchasePlan()
      // _this.getList();
    } else {
      _this.authin = '0'
    }
    if (SessionStorage.has('goods_code')) {
    } else {
      SessionStorage.set('goods_code', [])
    }
  },
  updated () {
  },
  destroyed () {
  },
  components: {
    GoodsSearchDialog,
    CommonTable,
    NewForm
  }
}
</script>
