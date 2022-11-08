<template>
  <div>
    <transition>
      <CommonTable
        ref="asnPresortTable"
        :table_list="asnGroupList"
        :columns="columns"
        :loading="loading"
        :num-rows="numRows"
        :filterFn="filteredRows"
        :getNextPage="getListNext"
        multiple-select="true"
        @getSearchList="getSearchList"
        @newForm="newForm = true"
        @fieldUpdate="updateField"
        @refresh="reFresh"
      />
    </transition>
  </div>
</template>
<router-view/>

<script>
import {
  getauth
} from 'boot/axios_request'
import { SessionStorage, LocalStorage } from 'quasar'
import { mapActions, mapGetters, mapMutations } from 'vuex'

import {
  MOVE_TO_NEXT_PHASE,
  ACTION_ASYNC_GET_ANS_LIST,
  GET_GOODS_BY_ID,
  PHASE_TYPE,
  ACTION_UPDATE_ASN_LIST,
  ACTION_DELETE_ASN_OBJ,
  ANS_DETAIL_MODEL,
  ANS_DETAIL_GOODS_MODEL,
  GET_GOODS_TO_SORT, UPDATE_ACTUAL_QTY
} from 'src/store/inbound/types'

import CommonTable from '../../components/Share/commontable.vue'

export default {
  name: 'Pageasnlist',
  data () {
    var _this = this
    return {
      phase: PHASE_TYPE.sort,
      nextPhase: false,
      numRows: 0,
      loading: false,
      orderUrl: '',
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
          name: 'supplier',
          label: this.$t('baseinfo.view_supplier.supplier_name'),
          field: 'supplier',
          type: 'text',
          align: 'center',
          fieldMap: supplier => {
            return supplier.supplier_name
          },
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          }
        },

        {
          name: 'total_cost',
          label: '金额',
          field: 'total_cost',
          type: 'number',
          style: {
            width: '50px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          fieldMap: cost => { return cost.toFixed(1) },
          align: 'center'
        },
        {
          name: 'total_qty',
          label: '数量',
          field: 'total_qty',
          type: 'number',
          style: {
            width: '60px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          align: 'center'
        },
        {
          name: 'order_url',
          label: '链接',
          field: 'order',
          type: 'url',
          align: 'center',
          style: {
            width: '60px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          fieldMap: order => {
            return order && order.length > 0 ? order[0].url : undefined
          }
        },
        {
          name: 'purchase_url',
          label: '采购链接',
          field: 'purchases',
          type: 'table',
          keepExpand: true,
          rowHeight: 50,
          subColumns: [
            {
              name: 'tag',
              label: '标签',
              field: 'tag',
              align: 'center',
              class: 'col-2 text-center'
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
              class: 'col-9',
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
                  class: 'col-3 text-center',
                  fieldMap: goods => {
                    return goods.goods_code
                  }
                },
                {
                  name: 'stock_onhand',
                  label: '现有',
                  field: 'goods',
                  align: 'center',
                  type: 'number',
                  class: 'col-1 text-center',
                  fieldMap: goods => {
                    return goods.stocks.stock_onhand
                  }
                },
                {
                  name: 'stock_reserved',
                  label: '预留',
                  field: 'goods',
                  type: 'number',
                  class: 'col-1 text-center',
                  edit: false,
                  fieldMap: goods => {
                    return goods.stocks.stock_reserve
                  }
                },
                {
                  name: 'goods_qty',
                  label: '购买',
                  field: 'goods_qty',
                  type: 'number',
                  class: 'col-1 text-center'
                },
                {
                  name: 'goods_actual_qty',
                  label: '实到数量',
                  field: 'goods_actual_qty',
                  type: 'number',
                  class: 'col-2',
                  edit: true,
                  onUpdate: (asn, purchase, detail, qty) => {
                    console.log('on goods_actual_qty update ', detail, qty)
                    return _this.updateActualQty(asn, detail, qty)
                  }
                },
                {
                  name: 'goods_damage_qty',
                  label: '损坏数量',
                  field: 'goods_damage_qty',
                  type: 'number',
                  class: 'col-2',
                  edit: true,
                  onUpdate: (asn, purchase, detail, qty) => {
                    console.log('on onUpdate goods_damage_qty ', asn, detail, qty)
                    return _this.updateDamageQty(asn, detail, qty)
                  }
                }
              ]
            }
          ]
        },
        {
          name: 'note',
          style: {
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          label: '备注',
          field: 'note'
        },
        {
          name: 'creater',
          label: this.$t('creater'),
          style: {
            width: '80px',
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
            maxWidth: '200px',
            width: '200px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          label: this.$t('action'),
          align: 'right',
          actions: [
            {
              name: 'next',
              label: '分拣',
              tip: '分拣这批货物',
              click: asn => {
                console.log('to stock, ', asn)
                _this.moveToStockList(asn.id)
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
      goodsToSortedList: GET_GOODS_TO_SORT
    }),
    asnGroupList () {
      this.goodsToSortedList.forEach(asn => {
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
      return this.goodsToSortedList
    }
  },
  methods: {
    ...mapMutations('inbound', {
      onNextPhase: MOVE_TO_NEXT_PHASE,
      updateReceivedQty: UPDATE_ACTUAL_QTY
    }),
    ...mapGetters('inbound', {
      asnByPhaseId: GET_GOODS_BY_ID
    }),
    ...mapActions('inbound', {
      asyncGetList: ACTION_ASYNC_GET_ANS_LIST,
      asyncUpdateList: ACTION_UPDATE_ASN_LIST,
      removeItem: ACTION_DELETE_ASN_OBJ
    }),
    moveToStockList (asn_id) {
      console.log('moveToStockList ', asn_id)
      const data = {
        currentPhase: this.phase,
        asn_id: asn_id
      }
      this.onNextPhase(data)
    },
    updateActualQty (asnObj, detailObj, qty) {
      if (qty < 0) {
        this.$q.notify({
          message: '无效值',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      this.updateReceivedQty({ asnId: asnObj.id, detailsId: detailObj.id, goods_actual_qty: qty })
      return new Promise((resolve, reject) => {
        resolve(qty)
      })
    },
    updateDamageQty (asnObj, detailObj, qty) {
      if (qty < 0) {
        this.$q.notify({
          message: '无效值',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      this.updateReceivedQty({ asnId: asnObj.id, detailsId: detailObj.id, goods_damage_qty: qty })
      return new Promise((resolve, reject) => {
        resolve(qty)
      })
    },
    updateField (formData) {
      var _this = this
      const asnObj = _this.asnByPhaseId()(this.phase, formData.row_id)
      console.log('updateField asnObj ', asnObj)
      if (asnObj === undefined) {
        _this.$q.notify({
          message: '找不到记录，请重新刷新页面',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const detailObj = asnObj.details.find(item => {
        return item.id == formData.subrow_id
      })
      if (detailObj == undefined) {
        _this.$q.notify({
          message: '找不到记录，请重新刷新页面',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const fieldName = formData.field_name
      const value = formData.value
      if (fieldName == ANS_DETAIL_MODEL.goods_qty) {
        // 更新 进货单 的统计信息
        const diff = value - detailObj[ANS_DETAIL_MODEL.goods_qty]
        const goods_qty_new = value
        const goods_cost_new =
          detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.purchase]
            .price * goods_qty_new

        const total_qty = asnObj.total_qty + diff
        // cost 更新
        const total_cost =
          asnObj.total_cost +
          detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.purchase]
            .price *
          diff

        console.log('asnobj ', asnObj, asnObj.total_weight)
        console.log(
          'detailObj, ',
          detailObj,
          ANS_DETAIL_MODEL.goods,
          ANS_DETAIL_GOODS_MODEL.goods_weight,
          detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.goods_weight]
        )
        const total_weight =
          asnObj.total_weight +
          detailObj[ANS_DETAIL_MODEL.goods][
            ANS_DETAIL_GOODS_MODEL.goods_weight
          ] *
          diff

        // 用于更新服务器端数据
        const objectToUpdate = {
          phase: this.phase,
          partial: true,
          id: asnObj.id,
          total_qty: total_qty,
          total_weight: total_weight,
          total_cost: total_cost,
          details: [
            {
              partial: true,
              id: detailObj.id,
              goods_qty: goods_qty_new,
              goods_actual_qty: goods_qty_new,
              goods_cost: goods_cost_new
            }
          ]
        }
        const response = this.asyncUpdateList(objectToUpdate)

        return objectToUpdate
      }
    },
    filteredRows (asn, searchTerm) {
      const codeMatch = asn.asn_code.indexOf(searchTerm) > -1
      const asnOrderUrl = asn.order && asn.order.length > 0 ? asn.order[0].url : ''
      const orderMatch = asnOrderUrl.length > 0 && searchTerm.indexOf(asnOrderUrl) > -1
      let goodsMatch = false
      asn.details.forEach(detail => {
        if (detail.goods.goods_code.indexOf(searchTerm) > -1) {
          goodsMatch = true
        }
      })
      return codeMatch || orderMatch || goodsMatch
    },
    getSearchList () {
    },
    getListNext () {
      this.getPreSortedList(this.pathname_next)
    },
    async getPreSortedList (path) {
      this.loading = true
      const response = await this.asyncGetList({ status: 2, path: path})
      this.numRows = response.count
      this.pathname_next = response.next
      this.loading = false
    },
    reFresh () {
      this.getPreSortedList()
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
      if (_this.goodsToSortedList.length <= 0) {
        _this.getPreSortedList()
      }
    } else {
      _this.authin = '0'
    }
    if (SessionStorage.has('goods_code')) {
    } else {
      SessionStorage.set('goods_code', [])
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
  destroyed () {
  },
  components: {
    CommonTable
  }
}
</script>
