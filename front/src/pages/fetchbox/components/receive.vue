<template>
  <q-dialog ref="receiveDialog" no-backdrop-dismiss>
    <q-card class="q-px-md">
      <q-card-section class="q-pa-none">
        <q-banner class="q-pa-none" dense>
          {{title}}
        </q-banner>
        <q-separator/>
        <div class="q-my-md">
          {{message}}
        </div>
      </q-card-section>
      <q-card-actions align="right" class="q-pa-none q-pb-md">
        <q-btn :label="$t('cancel')" @click="hide"/>
        <q-btn color="primary" :key="label" v-for="(label, index) in btn" :label="label" @click="submit(index)"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
export default {
  name: 'Receive',
  props: {
    title: String,
    message: String,
    btn: Array
  },
  data () {
    return {}
  },
  methods: {
    submit (index) {
      this.$emit('ok', index)
      this.hide()
    },
    show () {
      this.$refs.receiveDialog.show()
    },
    hide () {
      this.$refs.receiveDialog.hide()
    }
  }
}
</script>
