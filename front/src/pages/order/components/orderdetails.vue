<style>
.center-padding {
  padding-left: 1em;
}
.model-font-size {
  font-size: 1.2em;
}
.base-info-font-size {
  font-size: 1em;
}
.word-break {
  white-space:pre-line;
  word-wrap: break-word;
  word-break: normal;
}
</style>
<template>
    <q-card v-model="show" class="q-pa-none">
      <q-card-section class="row q-mx-xs q-pa-none" v-if="hasItem()">
        <div class="col-7">
          <q-card-section v-if="reissueList && reissueList.length > 0" class="row q-pa-none" style="border-bottom: 1px solid rgba(0,0,0,0.1)">
            <div class="col-all q-pa-none" :class="[(reissueList && reissueList.length > 0) ? 'card-border':'']">
              <div class="row" :key='reissue.id' v-for="reissue in reissueList">
                <q-img class="col-1 rounded-borders"
                       :src="reissue.image_url"
                       contain
                       :ratio="1"
                       style="max-height: 100px; max-width: 100px"
                       basic
                       spinner-color="white"
                       @click="zoomImage(reissue.image_url)"
                >
                  <template v-slot:error>
                    <q-icon name="error"></q-icon>
                  </template>
                  <div v-if="reissue.packages" class="no-padding absolute-top text-center text-italic text-body2 base-info-font-size">
                    {{$t('order.view_details.package')}}
                  </div>
                  <div class="no-padding absolute-bottom text-center text-italic text-body2 base-info-font-size">
                    {{$t('order.view_details.reissue')}}
                  </div>
                </q-img>
                <div class="col-9 center-padding overflow-hidden">
                  <strong>
                    <span class="model-font-size">{{$t('order.view_details.model_sku')}}:</span>
                    <span class="text-purple-8 cursor-pointer model-font-size" @click="copyText(reissue.global_sku)">
                      {{reissue.global_sku}} <span class="text-red">* {{reissue.quantity}}</span>
                      <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
                    </span>
                    <span v-if="reissue.stock" class="cursor-pointer" :class="!checkIsLockedStock(reissue) ? 'text-red-10' : 'text-black'" style="padding-left: .6em" @click="openStock(reissue.stock, reissue.packages)">
                      [
                      <template v-if="checkIsLockedStock(reissue)">
                        {{ $t('order.view_details.stock_status_options.12')}} * {{getLockedStock(reissue)}}
                      </template>
                      <template v-else>
                        {{$t('order.view_details.stock_status_options.11')}}
                      </template>
                      ]
                      <q-tooltip>{{$t('check')+$t('more')}}</q-tooltip>
                    </span>
                    <span v-else class="text-red-10" style="padding-left: .6em">
                      [
                      {{$t('order.view_details.stock_not_exists')}}
                      ]
                    </span>
                  </strong>
                </div>
                <div class="col-2">
                  <div class="float-right">
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs" push>
                        <template v-if="reissue.has_package">
                          <q-btn v-if="reissue.packages" dense :label="$t('order.view_orderavailable.cancel_package')" @click="cancelPackage(reissue.id, 2)"></q-btn>
                          <q-btn v-if="!reissue.packages" dense :label="$t('order.view_orderavailable.toggle_package')" @click="togglePackage(reissue.id, 2)"></q-btn>
                        </template>
                      </q-btn-group>
                    </div>
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs" push>
                        <q-btn dense :label="$t('order.view_orderavailable.freed_stock')" v-if="reissue.stock && checkIsLockedStock(reissue)" @click="freedStock(reissue.id, true)"></q-btn>
                        <q-btn dense :label="$t('order.view_orderavailable.stock_matching')" v-if="reissue.stock && !checkIsLockedStock(reissue)" @click="stockMatching(reissue.id, true)"></q-btn>
                        <q-btn dense :label="$t('order.view_details.remove')" @click="remove(reissue.id)"></q-btn>
                      </q-btn-group>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
          <q-card-section :key='item.id' v-for="item in itemList" class="row q-pa-none"
                          style="border-bottom: 1px solid rgba(0,0,0,0.1)">
            <div class="col-all q-pa-none" :class="[hasReplaceList(item) ? 'card-border':'']">
              <div :key="replace.id" class="row" v-for="replace in item.replace_list">
                <q-img class="col-1 rounded-borders"
                       :src="replace.image_url"
                       :ratio="1"
                       contain
                       style="max-height: 100px; max-width: 100px"
                       basic
                       spinner-color="white"
                       @click="zoomImage(replace.image_url)">
                  <template v-slot:error>
                    <q-icon name="error"></q-icon>
                  </template>
                  <div v-if="replace.packages" class="no-padding absolute-top text-center text-italic text-body2 base-info-font-size">
                    {{$t('order.view_details.package')}}
                  </div>
                  <div class="no-padding absolute-bottom text-center text-italic text-body2 base-info-font-size">
                    {{$t('order.view_details.replace')}}
                  </div>
                </q-img>
                <div class="col-9 center-padding overflow-hidden">
                  <strong>
                    <span class="model-font-size">{{$t('order.view_details.model_sku')}}:</span>
                    <span class="text-purple-8 cursor-pointer model-font-size" @click="copyText(replace.global_sku)">
                      {{replace.global_sku}} <span class="text-red">* {{replace.quantity}}</span>
                      <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
                    </span>
                    <span v-if="replace.stock" class="cursor-pointer" :class="!checkIsLockedStock(replace) ? 'text-red-10' : 'text-black'" style="padding-left: .6em" @click="openStock(replace.stock, replace.packages)">
                      [
                      <template v-if="checkIsLockedStock(replace)">
                        {{ $t('order.view_details.stock_status_options.12')}} * {{getLockedStock(replace)}}
                      </template>
                      <template v-else>
                        {{$t('order.view_details.stock_status_options.11')}}
                      </template>
                      ]
                      <q-tooltip>{{$t('check')+$t('more')}}</q-tooltip>
                    </span>
                    <span v-else class="text-red-10" style="padding-left: .6em">
                      [
                      {{$t('order.view_details.stock_not_exists')}}
                      ]
                    </span>
                  </strong>
                </div>
                <div class="col-2 q-px-sm">
                  <div class="float-right">
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs" push>
                        <template v-if="replace.has_package">
                          <q-btn v-if="replace.packages" dense :label="$t('order.view_orderavailable.cancel_package')" @click="cancelPackage(replace.id, 2)"></q-btn>
                          <q-btn v-if="!replace.packages" dense :label="$t('order.view_orderavailable.toggle_package')" @click="togglePackage(replace.id, 2)"></q-btn>
                        </template>
                      </q-btn-group>
                    </div>
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs" push>
                        <q-btn dense :label="$t('order.view_orderavailable.freed_stock')" v-if="replace.stock && checkIsLockedStock(replace)" @click="freedStock(replace.id, true)"></q-btn>
                        <q-btn dense :label="$t('order.view_orderavailable.stock_matching')" v-if="replace.stock && !checkIsLockedStock(replace)" @click="stockMatching(replace.id, true)"></q-btn>
                        <q-btn dense :label="$t('order.view_details.remove')" @click="remove(replace.id)"></q-btn>
                      </q-btn-group>
                    </div>
                  </div>
                </div>
              </div>
              <div class="row" v-if="getItemQuantity(item) > 0">
                <q-img :src="item.image_url"
                       :ratio="1"
                       contain
                       style="max-height: 100px; max-width: 100px"
                       basic
                       spinner-color="white"
                       class="col-1 rounded-borders"
                       @click="zoomImage(item.image_url)"
                >
                  <template v-slot:error>
                    <q-icon name="error"></q-icon>
                  </template>
                  <div v-if="item.packages" class="no-padding absolute-top text-center text-italic text-body2 base-info-font-size">
                    {{$t('order.view_details.package')}}
                  </div>
                </q-img>
                <div class="col-9 center-padding overflow-hidden">
                  <strong>
                    <span class="model-font-size">{{$t('order.view_details.model_sku')}}:</span>
                    <span class="text-purple-8 cursor-pointer model-font-size" @click="copyText(item.goods_code)">
                      {{item.goods_code ? item.goods_code : $t('nodata')}} <span class="text-red">* {{getItemQuantity(item)}}</span>
                      <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
                    </span>
                    <span v-if="item.stock" class="cursor-pointer" :class="!checkIsLockedStock(item) ? 'text-red-10' : 'text-black'" style="padding-left: .6em" @click="openStock(item.stock, item.packages)">
                      [
                      <template v-if="checkIsLockedStock(item)">
                        {{ $t('order.view_details.stock_status_options.12')}} * {{getLockedStock(item)}}
                      </template>
                      <template v-else>
                        {{$t('order.view_details.stock_status_options.11')}}
                      </template>
                      ]
                      <q-tooltip>{{$t('check')+$t('more')}}</q-tooltip>
                    </span>
                    <span v-else class="text-red-10" style="padding-left: .6em">
                      [
                      {{$t('order.view_details.stock_not_exists')}}
                      ]
                    </span>
                  </strong>
                  <div class="word-break">{{$t('order.view_details.item_sku')}}: {{item.item_sku}}</div>
                  <div class="word-break">{{$t('order.view_details.item_name')}}: {{item.item_name}}</div>
                </div>
                <div class="col-2 q-px-sm">
                  <div class="float-right">
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs">
                        <q-btn dense :label="$t('order.view_details.change_goods')" @click="changeGoods(item)"></q-btn>
                        <template v-if="item.has_package">
                          <q-btn v-if="item.packages" dense :label="$t('order.view_orderavailable.cancel_package')" @click="cancelPackage(item.id, 1)"></q-btn>
                          <q-btn v-if="!item.packages" dense :label="$t('order.view_orderavailable.toggle_package')" @click="togglePackage(item.id, 1)"></q-btn>
                        </template>
                      </q-btn-group>
                    </div>
                    <div class="full-width">
                      <q-btn-group class="float-right q-my-xs">
                        <q-btn dense :label="$t('order.view_orderavailable.freed_stock')" v-if="item.stock && checkIsLockedStock(item)" @click="freedStock(item.id, false)"></q-btn>
                        <q-btn dense :label="$t('order.view_orderavailable.stock_matching')" v-if="item.stock && !checkIsLockedStock(item)" @click="stockMatching(item.id, false)"></q-btn>
                        <q-btn dense :label="$t('order.view_details.replace')" @click="modify(2, item)"></q-btn>
                      </q-btn-group>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </q-card-section>
        </div>
        <div class="col-2 text-left base-info-font-size" style="display: table; border-left: 1px solid rgba(0,0,0, 0.1)">
          <div class="q-pa-md" style="display: table-cell; vertical-align: middle">
            <div class="q-pa-none">
              {{$t('order.view_orderlist.order_sn')}}:
              <span class="cursor-pointer" @click="copyText(order.order_sn)">
                {{order.order_sn}}
                <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
              </span>
            </div>
            <div class="q-pa-none">
              {{ $t('order.view_details.ship_by_date') }}:
              <span>{{formatDate(order.ship_by_date)}}</span>
            </div>
            <div class="q-pa-none">
              {{ $t('order.view_details.cancel_time') }}:
              <span class="cursor-pointer" @click="copyText(formatDate(order.ship_by_date, 3))">
                {{formatDate(order.ship_by_date, 3)}}
                <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
              </span>
            </div>
          </div>
        </div>
        <div class="col base-info-font-size" style="display: table; border-left: 1px solid rgba(0,0,0, 0.1)">
          <div class="absolute-top-right q-ma-md">
            <q-btn class="float-right q-mx-xs" dense :label="$t('order.view_details.reissue')" @click="modify(1)"></q-btn>
            <q-btn class="float-right q-mx-xs" dense :label="$t('order.view_details.remark')" @click="remark"></q-btn>
          </div>
          <div class="full-width q-pa-md" style="display: table-cell; vertical-align: middle;">
            <div class="q-pa-none q-my-sm row">
              <span class="col word-break q-px-xs">
                {{$t('order.view_details.item_quantity')}}:
                <span class="q-ml-sm text-red text-bold">{{getKindAmount()}}</span>
              </span>
              <q-separator vertical/>
              <span class="col word-break q-px-xs">
                {{$t('order.view_details.quantity')}}:
                <span class="q-ml-sm text-red text-bold">{{quantity}}</span>
              </span>
              <q-separator vertical/>
              <span class="col word-break q-px-xs">
                {{$t('order.view_details.total_amount')}}:
                <span class="q-ml-sm text-red text-bold">{{order.total_amount}}</span>
              </span>
            </div>
            <q-separator v-if="messages && messages.length > 0"/>
            <div class="q-pa-none q-mt-sm text-red" :key="`message-${msg.id}`" v-for="msg in messages">
              {{$t('order.view_details.message_type.' + msg.type)}}:
              <span class="word-break text-bold">
                {{msg.message}}
              </span>
              <q-separator/>
            </div>
          </div>
        </div>
      </q-card-section>
      <q-card-section v-if="!hasItem()" class="text-center">
        {{$t('nodata')}}
      </q-card-section>
    </q-card>
</template>
<script>
import orderService from 'pages/order/services/orderservice'
import moment from 'moment'
import ZoomImage from 'pages/order/components/zoomimage'
import OrderModify from 'pages/order/components/ordermodify'
import GoodsSearch from 'pages/order/components/goodssearch'
import OrderStock from 'pages/order/components/orderstock'
import Remark from 'pages/order/components/remark'

export default {
  name: 'OrderDetails',
  data () {
    return {
      pathname: 'order/details',
      itemList: null,
      reissueList: null,
      ship_by_date: null,
      cancel_time: null,
      quantity: 0,
      messages: []
    }
  },
  props: {
    order: Object,
    show: {
      type: Boolean,
      require: true
    },
    orderId: {
      // eslint-disable-next-line vue/require-prop-type-constructor
      type: Number | String,
      require: true
    }
  },
  watch: {
    show (n, o) {
      if (n) {
        this.getOrderDetails();
      } else {
        this.itemList = null;
      }
    }
  },
  methods: {
    checkIsLockedStock (data) {
      if (data.has_package && data.packages) {
        for (const i in data.packages) {
          if (data.packages[i].stock.stock_status !== 12) {
            return false
          }
        }
        return true
      } else {
        if (!data.stock) {
          return false
        }
        return data.stock.stock_status === 12
      }
    },
    getLockedStock (data) {
      if (data.has_package && data.packages) {
        let sumQty = 0
        for (const i in data.packages) {
          if (data.packages[i].stock.stock_status === 12) {
            sumQty += data.packages[i].stock.stock_qty
          }
        }
        return Math.trunc(sumQty / data.packages.length)
      } else {
        if (data.stock) {
          return data.stock.stock_qty
        }
        return 0
      }
    },
    togglePackage (uid, type) {
      const _this = this
      orderService.togglePackage(uid, type).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getOrderDetails()
      })
    },
    cancelPackage (uid, type) {
      const _this = this
      orderService.cancelPackage(uid, type).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getOrderDetails()
      })
    },
    checkDetailPackage (item) {},
    checkModifyPackage (modify) {},
    remark () {
      const _this = this
      let note = null
      _this.messages.forEach(message => {
        if (message.type === 2) {
          note = message.message
        }
      })
      _this.$q.dialog({
        component: Remark,
        note: note
      }).onOk(newNote => {
        orderService.orderRemark(_this.order.id, newNote).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          })
          _this.getOrderDetails()
        })
      })
    },
    stockMatching (id, isModify) {
      const _this = this
      orderService.modelStockMatching({ is_modify: isModify, id: id }).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getOrderDetails()
      })
    },
    freedStock (id, isModify) {
      const _this = this
      orderService.freedModelStock({ is_modify: isModify, id: id }).then(res => {
        _this.$q.notify({
          message: res,
          icon: 'check',
          color: 'green'
        })
        _this.getOrderDetails()
        _this.$emit('freedStock', _this.order.id)
      })
    },
    openStock (stock, packages) {
      const _this = this
      _this.$q.dialog({
        component: OrderStock,
        stock: stock,
        packages: packages
      })
    },
    copyText (value) {
      const _this = this
      _this.$copyText(value).then(e => {
        _this.$q.notify({
          message: `${_this.$t('copy')} ${e.text} ${_this.$t('success')}`,
          icon: 'check',
          color: 'green'
        });
      })
    },
    changeGoods (item) {
      const _this = this;
      _this.$q.dialog({
        component: GoodsSearch,
        preSearch: item.goods_code
      }).onOk(goodsList => {
        orderService.changeGoods(item.id, goodsList).then(res => {
          _this.$q.notify({
            message: res,
            icon: 'check',
            color: 'green'
          });
          _this.getOrderDetails()
        })
      })
    },
    getKindAmount () {
      const _this = this;
      const skuList = [];
      if (_this.reissueList) {
        _this.reissueList.forEach(reissue => {
          if (!skuList.includes(reissue.global_sku)) {
            skuList.push(reissue.global_sku)
          }
        })
      }
      if (_this.itemList) {
        _this.itemList.forEach(item => {
          if (_this.getItemQuantity(item) > 0 && !skuList.includes(item.model_sku)) {
            skuList.push(item.model_sku)
          }
          item.replace_list.forEach(replace => {
            if (!skuList.includes(replace.global_sku)) {
              skuList.push(item.model_sku)
            }
          })
        })
      }
      return skuList.length;
    },
    getItemQuantity (item) {
      let quantity = item.model_quantity_purchased;
      if (this.hasReplaceList(item)) {
        item.replace_list.forEach(replace => {
          quantity -= replace.quantity
        })
      }
      return quantity
    },
    hasReplaceList (item) {
      return item.replace_list && item.replace_list.length > 0
    },
    remove (modifyId) {
      const _this = this;
      orderService.deleteOrderModify(modifyId).then(res => {
        _this.getOrderDetails()
        _this.$forceUpdate()
      })
    },
    modify (modifyType, item) {
      const _this = this;
      _this.$q.dialog({
        component: OrderModify,
        parent: _this,
        modifyType: modifyType,
        item: item
      }).onOk(res => {
        console.log('res', res)
        res.orderId = _this.order.id;
        orderService.orderModify(res).then(res => {
          _this.getOrderDetails()
          _this.$forceUpdate()
        })
      })
    },
    zoomImage (imageUrl) {
      const _this = this;
      _this.$q.dialog({
        component: ZoomImage,
        parent: _this,
        img_url: imageUrl
      })
    },
    hasItem () {
      return (this.itemList && this.itemList.length > 0) || (this.reissueList && this.reissueList.length > 0);
    },
    getOrderDetails () {
      const _this = this;
      orderService.getOrderDetails(_this.orderId).then(res => {
        _this.itemList = res.order_detail_list;
        _this.reissueList = res.reissue_list;
        _this.messages = res.messages;
        _this.refreshTotalQuantity();
      })
    },
    refreshTotalQuantity () {
      const _this = this
      _this.quantity = 0;
      _this.itemList.forEach((item) => {
        _this.quantity += item.model_quantity_purchased;
      })
      _this.reissueList.forEach((reissue) => {
        _this.quantity += reissue.quantity
      })
    },
    formatDate (date, days) {
      if (days) {
        return moment(date).add(days, 'day').format('YYYY-MM-DD hh:mm:ss');
      } else {
        return moment(date).format('YYYY-MM-DD hh:mm:ss');
      }
    }
  }
}
</script>
