<template>
  <q-dialog ref="dialog" no-backdrop-dismiss>
    <q-card style="min-width: 300px">
      <q-card-section class="q-py-none">
        <q-banner class="q-pa-none">
          {{$t('order.view_details.remark')}}
          <q-separator/>
        </q-banner>
        <q-input
            :maxlength="maxLength"
            v-model="text"
            filled
            autogrow
            autofocus
            :label="`${$t('order.view_details.max_len')}${maxLength}`"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn :label="$t('cancel')" @click="hide"/>
        <q-btn color="primary" :label="$t('submit')" @click="submit"/>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
export default {
  name: 'Remark',
  data () {
    return {
      text: null,
      maxLength: 200
    }
  },
  props: {
    note: String
  },
  methods: {
    submit () {
      const _this = this
      _this.$emit('ok', _this.text)
      _this.hide()
    },
    hide () {
      this.$refs.dialog.hide()
    },
    show () {
      this.$refs.dialog.show()
    }
  },
  created () {
    this.text = this.note
  }
}
</script>

<style scoped>

</style>
