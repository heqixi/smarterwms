<template>
  <div>
    <transition>
      <CommonTable
        ref="asnPresortTable"
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
  GET_GOODS_IN_STOCK
} from 'src/store/inbound/types'

import CommonTable from '../../components/Share/commontable.vue'

export default {
  name: 'Pageasnlist',
  data () {
    var _this = this
    return {
      phase: PHASE_TYPE.stock,
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
          field: 'asn_code'
        },
        {
          name: 'supplier',
          label: this.$t('baseinfo.view_supplier.supplier_name'),
          field: 'supplier',
          type: 'text',
          align: 'center',
          fieldMap: supplier => {
            return supplier.supplier_name
          }
        },

        {
          name: 'total_cost',
          label: '金额',
          field: 'total_cost',
          type: 'number',
          align: 'center',
          fieldMap: cost => { return cost.toFixed(1) }
        },
        {
          name: 'total_qty',
          label: '数量',
          field: 'total_qty',
          type: 'number',
          align: 'center'
        },
        {
          name: 'order_url',
          label: '链接',
          field: 'order',
          type: 'url',
          align: 'center',
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
                  class: 'col-4 text-center',
                  fieldMap: goods => {
                    return goods.goods_code
                  }
                },
                {
                  name: 'goods_qty',
                  label: '购买数量',
                  field: 'goods_qty',
                  type: 'number',
                  class: 'col-2 text-center'
                },
                {
                  name: 'goods_actual_qty',
                  label: '实到数量',
                  field: 'goods_actual_qty',
                  type: 'number',
                  class: 'col-2'
                },
                {
                  name: 'goods_damage_qty',
                  label: '损坏数量',
                  field: 'goods_damage_qty',
                  type: 'number',
                  class: 'col-2'
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
            maxWidth: '100px',
            width: '100px',
            textAlign: 'center',
            whiteSpace: 'normal',
            fontSize: '8px'
          },
          label: this.$t('action'),
          align: 'right',
          actions: [
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
      goodsInStockList: GET_GOODS_IN_STOCK
    }),
    asnGroupList () {
      const nonAmendList = this.goodsInStockList.filter(asn => { return !asn.amend })
      nonAmendList.forEach(asn => {
        asn.purchases = []
        const details = asn.details
        for (let i = 0; i < details.length; i++) {
          const purchase = asn.purchases.find(purchase => {
            return purchase.id === details[i].purchase.id
          })
          if (!purchase) {
            const purchase = details[i].purchase
            purchase.details = [details[i]]
            asn.purchases.push(purchase)
          } else {
            purchase.details.push(details[i])
          }
        }
      })
      return nonAmendList
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
    updateField (formData) {
      var _this = this
      const asnObj = _this.asnByPhaseId()(this.phase, formData.row_id)
      console.log('updateField asnObj ', asnObj)
      // let asnObj = _this.goodsToPurchaseList.find(item => {
      //   return item.id == formData.row_id;
      // });

      if (asnObj === undefined) {
        _this.$q.notify({
          message: '找不到记录，请重新刷新页面',
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
          message: '找不到记录，请重新刷新页面',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      const fieldName = formData.field_name
      const value = formData.value
      if (fieldName === ANS_DETAIL_MODEL.goods_qty) {
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
    getListNext () {
      this.getAsnInStockList(this.pathname_next)
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
      this.getAsnList(this.pathname_next)
    },
    async getAsnInStockList (path) {
      this.loading = true
      const response = await this.asyncGetList({ status: 3, path: path })
      this.numRows = response.count
      this.pathname_next = response.next
      this.loading = false
    },
    reFresh () {
      this.getAsnInStockList()
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
      if (_this.goodsInStockList.length <= 0) {
        _this.getAsnInStockList()
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
