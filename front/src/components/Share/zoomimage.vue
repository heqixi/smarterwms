<template>
  <q-dialog ref="dialog">
    <q-img :src="img_url">
      <template v-slot:loading>
        <div class="text-black">
          <q-spinner-ios/>
          <div class="q-mt-md">Loading...</div>
        </div>
      </template>
      <template v-slot:error>
        <q-icon name="error"></q-icon>
      </template>
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
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  }
}
</script>
