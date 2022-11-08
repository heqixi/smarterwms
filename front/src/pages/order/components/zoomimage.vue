<template>
  <q-dialog ref="dialog">
    <q-img :src="img_url" @dblclick="copy" class="cursor-pointer">
      <template v-slot:loading>
        <div class="text-black">
          <q-spinner-ios/>
          <div class="q-mt-md">Loading...</div>
        </div>
      </template>
      <template v-slot:error>
        <q-icon name="error"></q-icon>
      </template>
      <q-tooltip>{{$t('dbclick')+$t('copy')}}</q-tooltip>
    </q-img>
  </q-dialog>
</template>
<script>
export default {
  name: 'ZoomImage',
  props: {
    img_url: {
      type: String,
      require: true
    }
  },
  methods: {
    copy (e) {
      const _this = this
      const img = new Image()
      img.src = _this.img_url
      e.target.appendChild(img)
      const selection = window.getSelection()
      if (selection.rangeCount > 0) {
        selection.removeAllRanges()
      }
      if (!document.queryCommandSupported('copy')) {
        throw new Error('Browser does not support copy')
      } else {
        const range = document.createRange()
        range.selectNode(img)
        selection.addRange(range)
        document.execCommand('copy')
        selection.removeAllRanges()
        img.remove()
        _this.$q.notify({
          message: `${_this.$t('copy')}${_this.$t('success')}`,
          icon: 'check',
          color: 'green'
        })
      }
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  }
}
</script>
