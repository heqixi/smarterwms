<template>
  <q-dialog  ref="dialog">
    <q-uploader
      style="width:1000px"
      :url="uploadPathName"
      method="post"
      label="Max number of files (8)"
      multiple
      batch
      :max-files="maxFiles ? maxFiles : 8"
      @rejected="onRejected"
      @uploaded="onFileUploaded"
      @added="onFileAdded"
      @removed="onFileRemoved"
      :headers="[{ name: 'token', value: token }]"
      :field-name="file => file.name"
      :factory="mediaFileUploadFactory">
      <template v-slot:list="scope">
        <div>
          <q-list class="row" separator>
            <q-item
              class="col-2 q-ml-sm q-mb-sm"
              v-for="file in scope.files"
              :key="file.__key"
              :style="{height: '120px', width:'120px'}">
              <q-item-section v-if="file.__img" thumbnail class="gt-xs">
                <img :src="file.__img.src" :style="{height: '120px', width:'120px'}"/>
              </q-item-section>

              <q-item-section top side>
                <div class="row">
                  <q-btn
                    class="gt-xs"
                    size="12px"
                    flat
                    dense
                    round
                    icon="delete"
                    @click="scope.removeFile(file)"/>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </div>
      </template>
    </q-uploader>
  </q-dialog>
</template>

<script>
import { LocalStorage } from 'quasar'

export default {
  name: 'UploadImageDialog',
  data () {
    return {
      token: LocalStorage.getItem('openid'),
      meida_form_fields: [],
      uploadPathName: baseurl + 'product/image/',
      baseUrl: baseurl
    }
  },
  methods: {
    mediaFileUploadFactory (files) {
      const formFieldsWithTags = []
      files.forEach(file => {
        formFieldsWithTags.push({
          name: file.name,
          value: 'V'
        })
      })
      return {
        formFields: formFieldsWithTags
      }
    },
    onRejected (rejectedEntries) {
      // Notify plugin needs to be installed
      // https://quasar.dev/quasar-plugins/notify#Installation
      this.$q.notify({
        type: 'negative',
        message: `${rejectedEntries.length} file(s) did not pass validation constraints`
      })
    },
    onFileUploaded (info) {
      const response = info.xhr.response
      const images = JSON.parse(response)
      this.$emit('ok', images)
      this.hide()
    },
    onFileAdded (files) {
      console.log('file added ', files)
      files.forEach(file => {
        if (file.type.indexOf('video') !== -1) {
          this.meida_form_fields.push({
            name: file.name,
            value: 'Video'
          })
        } else {
          this.meida_form_fields.push({
            name: file.name,
            value: 'DescImage'
          })
        }
      })
    },
    onFileRemoved (files) {
      console.log('onFile removed ', files)
      // let goods_media = this.baseInfo.goods_media
      // files.forEach(file => {
      //   goods_media.forEach((item, index) => {
      //     if (item.name === file.name) {
      //       if (item.id > 0) {
      //         console.log(
      //           'start delete file remote ',
      //           file.name,
      //           ', id ',
      //           item.id
      //         )
      //         this.deleteFileRemote(item.id)
      //       }
      //       goods_media.splice(index, 1)
      //     }
      //   })
      // })
    },
    show () {
      this.$refs.dialog.show()
    },
    hide () {
      this.$refs.dialog.hide()
    }
  },
  props: ['maxFiles']
}
</script>

<style scoped>

</style>
