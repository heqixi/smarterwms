<template>
  <div>
    <transition>
      <CommonTable
        ref="asnListTable"
        :table_list="asnGroupList"
        :columns="columns"
        :loading="loading"
        :num-rows="numRows"
        :getNextPage="getListNext"
        :filterFn="filteredRows"
        :searchFn="getSearchList"
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
  GET_GOODS_WAITING
} from 'src/store/inbound/types'

import CommonTable from '../../components/Share/commontable.vue'

export default {
  name: 'Pageasnlist',
  data () {
    var _this = this
    return {
      phase: PHASE_TYPE.waiting,
      editting_asn_id: -1,
      numRows: 0,
      loading: false,
      nextPhase: false,
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
            width: '100px',
            maxWidth: '100px',
            textAlign: 'center',
            whiteSpace: 'pre-line',
            fontSize: '8px'
          }
        },
        {
          name: 'summary',
          label: '??????',
          field: 'self',
          type: 'text',
          align: 'center',
          fieldMap: asn => {
            const supplierName = asn.supplier ? asn.supplier.supplier_name : ''
            const cost = '??????:' + asn.total_cost.toFixed(1) || ''
            const totalQty = '??????:' + asn.total_qty || ''
            return supplierName + '\n' + totalQty + ' ' + cost
          },
          style: {
            width: '120px',
            maxWidth: '120px',
            textAlign: 'center',
            whiteSpace: 'pre-line',
            fontSize: '8px'
          }
        },
        {
          name: 'order_url',
          label: '??????',
          field: 'order',
          type: 'url',
          align: 'center',
          class: 'col-1',
          fieldMap: order => {
            return order && order.length > 0 ? order[0].url : undefined
          }
        },
        {
          name: 'order_status',
          label: '??????',
          field: 'order',
          type: 'text',
          align: 'center',
          class: 'col-1',
          fieldMap: order => {
            const status = order && order.length > 0 ? order[0].status : -1
            return status === 0
              ? '?????????'
              : status === 1
                ? '?????????'
                : status === 2
                  ? '?????????'
                  : '??????'
          }
        },
        {
          name: 'delivery_date',
          label: '????????????',
          field: 'order',
          type: 'text',
          align: 'center',
          class: 'col-1',
          fieldMap: order => {
            return order && order.length > 0 ? order[0].delivery_date : '??????'
          }
        },
        {
          name: 'purchase_url',
          label: '????????????',
          field: 'purchases',
          type: 'table',
          keepExpand: true,
          rowHeight: 50,
          subColumns: [
            {
              name: 'tag',
              label: '??????',
              field: 'tag',
              align: 'center',
              class: 'col-2 text-center'
            },
            {
              name: 'url',
              label: '??????',
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
              label: '??????',
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
                  label: '??????',
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
                  class: 'col-4 text-center',
                  fieldMap: goods => {
                    return goods.goods_code
                  }
                },
                {
                  name: 'stock_onhand',
                  label: '??????',
                  field: 'goods',
                  align: 'center',
                  type: 'number',
                  class: 'col-2 text-center',
                  fieldMap: goods => {
                    return goods.stocks.stock_onhand
                  }
                },
                {
                  name: 'stock_reserved',
                  label: '??????',
                  field: 'goods',
                  type: 'number',
                  class: 'col-2 text-center',
                  edit: false,
                  fieldMap: goods => {
                    return goods.stocks.stock_reserve
                  }
                },
                {
                  name: 'goods_qty',
                  label: '??????',
                  field: 'goods_qty',
                  type: 'number',
                  style: {
                    width: '80px',
                    fontSize: '6px'
                  },
                  class: 'col-2 text-center'
                }
              ]
            }
          ]
        },
        {
          name: 'note',
          class: 'col-1',
          label: '??????',
          field: 'note'
        },
        {
          name: 'creater',
          label: this.$t('creater'),
          class: 'col-1',
          field: 'creater',
          align: 'center'
        },
        {
          name: 'action',
          type: 'actions',
          class: 'col-1',
          label: this.$t('action'),
          align: 'right',
          actions: [
            {
              name: 'next',
              label: '?????????',
              tip: '?????????',
              click: asn => {
                console.log('to purchase, ', asn)
                _this.moveToSortList(asn.id)
              }
            },
            {
              name: 'delete',
              label: '??????',
              tip: '??????????????????',

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
      goodsWaitingList: GET_GOODS_WAITING
    }),
    asnGroupList () {
      this.goodsWaitingList.forEach(asn => {
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
      this.goodsWaitingList.forEach(asn => {
        console.log('asn ', asn, asn.purchases)
      })
      return this.goodsWaitingList
    }
  },
  methods: {
    ...mapMutations('inbound', {
      onNextPhase: MOVE_TO_NEXT_PHASE
    }),
    ...mapGetters('inbound', {
      asnByPhaseId: GET_GOODS_BY_ID
    }),
    ...mapActions('inbound', {
      asyncGetList: ACTION_ASYNC_GET_ANS_LIST,
      asyncUpdateList: ACTION_UPDATE_ASN_LIST,
      removeItem: ACTION_DELETE_ASN_OBJ
    }),
    moveToSortList (asn_id) {
      console.log('moveToSortList ', asn_id)
      let data = {
        currentPhase: this.phase,
        asn_id: asn_id
      }
      this.onNextPhase(data)
    },
    updateField (formData) {
      var _this = this
      const asnObj = _this.asnByPhaseId()(this.phase, formData.row_id)
      console.log('updateField asnObj ', asnObj)
      if (asnObj === undefined) {
        _this.$q.notify({
          message: '???????????????????????????????????????',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const detailObj = asnObj.details.find(item => {
        return item.id === formData.subrow_id
      })
      if (detailObj === undefined) {
        _this.$q.notify({
          message: '???????????????????????????????????????',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      let fieldName = formData.field_name
      let value = formData.value
      if (fieldName == ANS_DETAIL_MODEL.goods_qty) {
        // ?????? ????????? ???????????????
        let diff = value - detailObj[ANS_DETAIL_MODEL.goods_qty]
        let goods_qty_new = value
        let goods_cost_new =
          detailObj[ANS_DETAIL_MODEL.goods][ANS_DETAIL_GOODS_MODEL.purchase]
            .price * goods_qty_new

        let total_qty = asnObj.total_qty + diff
        // cost ??????
        let total_cost =
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
        let total_weight =
          asnObj.total_weight +
          detailObj[ANS_DETAIL_MODEL.goods][
            ANS_DETAIL_GOODS_MODEL.goods_weight
            ] *
          diff

        // ??????????????????????????????
        let objectToUpdate = {
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
        let response = this.asyncUpdateList(objectToUpdate)
        return objectToUpdate
      }
    },
    getListNext () {
      this.getAsnWaitingList(this.pathname_next)
    },
    getSearchList () {
      if (this.numRows > this.goodsWaitingList.length) {
        this.$q.notify({
          message: '?????????????????????????????????????????????????????????????????????',
          icon: 'check',
          color: 'green'
        })
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
    async getAsnWaitingList (path) {
      this.loading = true
      const response = await this.asyncGetList({status: 1, path: path})
      this.numRows = response.count
      this.pathname_next = response.next
      this.loading = false
    },
    reFresh () {
      this.getAsnWaitingList()
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
      if (_this.goodsWaitingList.length <= 0) {
        _this.getAsnWaitingList()
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
