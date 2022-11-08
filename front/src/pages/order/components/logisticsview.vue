<template>
  <q-dialog ref="dialog" full-height>
    <q-card class="q-pa-md" style="width: 700px; max-width: 80vw;">
<!--      <iframe width="100%" height="100%" :src="`statics/plugins/pdfjs/web/viewer.html?file=${filePath}`"></iframe>-->
      <iframe width="100%" height="100%" :src="`${filePath}`"></iframe>
    </q-card>
  </q-dialog>
</template>
<script>
import orderService from 'pages/order/services/orderservice'

export default {
  name: 'LogisticsView',
  data () {
    return {
      filePath: ''
    }
  },
  props: {
    openid: {
      type: String,
      require: true
    },
    orderList: {
      type: Array,
      require: true
    }
  },
  methods: {
    show () {
      const _this = this
      _this.filePath = orderService.getLogisticsFileUrl(_this.orderList, _this.openid)
      // _this.filePath = encodeURIComponent(orderService.getLogisticsFileUrl(_this.shopId, _this.orderList))
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    // 禁用鼠标右击、F12 来禁止打印和打开调试工具
    prohibit () {
      // 屏蔽右键菜单
      document.oncontextmenu = (ev) => {
        return false
      }
      document.onkeydown = (e) => {
        if (e.ctrlKey && (e.keyCode === 65 || e.keyCode === 67 || e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 80 || e.keyCode === 83 || e.keyCode === 85 || e.keyCode === 86 || e.keyCode === 117)) {
          return false
        }
        if (e.keyCode === 18 || e.keyCode === 123) {
          return false
        }
      }
    }
  }
}
</script>
