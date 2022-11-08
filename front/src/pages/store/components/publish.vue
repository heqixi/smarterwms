<template>
  <q-dialog ref="dialog">
    <q-card class="q-dialog-plugin">
      <q-btn-group push>
        <q-btn label='发布所有产品' @click="publishProduct()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
        </q-btn>
        <q-btn label='获取发布结果' @click="getPublishResult()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
        </q-btn>
        <q-btn label='更新库存' @click="updateStock()">
          <q-tooltip content-class="bg-amber text-black shadow-4" :offset="[10, 10]" content-style="font-size: 12px">{{ $t('refreshtip') }}</q-tooltip>
        </q-btn>
        <q-input dense clearable clear-icon="close" color="dark"
                 v-model="pid"
                 label="publish_task_id"/>
      </q-btn-group>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { getauth, postauth } from 'boot/axios_request'

export default {
  name: 'publish',
  data () {
    return {
      pid: '',
      pathname: 'store/product/'
    }
  },
  props: {
    shop_id: null
  },
  methods: {
    show () {
      this.$refs.dialog.show()
    },

    // following method is REQUIRED
    // (don't change its name --> "hide")
    hide () {
      this.$refs.dialog.hide()
    },
    updateStock () {
      const _this = this;
      postauth(_this.pathname + 'update_stock', { shop_id: _this.shop_id })
        .then(res => {
          console.log('publish result: ', res)
        })
    },
    getPublishResult () {
      const _this = this;
      getauth(_this.pathname + 'publish/result?publish_task_id=' + _this.pid)
        .then(res => {
          console.log('publish result: ', res)
        })
    },
    publishProduct () {
      const _this = this
      postauth(_this.pathname + 'publish', { shop_id: _this.search_form.cur_shop_id })
        .then(res => {
          console.log('publish: ', res)
        })
    }
  }
}
</script>
