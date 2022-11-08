<style>
.q-card-padding {
  padding: 5px;
}
</style>
<template>
  <q-dialog ref="dialog">
    <q-card class="q-dialog-plugin q-card-padding">
      <q-banner rounded dense class="bg-white">
        <template v-slot:avatar>
          <q-icon name="sync_alt"/>
          {{$t('sync')}}
        </template>
      </q-banner>
      <q-select dense color="dark" transition-show="flip-up" transition-hide="flip-down"
                v-model="cur_shop_id"
                :options="shop_options"
                :label="$t('store.label')"
                emit-value
                map-options>
        <template v-slot:prepend>
          <q-icon name="img:statics/store/store.svg"/>
        </template>
      </q-select>
      <q-tabs v-model="tab" dense class="text-grey"
        active-color="primary" indicator-color="primary" align="justify" narrow-indicator>
        <q-tab name="single" :label="$t('single')" />
        <q-tab name="all" :label="$t('all')" />
      </q-tabs>
      <q-separator />
      <q-tab-panels v-model="tab" animated class="q-pa-md">
        <q-tab-panel name="single" class="row">
          <q-input class="col-all" dense clearable clear-icon="close" color="dark"
                   v-model="order_sn" :label="$t('order.view_orderlist.order_sn')"/>
        </q-tab-panel>
        <q-tab-panel name="all" class="row">
          <q-input class="col-5" dense v-model="date.from" mask="date"
                   :rules="['date']" :label="$t('starttime')">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy ref="qDateProxy" transition-show="scale" transition-hide="scale">
                  <q-date v-model="date.from" :locale="locale[$i18n.locale]">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
          <span class="col-2 self-center text-center">-</span>
          <q-input class="col-5" dense v-model="date.to" mask="date"
                   :rules="['date']" :label="$t('endtime')">
            <template v-slot:append>
              <q-icon name="event" class="cursor-pointer">
                <q-popup-proxy ref="qDateProxy" transition-show="scale" transition-hide="scale">
                  <q-date v-model="date.to" :locale="locale[$i18n.locale]">
                    <div class="row items-center justify-end">
                      <q-btn v-close-popup label="Close" color="primary" flat />
                    </div>
                  </q-date>
                </q-popup-proxy>
              </q-icon>
            </template>
          </q-input>
        </q-tab-panel>
      </q-tab-panels>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide" />
        <q-btn color="primary" :label="$t('submit')" @click="sync"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { postauth } from 'boot/axios_request'
import moment from 'moment'
import storeService from 'pages/store/services/storeservice'
import orderService from 'pages/order/services/orderservice'

export default {
  name: 'SyncOrder',
  data () {
    return {
      date: {
        from: moment().format('YYYY/MM/DD'),
        to: moment().add(1, 'day').format('YYYY/MM/DD')
      },
      tab: 'single',
      order_sn: '',
      pathname: 'order/',
      locale: {
        'zh-hans': {
          days: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
          daysShort: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
          months: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
          monthsShort: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
          firstDayOfWeek: 1,
          format24h: true
        },
        'zh-hant': {
          days: ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'],
          daysShort: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
          months: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'],
          monthsShort: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
          firstDayOfWeek: 1,
          format24h: true
        }
      },
      cur_shop_id: null,
      shop_options: []
    }
  },
  props: {
    parent: Object
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    sync () {
      if (this.tab === 'single') {
        this.syncOrder()
      } else {
        this.syncAllOrder()
      }
    },
    syncOrder () {
      const _this = this
      orderService.syncOrder({
        shop_id: _this.cur_shop_id,
        order_sn: _this.order_sn
      }).then(() => {
        _this.parent.reFresh()
      }).finally(() => {
        _this.hide()
      })
    },
    syncAllOrder () {
      const _this = this
      const timeFrom = moment(_this.date.from).valueOf() / 1000
      const timeTo = moment(_this.date.to).valueOf() / 1000
      if (timeFrom >= timeTo) {
        _this.$q.notify({
          message: 'Time Error',
          icon: 'close',
          color: 'negative'
        })
        return
      }
      orderService.syncOrder({
        shop_id: _this.cur_shop_id,
        time_from: timeFrom,
        time_to: timeTo
      }).then(() => {
        _this.parent.reFresh()
      }).finally(() => {
        _this.hide()
      })
    }
  },
  created () {
    const _this = this
    storeService.getStoreList().then(stores => {
      const options = [];
      for (const i in stores) {
        const store = stores[i]
        store.label = store.name + '(' + store.area + ')'
        store.value = store.uid
        options.push(store)
      }
      _this.cur_shop_id = options[0].value
      _this.shop_options = options
    })
  }
}
</script>
