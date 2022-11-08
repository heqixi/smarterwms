<template>
  <div>
    <transition>
      <CommonTable
        ref="asnPresortTable"
        :table_list="asnGroupList"
        :columns="columns"
        :loading="loading"
        :filterFn="filteredRows"
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
import { LocalStorage, SessionStorage } from 'quasar'
import { mapActions, mapGetters, mapMutations } from 'vuex'

import {
  ACTION_ASYNC_GET_ANS_LIST,
  ACTION_DELETE_ASN_OBJ,
  ACTION_UPDATE_ASN_LIST,
  ANS_DETAIL_GOODS_MODEL,
  ANS_DETAIL_MODEL,
  GET_GOODS_BY_ID,
  GET_GOODS_IN_STOCK,
  MOVE_TO_NEXT_PHASE,
  PHASE_TYPE
} from 'src/store/inbound/types'

import CommonTable from '../../components/Share/commontable.vue'
import { postauth } from 'boot/axios_request'

export default {
  name: 'Pageasnlist',
  data () {
    var _this = this
    return {
      phase: PHASE_TYPE.stock,
      nextPhase: false,
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
            width: '120px',
            maxWidth: '120px',
            textAlign: 'center',
            whiteSpace: 'pre-line',
            fontSize: '8px'
          }
        },
        // {
        //   name: 'total_cost',
        //   label: '金额',
        //   field: 'total_cost',
        //   type: 'number',
        //   align: 'center',
        //   fieldMap: cost => { return cost.toFixed(1) }
        // },
        // {
        //   name: 'total_qty',
        //   label: '数量',
        //   field: 'total_qty',
        //   type: 'number',
        //   align: 'center'
        // },
        {
          name: 'order_url',
          label: '链接',
          field: 'order',
          type: 'url',
          align: 'center',
          fieldMap: order => {
            return order && order.length > 0 ? order[0].url : undefined
          },
          style: {
            width: '50px',
            maxWidth: '50px',
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
                  label: '实到',
                  field: 'goods_actual_qty',
                  type: 'number',
                  class: 'col-1 text-center'
                },
                {
                  name: 'goods_damage_qty',
                  label: '损坏',
                  field: 'goods_damage_qty',
                  type: 'number',
                  class: 'col-1 text-center'
                },
                {
                  name: 'goods_amend_qty',
                  label: '补发数量',
                  edit: true,
                  field: 'goods_amend_qty',
                  type: 'number',
                  class: 'col-2 text-center',
                  onUpdate: (asn, purchase, detail, qty) => {
                    console.log('on onUpdate goods_amend_qty ', asn, detail, qty)
                    _this.$set(detail, 'goods_amend_qty', qty)
                    return new Promise((resolve, reject) => {
                      resolve(qty)
                    })
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
              name: 'amend',
              label: '补发',
              tip: '补发产品',
              click: asn => {
                console.log('amend asn, ', asn)
                _this.amendAsn(asn)
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
      const shortage = this.goodsInStockList.filter(asn => {
        let shortage = false
        asn.details.forEach(detail => {
          if (detail.goods_qty > detail.goods_actual_qty) {
            shortage = true
          }
        })
        console.log('shortage asn ', asn)
        return shortage
      })
      shortage.forEach(asn => {
        asn.purchases = []
        const details = asn.details
        for (let i = 0; i < details.length; i++) {
          if (details[i].goods_qty <= details[i].goods_actual_qty) {
            continue
          }
          const purchase = asn.purchases.find(purchase => {
            return purchase.id === details[i].purchase.id
          })
          if (details[i].goods_amend_qty === undefined) {
            console.log('set goods amend qty ')
            this.$set(details[i], 'goods_amend_qty', details[i].goods_qty - details[i].goods_actual_qty)
          }
          if (!purchase) {
            const purchase = details[i].purchase
            purchase.details = [details[i]]
            asn.purchases.push(purchase)
          } else {
            purchase.details.push(details[i])
          }
        }
      })
      return shortage
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
    amendAsn (asn) {
      const details2Amend = []
      asn.details.forEach(detail => {
        if (detail.goods_amend_qty > 0) {
          const detail2Amend = {
            id: detail.id,
            goods_qty: detail.goods_amend_qty
          }
          details2Amend.push(detail2Amend)
        }
      })
      const form = {
        asn: asn.id,
        details: details2Amend
      }
      postauth('asn/amend/', form).then(res => {
        console.log('amend asn success')
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
        this.asyncUpdateList(objectToUpdate)
        return objectToUpdate
      }
    },
    async getAsnInStockList () {
      this.loading = true
      const response = await this.asyncGetList(3)
      this.loading = false
    },
    getSearchList () {
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
