<template>
  <q-dialog ref="dialog">
    <NewForm
      :items="newFormItems"
      :newFormData="newFormData"
      @newDataSummit="onNewDataSummit"
      @newDataCancel="onNewDataCancel"
    />
  </q-dialog>
</template>

<script>
import NewForm from 'src/components/Share/newForm'

import * as XLSX from 'xlsx'

const MAX_FILE_SIZE = 1024 * 1024 * 10

export default {
  name: 'FilePicker',
  data () {
    var _this = this
    return {
      workbook: undefined,
      newFormData: {
        file: null,
        // eslint-disable-next-line no-undef
        url: baseurl + 'goodsmedia/upload/',
        sheetName: []
      },
      newFormItems: [
        {
          name: 'file',
          label: '请选择excel文件',
          field: 'file',
          type: 'file',
          maxFileSize: MAX_FILE_SIZE,
          edit: true,
          onUpload: files => {
          },
          onFileAdded: files => {
            if (files.length > 1) {
              throw new Error('Can only upload  one file ')
            }
            _this.onFileAdded(files[0])
          },
          onRejected: _this.onRejectedFile
        },
        {
          name: 'sheetName',
          label: '选择工作表',
          field: 'sheetName',
          type: 'select',
          options: [],
          edit: true
        }
      ]
    }
  },
  methods: {
    onFileAdded (file) {
      console.log('on file Added ', this.newFormData, file)
      var _this = this
      const fileName = file.name
      if (fileName.length <= 0) {
        return false
      } else if (!/\.(xls|xlsx)$/.test(fileName.toLowerCase())) {
        // excel判断是不是excel，不是则提示用户文件格式不正确
        this.$q.notify({
          position: 'center',
          type: 'negative',
          message: '上传格式不正确，请上传xls或者xlsx格式',
          timeout: 3000
        })
        return false
      } else {
        _this.importExcel2Json(file, (jsonData) => {
          console.log('read data success ', jsonData)
        })
      }
    },
    importExcel2Json (file, callback) {
      var _this = this
      const reader = new FileReader()
      reader.onload = function (e) {
        _this.workbook = XLSX.read(e.target.result, { type: 'binary' })
        console.log('importExcel2Json sheet name ', _this.workbook)
        _this.newFormItems[1].options = _this.workbook.SheetNames
        _this.newFormData.sheetName = _this.workbook.SheetNames[0]
      }
      reader.readAsBinaryString(file)
    },
    onRejectedFile (rejectedEntries) {
      let reason = '未知错误'
      rejectedEntries.forEach(entry => {
        if (entry.failedPropValidation === 'max-file-size') {
          reason = '文件大小超过 ' + MAX_FILE_SIZE / (1024 * 1024) + '兆'
        }
      })
      this.$q.notify({
        type: 'negative',
        message: `文件上传失败, ${reason}`
      })
    },
    onNewDataSummit () {
      const sheetName = this.newFormData.sheetName
      const data = XLSX.utils.sheet_to_json(this.workbook.Sheets[sheetName], { defval: '', header: 0})
      this.workbook = undefined
      this.$emit('ok', data)
      this.hide()
    },
    onNewDataCancel () {
      console.log('on data cancel')
      this.workbook = undefined
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
  components: {
    NewForm
  }
}
</script>

<style scoped>

</style>
