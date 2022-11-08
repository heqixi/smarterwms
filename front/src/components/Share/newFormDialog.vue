<template>
  <q-dialog ref="dialog">
    <div @focusin="stopPropagation">
      <NewForm
        :items="newFormItems"
        :newFormData="newFormData"
        :title="title"
        @newDataSummit="onConfirm"
        @newDataCancel="onCancel"
      />
    </div>
  </q-dialog>
</template>

<script>
import NewForm from 'src/components/Share/newForm'

export default {
  name: 'NewFormDiloag',
  methods: {
    stopPropagation (evt) {
      evt.stopPropagation()
    },
    onConfirm () {
      this.$emit('ok')
      this.hide()
    },
    onCancel () {
      this.hide()
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  },
  emits: [
    // REQUIRED
    'ok'
  ],
  props: [
    'newFormItems', 'newFormData', 'title'
  ],
  components: {
    NewForm
  }
}
</script>

<style scoped>

</style>
