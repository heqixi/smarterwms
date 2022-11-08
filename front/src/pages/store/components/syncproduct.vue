<style>
.q-card-padding {
  padding: 5px;
}
</style>
<template>
  <q-dialog ref="dialog">
    <q-card class="q-dialog-plugin q-card-padding">
      <q-input dense clearable clear-icon="close" color="dark"
               v-model="item_id" label="Item ID"/>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide" />
        <q-btn color="primary" :label="$t('submit')" @click="syncProduct" />
        <q-btn color="primary" :label="$t('syncall')" @click="syncAllProduct" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>

export default {
  name: 'SyncProduct',
  data () {
    return {
      item_id: ''
    }
  },
  props: {},
  methods: {
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    syncProduct () {
      const _this = this
      _this.$emit('ok', {
        uid: _this.uid, item_id: _this.item_id
      })
      _this.hide()
    },
    syncAllProduct () {
      const _this = this
      _this.$emit('ok', {})
      _this.hide()
    }
  }
}
</script>
